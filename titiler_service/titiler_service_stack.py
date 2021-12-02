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
            "MAX_THREADS": "0" # turn off rio-tiler threading, better for lamda
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

        # S3 Permissions
        permission = iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[
                f"arn:aws:s3:::figgy-geo-{stage}/*",
                "arn:aws:s3:::*/*"
            ],
        )
        lambda_function.add_to_role_policy(permission)

        # API Gateway
        api = aws_apigatewayv2.HttpApi(
            self,
            f"titiler-{stage}-endpoint",
            default_integration=aws_apigatewayv2_integrations.LambdaProxyIntegration(
                handler=lambda_function
            ),
        )

        api_domain = f'{api.http_api_id}.execute-api.{core.Stack.of(self).region}.amazonaws.com'

        # Cloudfront
        cache_policy = aws_cloudfront.CachePolicy(self, f"titiler-{stage}-CachePolicy",
            cache_policy_name=f"titiler-{stage}-CachePolicy",
            comment="Cache policy for TiTiler",
            default_ttl=core.Duration.days(365),
            min_ttl=core.Duration.days(365),
            max_ttl=core.Duration.days(365),
            query_string_behavior=aws_cloudfront.CacheQueryStringBehavior.all(),
            enable_accept_encoding_gzip=True,
            enable_accept_encoding_brotli=True
        )
        distribution = aws_cloudfront.Distribution(self, f"titiler-{stage}-DistPolicy",
            default_behavior=aws_cloudfront.BehaviorOptions(
                origin=aws_cloudfront_origins.HttpOrigin(api_domain),
                cache_policy=cache_policy,
                allowed_methods=aws_cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                viewer_protocol_policy=aws_cloudfront.ViewerProtocolPolicy.HTTPS_ONLY
            )
        )

        # Add base url env var so TiTiler generates correct tile URLs.
        # Used in HostMiddleware.
        lambda_function.add_environment("TITILER_BASE_URL", distribution.domain_name)

        core.CfnOutput(self, "API Endpoint", value=api.url)
        core.CfnOutput(self, "Cloudfront Endpoint", value=distribution.domain_name)
