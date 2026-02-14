import aws_cdk as cdk
from aws_cdk.assertions import Match, Template

from infra.stacks.baseline_stack import BaselineStack


def test_baseline_stack_contains_core_resources() -> None:
    app = cdk.App()
    stack = BaselineStack(app, "TestStack")
    template = Template.from_stack(stack)

    template.resource_count_is("AWS::Lambda::Function", 4)
    template.resource_count_is("AWS::SQS::Queue", 1)
    template.resource_count_is("AWS::SNS::Topic", 1)
    template.resource_count_is("AWS::SNS::Subscription", 1)

    template.has_resource_properties(
        "AWS::Lambda::Function",
        {"Handler": "services.ingress.handler.lambda_handler"},
    )
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {"Handler": "services.consumer.handler.lambda_handler"},
    )


def test_baseline_stack_configures_api_gateway_with_authorizer() -> None:
    app = cdk.App()
    stack = BaselineStack(app, "TestStackApi")
    template = Template.from_stack(stack)

    template.resource_count_is("AWS::ApiGateway::RestApi", 1)
    template.resource_count_is("AWS::ApiGateway::Authorizer", 1)

    template.has_resource_properties(
        "AWS::ApiGateway::RestApi",
        {"Name": "event-ingestion-api-dev"},
    )

    template.has_resource_properties(
        "AWS::ApiGateway::Authorizer",
        {
            "Type": "TOKEN",
            "IdentitySource": "method.request.header.Authorization",
        },
    )

    template.has_resource_properties(
        "AWS::ApiGateway::Method",
        {
            "HttpMethod": "POST",
            "AuthorizationType": "CUSTOM",
            "MethodResponses": Match.array_with(
                [
                    Match.object_like({"StatusCode": "202"}),
                    Match.object_like({"StatusCode": "400"}),
                ]
            ),
        },
    )
