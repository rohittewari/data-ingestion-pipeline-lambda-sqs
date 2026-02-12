# Tech Stack
## Project: AWS Event Ingestion Data Pipeline

**Version:** 1.0  
**Date:** February 11, 2026  
**Source Documents:** `docs/BRD.md`, `docs/PRD.md`, `docs/Observability-Plan.md`

## 1. Core Platform
- **Cloud Provider:** AWS
- **Environments:** Dev and Prod (separate AWS accounts)

## 2. Application and Compute
- **Runtime Language:** Python
- **Execution Model:** Serverless
- **Compute Services:**
  - AWS Lambda (Ingress Lambda)
  - AWS Lambda (Consumer Lambda services)

## 3. API and Security
- **API Layer:** Amazon API Gateway (HTTP API)
- **Primary Endpoint:** `POST /v1/events`
- **Authentication:** Amazon Cognito (JWT-based auth)
- **Transport Security:** TLS in transit

## 4. Messaging and Async Processing
- **Event Fan-Out:** Amazon SNS
- **Queues:** Amazon SQS (per consumer)
- **Failure Queues:** SQS Dead-Letter Queues (DLQs)
- **Delivery Semantics:** At-least-once
- **Idempotency Strategy:** `(consumer_name, event_id)` keying in consumers

## 5. Data Layer
- **Primary Database:** Aurora/RDS PostgreSQL
- **Connection Management:** RDS Proxy (for burst/load protection)
- **Persistence Pattern:**
  - Immutable raw events
  - Consumer-specific projection tables
- **Schema Migrations:** Alembic

## 6. Infrastructure and Delivery
- **Infrastructure as Code:** AWS CDK (Python)
- **CI/CD:** GitHub Actions
- **Release Model:** Automated deployment pipeline to Dev and Prod

## 7. Observability and Operations
- **Logs/Metrics/Alarms:** Amazon CloudWatch
- **Tracing:** AWS X-Ray
- **Operational Controls:**
  - Queue and DLQ monitoring
  - API latency/error monitoring
  - Consumer failure and retry monitoring

## 8. Security and Compliance Controls
- **Encryption at Rest:** SNS, SQS, RDS, and Secrets
- **Authentication Enforcement:** Cognito JWT on ingestion API
- **Operational Auditability:** End-to-end traceability from API request to DB persistence
