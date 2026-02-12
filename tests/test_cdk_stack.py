import aws_cdk as cdk
from aws_cdk.assertions import Template
from infra.stacks.baseline_stack import BaselineStack


def test_baseline_stack_contains_core_resources() -> None:
    app = cdk.App()
    stack = BaselineStack(app, "TestStack")
    template = Template.from_stack(stack)

    template.resource_count_is("AWS::Lambda::Function", 3)
    template.resource_count_is("AWS::SQS::Queue", 1)

    template.has_resource_properties(
        "AWS::Lambda::Function",
        {"Handler": "services.ingress.handler.lambda_handler"},
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {"Handler": "services.consumer.handler.lambda_handler"},
    )
