# Application Risk Register

## Project
AWS Event Ingestion Data Pipeline

## Date
February 11, 2026

## Risks
| ID | Risk | Impact | Likelihood | Mitigation | Owner |
|---|---|---|---|---|---|
| R-01 | DB connection spikes under burst load | High | Medium | Use RDS Proxy, reserved Lambda concurrency, and tuned batch sizes. | Platform/DevOps |
| R-02 | Poison messages repeatedly fail and block throughput | High | Medium | Configure per-consumer DLQs, alerting, and replay runbook. | Data Engineering |
| R-03 | Schema evolution breaks consumers | High | Medium | Use versioned event envelope and backward-compatible schema policy. | Data Platform |
| R-04 | Invalid payloads pass validation and degrade downstream data quality | High | Medium | Enforce strict API validation rules and return `400` with field-level errors. | API/Ingress Team |
| R-05 | Duplicate deliveries create duplicate projection writes | High | Medium | Enforce idempotent writes with `(consumer_name, event_id)` keying. | Consumer Service Owners |
| R-06 | Authentication/authorization misconfiguration exposes API | High | Low | Enforce Cognito JWT validation, least-privilege IAM, and regular security reviews. | Security/Platform |
| R-07 | DLQ backlog grows without timely replay | Medium | Medium | Add DLQ depth alarms, ownership, and SLA-backed replay procedures. | Operations |
| R-08 | Observability gaps slow incident diagnosis | Medium | Medium | Require correlation IDs, CloudWatch dashboards, X-Ray tracing, and actionable alarms. | Platform/DevOps |
| R-09 | Retry storms increase AWS cost and latency | Medium | Medium | Set retry bounds, monitor queue lag/concurrency, and use throttling controls. | Platform/FinOps |
| R-10 | CI/CD and DB migration drift causes runtime failures | High | Low | Gate releases with migration checks and environment parity validation. | Platform/Release |

## Review Cadence
- Review risks weekly during release cycles.
- Reassess impact/likelihood after major architecture changes.
