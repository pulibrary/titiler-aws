import os
from aws_cdk import core as cdk
from aws_cdk import (
        core,
        aws_iam as iam,
        aws_s3 as s3,
        aws_apigatewayv2,
        aws_apigatewayv2_integrations,
        aws_lambda
        )


class TitilerServiceStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
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
            f"titiler-service-lambda",
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
                "arn:aws:s3:::pul-tile-images/*",
                "arn:aws:s3:::*/*"
            ],
        )
        lambda_function.add_to_role_policy(permission)

        # API Gateway
        api = aws_apigatewayv2.HttpApi(
            self,
            f"titiler-service-endpoint",
            default_integration=aws_apigatewayv2_integrations.LambdaProxyIntegration(
                handler=lambda_function
            ),
        )
        core.CfnOutput(self, "Endpoint", value=api.url)
