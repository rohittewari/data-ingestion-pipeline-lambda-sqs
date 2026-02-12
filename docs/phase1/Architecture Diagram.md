┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /v1/events
       ▼
┌──────────────────┐
│  API Gateway     │
│ + Cognito Auth   │
└────────┬─────────┘
         │ Route to Lambda
         ▼
┌──────────────────┐
│ Ingress Lambda   │
│ - Validate       │
│ - Generate ID    │
│ - Publish SNS    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   SNS Topic      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   SQS Queue      │
└────────┬─────────┘
         │ Trigger
         ▼
┌──────────────────┐
│ Consumer Lambda  │
│ - Parse message  │
│ - Store in DB    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   PostgreSQL     │
│ - raw_events     │
│ - projections    │
└──────────────────┘