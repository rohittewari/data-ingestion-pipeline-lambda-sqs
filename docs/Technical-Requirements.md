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
