import pytest
from aws_cdk import core as cdk
from aws_cdk.assertions import Template

from titiler_service.titiler_service_stack import TitilerServiceStack

def test_synthesizes_properly():
    app = cdk.App()

    # Create the ProcessorStack.
    titiler_stack = TitilerServiceStack(app, "TitilerServiceStack")

    # Prepare the stack for assertions.
    template = Template.from_stack(titiler_stack)
