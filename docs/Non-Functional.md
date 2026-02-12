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
