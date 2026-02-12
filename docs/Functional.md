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
