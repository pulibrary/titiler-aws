import os
from aws_cdk import (
        core,
        aws_iam as iam,
        aws_s3 as s3,
        aws_apigatewayv2,
        aws_apigatewayv2_integrations,
        aws_lambda,
        aws_cloudfront,
        aws_cloudfront_origins,
        aws_certificatemanager,
        aws_events,
        aws_events_targets
        )


class TitilerServiceStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment Variables
        env = {
            "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.TIF,.tiff",
            "GDAL_CACHEMAX": "800",  # 800 mb
            "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
            "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
            "GDAL_HTTP_MULTIPLEX": "YES",
            "GDAL_HTTP_VERSION": "2",
            "PYTHONWARNINGS": "ignore",
            "VSI_CACHE": "TRUE",
            "VSI_CACHE_SIZE": "5000000",  # 5 MB (per file-handle)
            "RIO_TILER_MAX_THREADS": "1" # turn off rio-tiler threading, better for lamda
        }

        # Lambda Function Definition
        lambda_function = aws_lambda.Function(
            self,
            f"titiler-{stage}-TitilerFuntion",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.from_asset(
                path=os.path.abspath("./"),
                bundling=core.BundlingOptions(
                    image=core.BundlingDockerImage.from_asset(
                        os.path.abspath("./"), file="resources/Dockerfile",
                    ),
                    command=["bash", "-c", "cp -R /var/task/. /asset-output/."],
                ),
            ),
            handler="handler.handler",
            memory_size=3008,
            timeout=core.Duration.seconds(600),
            environment=env,
        )

        # Rewrite Lambda Definition
        # There is one rewrite handle per stage because env vars
        # can't be passed to edge lambdas and we need to set the
        # S3 bucket accoring to stage.
        rewrite_function = aws_lambda.Function(
            self,
            f"titiler-{stage}-RewriteEdgeFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler=f"rewrite_handler_{stage}.handler",
            code=aws_lambda.Code.from_asset("./resources")
        )

        rewrite_edge_lambda = aws_cloudfront.EdgeLambda(
            event_type=aws_cloudfront.LambdaEdgeEventType.VIEWER_REQUEST,
            function_version=rewrite_function.current_version,
            include_body=False
        )

        # S3 Permissions
        permission = iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[
                f"arn:aws:s3:::figgy-geo-{stage}/*",
                "arn:aws:s3:::*/*"
            ],
        )
        lambda_function.add_to_role_policy(permission)

        # Add function url to primary lambda
        # Use instead of API gateway to bypass 30 second gateway timeout limit
        lambda_url = lambda_function.add_function_url(
            auth_type=aws_lambda.FunctionUrlAuthType.NONE
        )
        function_url = core.Fn.select(2, core.Fn.split('/', lambda_url.url))

        # Certificate
        if stage == "staging":
            custom_domain = "map-tiles-staging.princeton.edu"
        else:
            custom_domain = "map-tiles.princeton.edu"

        certificate = aws_certificatemanager.Certificate(self, f"titiler-{stage}-Certificate",
            domain_name=custom_domain,
            validation=aws_certificatemanager.CertificateValidation.from_dns()
        )

        # Cloudfront
        cache_policy = aws_cloudfront.CachePolicy(self, f"titiler-{stage}-CachePolicy",
            cache_policy_name=f"titiler-{stage}-CachePolicy",
            comment="Cache policy for TiTiler",
            default_ttl=core.Duration.days(365),
            max_ttl=core.Duration.days(365),
            min_ttl=core.Duration.days(365),
            query_string_behavior=aws_cloudfront.CacheQueryStringBehavior.all(),
            enable_accept_encoding_gzip=True,
            enable_accept_encoding_brotli=True
        )
        response_headers_policy = aws_cloudfront.ResponseHeadersPolicy(self, f"titiler-{stage}-ResponseHeadersPolicy",
            response_headers_policy_name=f"titiler-{stage}-ResponseHeadersPolicy",
            comment="Custom response policy with cache-control max-age set to match TTL",
            cors_behavior=aws_cloudfront.ResponseHeadersCorsBehavior(
                access_control_allow_credentials=False,
                access_control_allow_headers=["*"],
                access_control_allow_methods=["ALL"],
                access_control_allow_origins=["*"],
                access_control_expose_headers=["*"],
                origin_override=True
            ),
            custom_headers_behavior=aws_cloudfront.ResponseCustomHeadersBehavior(
                custom_headers=[aws_cloudfront.ResponseCustomHeader(header="Cache-Control", value="public, max-age= 31536000", override=True)]
            )
        )
        distribution = aws_cloudfront.Distribution(self, f"titiler-{stage}-DistPolicy",
            certificate=certificate,
            domain_names=[custom_domain],
            default_behavior=aws_cloudfront.BehaviorOptions(
                origin=aws_cloudfront_origins.HttpOrigin(function_url),
                cache_policy=cache_policy,
                allowed_methods=aws_cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                response_headers_policy=response_headers_policy,
                viewer_protocol_policy=aws_cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                origin_request_policy=aws_cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN,
                edge_lambdas=[rewrite_edge_lambda]
            )
        )

        # Add base url env var so TiTiler generates correct tile URLs.
        # Used in HostMiddleware.
        lambda_function.add_environment("TITILER_BASE_URL", custom_domain)

        core.CfnOutput(self, "Function URL", value=function_url)
        core.CfnOutput(self, "Cloudfront Endpoint", value=distribution.domain_name)

        # Lambda warmer
        eventRule = aws_events.Rule(
          self,
          f"titiler-{stage}-warmer",
          schedule=aws_events.Schedule.cron(minute="0/15")
        )
        eventRule.add_target(aws_events_targets.LambdaFunction(lambda_function))
