#!/usr/bin/env python3
import os

import aws_cdk as cdk
from infra.stacks.baseline_stack import BaselineStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1")),
)

BaselineStack(app, "EventIngestionBaselineStack", env=env)

app.synth()

