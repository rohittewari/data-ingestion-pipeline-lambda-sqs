# Consolidated Requirements Document

**Version:** 1.0
**Date:** February 11, 2026
**Purpose:** Single consolidated document combining BRD, PRD, Technical Requirements, Functional, and Non-Functional sections.

## Included Source Documents
- `docs/BRD.md`
- `docs/PRD.md`
- `docs/Technical-Requirements.md`
- `docs/Functional.md`
- `docs/Non-Functional.md`

---

## Business Requirements Document (BRD)

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

---

## Product Requirements Document (PRD)

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

---

## Technical Requirements Document

# Technical Requirements Document
## Project: AWS Event Ingestion Data Pipeline

**Version:** 1.0  
**Date:** February 11, 2026  
**Owner:** Data Platform Team  
**Source Documents:** `docs/BRD.md`, `docs/PRD.md`, `docs/Functional.md`, `docs/Non-Functional.md`, `docs/tech-stack.md`, `docs/Observability-Plan.md`

## 1. Purpose
Define the implementation-level technical requirements for the V1 event ingestion platform.

## 2. Scope
- In scope: ingress API, authentication, validation, event envelope creation, SNS/SQS fan-out, consumer processing, PostgreSQL persistence, observability, and CI/CD deployment.
- Out of scope: BI dashboards, multi-region active/active, and non-AWS runtime targets.

## 3. Architecture Requirements
| ID | Requirement |
|---|---|
| TR-ARCH-01 | Platform shall run on AWS using serverless components. |
| TR-ARCH-02 | API ingress shall use API Gateway HTTP API and Lambda. |
| TR-ARCH-03 | Event distribution shall use SNS fan-out to at least two independent SQS queues. |
| TR-ARCH-04 | Each SQS queue shall be consumed by an independent Lambda consumer service. |
| TR-ARCH-05 | Persistence shall use Aurora/RDS PostgreSQL for raw and projection data. |
| TR-ARCH-06 | Environments shall be isolated across Dev and Prod AWS accounts. |

## 4. API Technical Requirements
### 4.1 Endpoint
- Method: `POST`
- Path: `/v1/events`
- Auth: Cognito JWT required

### 4.2 Request Contract
| Field | Type | Requirement | Notes |
|---|---|---|---|
| `event_type` | string | Required | Must be non-empty |
| `occurred_at` | string | Required | ISO-8601 timestamp |
| `source` | string | Required | Must be non-empty |
| `payload` | object | Required | JSON object |

Additional rules:
- `Content-Type` must be `application/json`.
- Typical payload size must remain below 64 KB.

### 4.3 Response Contract
- `202 Accepted`: event accepted, includes generated `event_id`.
- `400 Bad Request`: validation failed, includes field-level validation errors.
- `401/403`: authentication/authorization failure.
- `429/5xx`: transient service issues; client retries allowed.

## 5. Event Envelope Requirements
| ID | Requirement |
|---|---|
| TR-EVT-01 | Ingress service shall construct a versioned envelope for accepted events. |
| TR-EVT-02 | Envelope shall include `event_id`, `event_version`, `ingested_at`, and original payload body. |
| TR-EVT-03 | `event_id` shall be globally unique within the system. |
| TR-EVT-04 | Envelope versioning shall support backward-compatible schema evolution. |

## 6. Messaging and Processing Requirements
| ID | Requirement |
|---|---|
| TR-MSG-01 | Accepted events shall be published to SNS exactly once per accepted API request. |
| TR-MSG-02 | SNS shall deliver events to all configured consumer SQS queues. |
| TR-MSG-03 | Consumers shall process messages independently with no cross-consumer coupling. |
| TR-MSG-04 | Consumer failures shall not block ingestion or other consumer paths. |
| TR-MSG-05 | Consumers shall support partial batch failure reporting for SQS-triggered Lambda batches. |

## 7. Data Persistence Requirements
### 7.1 Raw Events
| ID | Requirement |
|---|---|
| TR-DATA-01 | System shall persist immutable raw event records for every accepted event. |
| TR-DATA-02 | Raw event records shall store `event_id`, envelope metadata, and payload snapshot. |
| TR-DATA-03 | Raw event records shall not be updated after insert (append-only behavior). |

### 7.2 Projection Data
| ID | Requirement |
|---|---|
| TR-DATA-04 | Each consumer shall persist projection records according to its consumer contract. |
| TR-DATA-05 | Projection persistence shall enforce idempotency using `(consumer_name, event_id)`. |
| TR-DATA-06 | Duplicate message deliveries shall not produce duplicate projection rows. |

### 7.3 Schema and Migrations
| ID | Requirement |
|---|---|
| TR-DATA-07 | Database schema changes shall be managed through Alembic migrations. |
| TR-DATA-08 | Migration execution shall be integrated into deployment workflows. |

## 8. Retry and Failure Handling Requirements
| ID | Requirement |
|---|---|
| TR-ERR-01 | Consumer retries shall rely on native SQS + Lambda retry behavior. |
| TR-ERR-02 | Each consumer queue shall route messages to a DLQ after `maxReceiveCount = 5`. |
| TR-ERR-03 | DLQ depth and failure conditions shall emit operational alarms. |
| TR-ERR-04 | API retries for `429/5xx` shall not create duplicate projection output. |

## 9. Security Requirements
| ID | Requirement |
|---|---|
| TR-SEC-01 | All in-transit communication shall use TLS. |
| TR-SEC-02 | SNS, SQS, RDS, and Secrets storage shall enforce encryption at rest. |
| TR-SEC-03 | API access shall require valid Cognito JWT tokens. |
| TR-SEC-04 | IAM permissions shall follow least-privilege for all services. |
| TR-SEC-05 | Sensitive data shall not be logged in plaintext. |

## 10. Observability Requirements
| ID | Requirement |
|---|---|
| TR-OBS-01 | System shall emit structured JSON logs with correlation IDs. |
| TR-OBS-02 | CloudWatch metrics shall track API latency/errors, queue lag, DLQ depth, and consumer failures. |
| TR-OBS-03 | X-Ray tracing shall provide end-to-end visibility from API ingress to persistence path. |
| TR-OBS-04 | Operational alarms shall be configured for critical failure modes and SLO risk conditions. |
| TR-OBS-05 | System shall provide traceability from request (`event_id`) to DB persistence records. |

## 11. Performance and Scalability Requirements
| ID | Requirement |
|---|---|
| TR-PERF-01 | API p95 latency target for `POST /v1/events` shall be `<= 500 ms`. |
| TR-PERF-02 | Consumer paths shall be independently scalable via queue-backed architecture. |
| TR-PERF-03 | System shall maintain bounded queue lag under expected workload. |
| TR-PERF-04 | DB connection handling shall support burst traffic (for example, via RDS Proxy). |

## 12. DevOps and Deployment Requirements
| ID | Requirement |
|---|---|
| TR-DEVOPS-01 | Infrastructure shall be managed as code using AWS CDK in Python. |
| TR-DEVOPS-02 | CI/CD shall run in GitHub Actions for build, test, and deployment orchestration. |
| TR-DEVOPS-03 | Dev and Prod deployments shall use environment-specific configuration and secrets. |
| TR-DEVOPS-04 | Deployment workflow shall include migration execution and health validation checks. |

## 13. Testing and Validation Requirements
### 13.1 Functional Validation
1. Valid authenticated request returns `202` and `event_id`.
2. Invalid payload returns `400` with validation errors.
3. Accepted event appears in both consumer queues.
4. Raw and projection records persist correctly.
5. Duplicate replay does not create duplicate projection writes.
6. Failed messages route to DLQ after configured retries.

### 13.2 Non-Functional Validation
1. API latency p95 meets `<= 500 ms` target under expected load.
2. Alerts trigger for simulated failure conditions.
3. End-to-end traces can link API request to DB writes.
4. Security controls confirm TLS and encryption-at-rest coverage.

## 14. Traceability to Business Requirements
| Technical Area | BRD Reference | PRD Reference |
|---|---|---|
| API + auth + validation | `FR-1`, `FR-2`, `FR-3`, `FR-11`, `FR-12` | Section 7 and Section 8 |
| Fan-out processing | `FR-4`, `FR-5`, `FR-6` | Section 7 |
| Persistence + idempotency | `FR-7`, `FR-8`, `FR-9` | Section 7 and Section 9 |
| Retry + DLQ behavior | `FR-10`, `RETRY-1` to `RETRY-5` | Section 9 |
| NFR and observability | `NFR-1` to `NFR-6` | Section 10 and Section 11 |

## 15. Assumptions
- Ordering guarantees are not globally required.
- Two consumer services are sufficient for initial release.
- Payloads are typically below 64 KB.

---

## Functional Requirements Specification

# Functional Requirements Specification
## Project: AWS Event Ingestion Data Pipeline

**Version:** 1.0  
**Date:** February 11, 2026  
**Source Documents:** `docs/BRD.md`, `docs/PRD.md`

## 1. Purpose
Define the functional behavior required for the V1 event ingestion application.

## 2. In Scope
- External event ingestion through authenticated API.
- Payload validation and rejection for invalid requests.
- Async fan-out processing through SNS and SQS.
- Independent consumer processing and PostgreSQL persistence.
- Retry, DLQ handling, and idempotent writes.

## 3. Out of Scope
- BI dashboards and advanced analytics outputs.
- Multi-region active/active deployment.
- Non-AWS hosting targets.

## 4. Functional Requirements
| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FUNC-01 | System shall expose `POST /v1/events` to ingest external events. | Must | Endpoint is reachable and documented for clients. |
| FUNC-02 | System shall authenticate request tokens using Cognito JWT. | Must | Requests without valid JWT fail with `401/403`. |
| FUNC-03 | System shall validate payload shape and required fields before publish. | Must | Missing/invalid required fields produce validation failures. |
| FUNC-04 | System shall reject invalid payloads with `400 Bad Request` and validation details. | Must | Invalid payload response contains field-level error info. |
| FUNC-05 | System shall create a versioned event envelope for accepted payloads. | Must | Envelope includes metadata and generated `event_id`. |
| FUNC-06 | System shall publish accepted events to SNS. | Must | Accepted events appear on configured SNS topic. |
| FUNC-07 | SNS shall fan out each event to at least two independent SQS queues. | Must | One publish is observed in both consumer queues. |
| FUNC-08 | Each consumer shall process messages independently. | Must | Failure in one consumer path does not block the other. |
| FUNC-09 | System shall persist immutable raw event records in Postgres. | Must | Raw event row exists for each accepted event. |
| FUNC-10 | Each consumer shall persist consumer-specific projection data in Postgres. | Must | Projection rows are written per consumer contract. |
| FUNC-11 | Consumers shall enforce idempotent writes keyed by `(consumer_name, event_id)`. | Must | Replays do not create duplicate projection rows. |
| FUNC-12 | System shall return `202 Accepted` with `event_id` for accepted requests. | Must | Client receives `202` and non-empty `event_id`. |
| FUNC-13 | Failed message processing shall retry and route to DLQ after `maxReceiveCount = 5`. | Must | Poison messages land in per-consumer DLQ after retries. |
| FUNC-14 | Consumers shall support partial batch failure reporting. | Should | Successful records in a batch are not unnecessarily retried. |

## 5. Payload Validation Rules (V1)
- Content-Type must be JSON.
- Payload size should remain below 64 KB.
- Required fields:
  - `event_type` as non-empty string
  - `occurred_at` as ISO-8601 timestamp
  - `source` as non-empty string
  - `payload` as JSON object
- Validation failures return `400` with structured error details.

## 6. Response Behavior
- `202 Accepted`: request accepted; response returns generated `event_id`.
- `400 Bad Request`: payload validation failure.
- `401/403`: authentication or authorization failure.
- `429/5xx`: transient service conditions; client retry permitted.

## 7. Traceability Matrix
| Functional ID | BRD Mapping | PRD Mapping |
|---|---|---|
| FUNC-01 to FUNC-12 | `FR-1` to `FR-12` in `docs/BRD.md` | `PRD-FR-1` to `PRD-FR-12` in `docs/PRD.md` |
| FUNC-13 | `RETRY-2` in `docs/BRD.md` | `PRD-FR-13` in `docs/PRD.md` |
| FUNC-14 | `RETRY-3` in `docs/BRD.md` | Section 9 in `docs/PRD.md` |

## 8. Functional Acceptance Scenarios
1. Valid authenticated event submission returns `202` and `event_id`.
2. Invalid event submission returns `400` with validation details.
3. Accepted event is delivered to both consumer queues.
4. Raw and projection records persist correctly in Postgres.
5. Duplicate replay does not create duplicate projection outputs.
6. Poison message is moved to DLQ after configured retries.

---

## Non-Functional Requirements Specification

# Non-Functional Requirements Specification
## Project: AWS Event Ingestion Data Pipeline

**Version:** 1.0  
**Date:** February 11, 2026  
**Source Documents:** `docs/BRD.md`, `docs/PRD.md`

## 1. Purpose
Define the quality attributes and operational constraints required for the V1 event ingestion application.

## 2. Scope
- Applies to ingress API, asynchronous messaging, consumer services, and persistence components.
- Covers Dev and Prod deployment environments.

## 3. Non-Functional Requirements
| ID | Category | Requirement | Target | Verification |
|---|---|---|---|---|
| NFR-01 | Security | All service communication shall use TLS in transit. | TLS enabled for API and internal service endpoints. | Security configuration and integration verification. |
| NFR-02 | Security | Data shall be encrypted at rest for SNS, SQS, RDS, and Secrets. | Encryption enabled on all listed services. | Infrastructure configuration review and deployment checks. |
| NFR-03 | Reliability | Processing shall support at-least-once delivery without duplicate projection writes. | Zero duplicate projection records for replay/duplicate delivery tests. | Replay and duplicate-message test scenarios. |
| NFR-04 | Reliability | Failed messages shall not block indefinite processing. | Per-consumer DLQ routing after `maxReceiveCount = 5`. | Queue and DLQ behavior validation under failure tests. |
| NFR-05 | Scalability | Consumer processing paths shall scale independently. | Independent scaling controls configured per consumer path. | Load tests and infrastructure scaling configuration checks. |
| NFR-06 | Performance | Ingress API latency shall meet initial service target. | p95 latency for `POST /v1/events` <= 500 ms under expected load. | Performance testing and API latency metrics. |
| NFR-07 | Observability | Platform shall provide actionable telemetry for failures and throughput. | Logs, metrics, traces, and alarms for key failure modes are active. | Dashboard/alarm validation and trace sampling checks. |
| NFR-08 | Maintainability | Infrastructure and application code shall be manageable through consistent tooling. | Python + CDK managed IaC and application deployment flow. | Codebase and pipeline review. |
| NFR-09 | Operability | System shall support end-to-end traceability from request to persistence. | Request correlation from API to DB record is available. | Traceability tests and log correlation review. |
| NFR-10 | Environment Isolation | Dev and Prod shall remain operationally isolated. | Separate AWS accounts and environment-specific configs. | Environment configuration audit. |

## 4. SLOs and Monitoring Signals
- API latency SLO: `POST /v1/events` p95 <= 500 ms.
- Processing success SLO: >= 99.9% successful consumer processing (excluding poison DLQ events).
- Data correctness SLO: zero duplicate projection writes.
- Queue health SLO: no unbounded queue lag under expected load.

Primary monitoring signals:
- API 2xx/4xx/5xx rates and latency percentiles.
- Queue depth, age of oldest message, DLQ depth.
- Consumer success/failure counts and retry counts.
- Database write latency/error rates.
- End-to-end trace completion rate.

## 5. Constraints and Assumptions
- Typical payload size is below 64 KB.
- Global event ordering is not required.
- Initial release includes two consumer services.
- CI/CD platform is GitHub Actions.

## 6. Acceptance Scenarios
1. Security controls validated for in-transit and at-rest encryption.
2. Load test confirms API p95 latency within target.
3. Replay and duplicate delivery tests produce no duplicate projection records.
4. Failure injection confirms DLQ routing and alarm behavior.
5. Traceability validation confirms API request to DB persistence linkage.
