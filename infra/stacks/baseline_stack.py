from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_event_sources as lambda_event_sources
from aws_cdk import aws_logs as logs
from aws_cdk import aws_sqs as sqs
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

        CfnOutput(self, "ConsumerQueueUrl", value=consumer_queue.queue_url)
        CfnOutput(self, "IngressFunctionName", value=ingress_function.function_name)
        CfnOutput(self, "ConsumerFunctionName", value=consumer_function.function_name)

