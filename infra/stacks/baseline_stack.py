from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_event_sources as lambda_event_sources
from aws_cdk import aws_logs as logs
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_sns as sns
from constructs import Construct


class BaselineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        consumer_queue = sqs.Queue(
            self,
            "ConsumerQueue",
            queue_name="event-pipeline-consumer-queue-dev",
            visibility_timeout=Duration.seconds(120),
        )

        ingress_function = lambda_.Function(
            self,
            "IngressFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="services.ingress.handler.lambda_handler",
            code=lambda_.Code.from_asset("src"),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={"QUEUE_URL": consumer_queue.queue_url},
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        consumer_function = lambda_.Function(
            self,
            "ConsumerFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="services.consumer.handler.lambda_handler",
            code=lambda_.Code.from_asset("src"),
            timeout=Duration.seconds(30),
            memory_size=256,
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        consumer_queue.grant_send_messages(ingress_function)
        consumer_queue.grant_consume_messages(consumer_function)

        consumer_function.add_event_source(
            lambda_event_sources.SqsEventSource(
                consumer_queue,
                batch_size=10,
            )
        )

        # Create SNS Topic for event distribution
        event_topic = sns.Topic(
            self,
            "EventTopic",
            topic_name="event-pipeline-topic-dev",
            display_name="Event Pipeline Topic"
        )

        # Grant Ingress Lambda permission to publish to SNS
        event_topic.grant_publish(ingress_function)

        # Create SNS subscription to SQS queue
        event_topic.add_subscription(
            sns.SqsSubscription(consumer_queue)
        )

        # Update Ingress Lambda environment with SNS Topic URL
        ingress_function.add_environment("SNS_TOPIC_ARN", event_topic.topic_arn)

        # Create API Gateway REST API
        api = apigateway.RestApi(
            self,
            "IngressApi",
            rest_api_name="event-ingestion-api-dev",
            description="Event Ingestion API for Phase 1",
            deploy_options=apigateway.StageOptions(
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            )
        )

        # Create /v1 resource
        v1_resource = api.root.add_resource("v1")

        # Create /v1/events resource
        events_resource = v1_resource.add_resource("events")

        # Add POST method to /v1/events
        events_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(
                ingress_function,
                proxy=False,
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="202",
                        response_templates={"application/json": ""},
                    ),
                    apigateway.IntegrationResponse(
                        status_code="400",
                        selection_pattern=".*error.*",
                        response_templates={"application/json": ""},
                    ),
                ]
            ),
            method_responses=[
                apigateway.MethodResponse(status_code="202"),
                apigateway.MethodResponse(status_code="400"),
            ]
        )

        # Stack Outputs
        CfnOutput(self, "ApiEndpoint", value=api.url)
        CfnOutput(self, "ConsumerQueueUrl", value=consumer_queue.queue_url)
        CfnOutput(self, "EventTopicArn", value=event_topic.topic_arn)
        CfnOutput(self, "IngressFunctionName", value=ingress_function.function_name)
        CfnOutput(self, "ConsumerFunctionName", value=consumer_function.function_name)

