# Product Requirements Document (PRD)
## Product: AWS Event Ingestion Data Pipeline

**Version:** 1.0  
**Date:** February 11, 2026  
**Owner:** Data Platform Team  
**Related Document:** `docs/BRD.md`

## 1. Overview
This product provides a secure, scalable event ingestion capability for external API consumers. It accepts authenticated event submissions, validates payloads, processes events asynchronously through decoupled consumer paths, and persists both immutable raw data and consumer-specific projections in PostgreSQL.

## 2. Problem Statement
Current event intake is inconsistent and difficult to audit, causing operational risk and poor traceability. The product must establish a standardized, resilient event ingestion path with reliable failure handling and replay support.

## 3. Goals (V1)
- Accept authenticated external event submissions through a single API.
- Validate payloads before ingestion.
- Process events asynchronously across independent consumer paths.
- Persist immutable raw events and consumer-specific projections.
- Enforce idempotent consumer writes under at-least-once delivery semantics.
- Provide production-grade security, observability, and operational controls.

## 4. Non-Goals (V1)
- BI dashboards and advanced analytics modeling.
- Multi-region active/active deployment.
- Non-AWS deployment targets.

## 5. Personas
- External API Consumer: Submits events reliably and needs clear API feedback.
- Product/Data Engineering Team: Uses persisted event data and projections downstream.
- Platform/DevOps Team: Operates and monitors ingestion and processing infrastructure.
- Security/Compliance Team: Validates authentication, encryption, and auditability controls.

## 6. User Journeys
1. External client submits valid authenticated event request to `POST /v1/events`.
2. System validates payload, accepts request, and returns `202 Accepted` with `event_id`.
3. Event is published to SNS and delivered to at least two independent SQS consumer paths.
4. Consumers persist raw and projection data to Postgres with idempotent handling.
5. On processing failure, retries occur automatically; poison messages route to DLQ.

## 7. Functional Requirements
- `PRD-FR-1`: Expose `POST /v1/events` for ingestion.
- `PRD-FR-2`: Require Cognito JWT authentication for ingestion requests.
- `PRD-FR-3`: Validate incoming payload before publish.
- `PRD-FR-4`: Reject invalid payloads with `400 Bad Request` and validation error details.
- `PRD-FR-5`: Build a versioned event envelope for accepted events.
- `PRD-FR-6`: Publish accepted events to SNS.
- `PRD-FR-7`: Fan out events to at least two independent SQS queues.
- `PRD-FR-8`: Process each consumer queue independently.
- `PRD-FR-9`: Persist immutable raw event records.
- `PRD-FR-10`: Persist consumer-specific projection records.
- `PRD-FR-11`: Enforce idempotency on consumers using `(consumer_name, event_id)`.
- `PRD-FR-12`: Return `202 Accepted` with `event_id` for accepted requests.
- `PRD-FR-13`: Support retry and DLQ routing behavior per queue configuration.

## 8. API Contract (Product-Level)
### Endpoint
- `POST /v1/events`

### Authentication
- Cognito JWT is required.

### Request Requirements
- Content type must be JSON.
- Typical payload size must be below 64 KB.
- Required fields:
  - `event_type`: non-empty string
  - `occurred_at`: ISO-8601 timestamp
  - `source`: non-empty string
  - `payload`: JSON object

### Responses
- `202 Accepted`: event accepted; response includes generated `event_id`.
- `400 Bad Request`: payload validation failed; response includes validation details.
- `401/403`: authentication or authorization failure.
- `429/5xx`: transient service issues; clients may retry.

## 9. Retry, Error Handling, and Idempotency
- Use native SQS + Lambda retry behavior.
- Route failed messages to per-consumer DLQ with `maxReceiveCount = 5`.
- Support partial batch failure reporting from consumers.
- Guarantee idempotent persistence keyed by `(consumer_name, event_id)`.
- Prevent duplicate projection writes when API clients retry or messages are replayed.

## 10. Non-Functional Requirements
- Security: TLS in transit and encryption at rest (SNS, SQS, RDS, Secrets).
- Reliability: at-least-once processing without duplicate projection records.
- Scalability: independent scaling across consumer paths.
- Performance: initial API p95 latency target `<= 500 ms`.
- Observability: logs, metrics, tracing, and alarms for critical failure modes.
- Maintainability: infrastructure and application code managed in Python with CDK.

## 11. Success Metrics
- `>= 99.9%` successful consumer processing (excluding poison DLQ events).
- No unbounded queue lag under expected load.
- Zero duplicate projection writes during duplicate delivery or replay scenarios.
- Full traceability from API request to database persistence.

## 12. Risks and Mitigations
- DB connection spikes during burst load.  
Mitigation: RDS Proxy, reserved concurrency, tuned batch sizes.
- Poison messages repeatedly failing.  
Mitigation: per-consumer DLQ, alarms, replay runbook.
- Schema evolution breaks consumers.  
Mitigation: versioned envelope and backward-compatible change policy.

## 13. Release Scope and Environments
- V1 includes Dev and Prod deployments in separate AWS accounts.
- CI/CD platform is GitHub Actions.
- Initial release includes two consumer services with independent queues and DLQs.

## 14. Acceptance Criteria
- Authenticated valid request to `POST /v1/events` returns `202` and `event_id`.
- Invalid request payload returns `400` with validation errors.
- Accepted event is observed in both consumer paths.
- Raw and projection records are persisted correctly in Postgres.
- Duplicate message replay does not create duplicate projection outputs.
- DLQ routing and operational alarms trigger as configured.
