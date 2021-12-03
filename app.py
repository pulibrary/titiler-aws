#!/usr/bin/env python3
import os

from aws_cdk import core
from titiler_service.titiler_service_stack import TitilerServiceStack

app = core.App()

TitilerServiceStack(
    app,
    "titiler-staging",
    stage="staging",
    env=core.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))
)

TitilerServiceStack(
    app,
    "titiler-production",
    stage="production",
    env=core.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))
)

app.synth()
