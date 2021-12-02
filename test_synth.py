import pytest
from aws_cdk import core as cdk
from aws_cdk.assertions import Template

from titiler_service.titiler_service_stack import TitilerServiceStack

def test_synthesizes_properly():
    app = cdk.App()

    # Create the stack
    titiler_stack = TitilerServiceStack(app, "titiler-production", stage="production")

    # Synthesize the stack and build template
    template = Template.from_stack(titiler_stack)
