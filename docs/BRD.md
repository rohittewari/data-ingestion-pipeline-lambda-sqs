## Business Requirements Document (BRD)
### Project: AWS Event Ingestion Data Pipeline

**Version:** 1.0  
**Date:** February 11, 2026  
**Owner:** Data Platform Team

### 1. Purpose
Build a secure, scalable pipeline to ingest external user events and persist both raw and processed data into PostgreSQL for downstream operational and analytics use.

### 2. Business Problem
Current event intake is not standardized, resilient, or auditable. The business needs:
- Reliable ingestion from external users.
- Decoupled processing for multiple downstream consumers.
- Durable storage with replay and traceability.
- Production-grade security, monitoring, and failure handling.

### 3. Objectives
- Accept authenticated external event submissions via API.
- Process events asynchronously with independent consumer services.
- Persist immutable raw events and consumer-specific projections.
- Support at-least-once delivery with idempotent writes.
- Operate across Dev and Prod with automated CI/CD.

### 4. Scope
**In Scope**
- API Gateway HTTP API with Cognito JWT auth.
- Ingress Lambda to validate and publish events.
- SNS topic fan-out to SQS queues.
- Two Lambda consumers with separate queues and DLQs.
- Aurora/RDS PostgreSQL persistence.
- Alembic migrations in deployment workflow.
- CloudWatch, alarms, and X-Ray tracing.

**Out of Scope**
- BI dashboards and advanced analytics modeling.
- Multi-region active/active deployment.
- Non-AWS deployment targets.

### 5. Stakeholders
- Product Owner (event ingestion capability)
- External API consumers
- Platform/DevOps team
- Data engineering team
- Security/compliance team

### 6. Functional Requirements
- `FR-1`: System shall expose `POST /v1/events` for event ingestion.
- `FR-2`: System shall authenticate requests using Cognito JWT.
- `FR-3`: Ingress service shall validate payload and build a versioned event envelope.
- `FR-4`: Ingress service shall publish accepted events to SNS.
- `FR-5`: SNS shall fan out events to at least two independent SQS queues.
- `FR-6`: Each consumer shall process messages independently and write to Postgres.
- `FR-7`: System shall store immutable raw events.
- `FR-8`: System shall store consumer-specific projection data.
- `FR-9`: Consumers shall enforce idempotency for duplicate delivery handling.
- `FR-10`: Failed messages shall be retried and eventually routed to DLQ.
- `FR-11`: System shall return `202 Accepted` and `event_id` for accepted requests.
- `FR-12`: System shall reject invalid payloads with `400 Bad Request` and validation error details.

### 7. Retry and Error Handling Requirements
- `RETRY-1`: Consumer processing shall use native SQS + Lambda retries.
- `RETRY-2`: Each consumer queue shall route failed messages to DLQ after `maxReceiveCount = 5`.
- `RETRY-3`: Consumers shall support partial batch failure reporting.
- `RETRY-4`: Consumers shall guarantee idempotent persistence using `(consumer_name, event_id)` keying.
- `RETRY-5`: API clients may retry `429/5xx`; duplicate events must not create duplicate projection records.

### 8. Non-Functional Requirements
- `NFR-1` Security: TLS in transit; encryption at rest for SNS, SQS, RDS, Secrets.
- `NFR-2` Reliability: At-least-once processing with no duplicate projection records.
- `NFR-3` Scalability: Support independent scaling of each consumer path.
- `NFR-4` Performance: Initial API p95 latency target <= 500 ms.
- `NFR-5` Observability: Logs, metrics, tracing, and alarms for key failure modes.
- `NFR-6` Maintainability: Infrastructure and app code managed in Python with CDK.

### 9. Assumptions
- Typical payload size is below 64 KB.
- Ordering is not globally required (standard SQS acceptable).
- Two consumers are sufficient for initial release.
- Dev and Prod use separate AWS accounts.
- CI/CD platform is GitHub Actions.

### 10. Risks and Mitigations
- Connection spikes to DB under burst load.  
Mitigation: Use RDS Proxy, reserved concurrency, tuned batch sizes.
- Poison messages causing repeated failures.  
Mitigation: Per-consumer DLQ, alarms, replay runbook.
- Schema evolution breaking consumers.  
Mitigation: Versioned envelope + backward-compatible change policy.

### 11. Success Metrics
- 99.9%+ successful consumer processing (excluding DLQ poison events).
- No unbounded queue lag under expected load.
- Zero duplicate projection writes for replayed messages.
- Full traceability from API request to DB persistence.

### 12. Acceptance Criteria
- Authenticated request to `POST /v1/events` returns `202` with `event_id`.
- Invalid request payload to `POST /v1/events` returns `400` with validation errors.
- Published event is observed in both consumer paths.
- Raw and projection records are persisted correctly in Postgres.
- Duplicate message replay does not create duplicate projection output.
- DLQ and operational alarms trigger as designed.
