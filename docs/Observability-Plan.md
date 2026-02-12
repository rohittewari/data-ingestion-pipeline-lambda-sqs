# Observability Plan
## Project: AWS Event Ingestion Data Pipeline

**Version:** 1.0  
**Date:** February 11, 2026  
**Source Documents:** `docs/BRD.md`, `docs/PRD.md`, `docs/Non-Functional.md`

## 1. Purpose
Define how the platform will monitor, trace, alert, and diagnose issues across ingestion, asynchronous processing, and persistence for V1.

## 2. Scope
- API ingestion path: `POST /v1/events`
- Ingress Lambda
- SNS topic fan-out
- Consumer SQS queues and DLQs
- Consumer Lambdas
- PostgreSQL persistence path
- Dev and Prod environments

## 3. Observability Objectives
- Detect production incidents quickly.
- Isolate failures by component (API, queue, consumer, DB).
- Provide end-to-end traceability from API request to DB write.
- Enable fast root-cause analysis with correlated logs, metrics, and traces.
- Validate SLO compliance and trigger alerts on breaches.

## 4. Telemetry Standards
### 4.1 Correlation and Context
- Every request/event must include or generate:
  - `event_id`
  - `request_id`
  - `trace_id`
  - `consumer_name` (for consumer paths)
  - `environment` (`dev` or `prod`)

### 4.2 Structured Logging
- Emit JSON logs for all services.
- Required log fields:
  - `timestamp`, `level`, `service`, `component`
  - `event_id`, `request_id`, `trace_id`
  - `message`, `error_code`, `error_type`
  - `latency_ms` (where applicable)
- Mask or omit sensitive data (tokens, secrets, PII).

### 4.3 Metrics Naming Convention
- Prefix custom metrics with `event_pipeline.`.
- Include dimensions:
  - `service`
  - `environment`
  - `consumer_name` (for consumer metrics)

### 4.4 Tracing
- Enable AWS X-Ray on API and Lambda components.
- Propagate trace context through async boundaries using message attributes where possible.

## 5. Golden Signals and Key Metrics
### 5.1 API Ingestion
- Request rate (`event_pipeline.api.requests`)
- Success rate (`2xx`) and error rates (`4xx`, `5xx`)
- p50/p95/p99 latency (`event_pipeline.api.latency_ms`)
- Validation failure count (`event_pipeline.api.validation_failures`)
- Auth failure count (`event_pipeline.api.auth_failures`)

### 5.2 Messaging (SNS/SQS)
- Publish success/failure count
- Queue depth and age of oldest message
- In-flight message count
- DLQ depth per consumer

### 5.3 Consumers
- Consumer processing success/failure count
- Retry count
- Batch partial failure count
- Processing latency per message/batch
- Idempotency conflict count (`event_pipeline.consumer.idempotency_conflicts`)

### 5.4 Database
- DB write latency
- Connection utilization/errors
- Transaction failures/timeouts
- Raw event write success/failure
- Projection write success/failure

## 6. SLOs, SLIs, and Error Budgets
### 6.1 SLOs
- API latency: p95 `<= 500 ms` for `POST /v1/events`.
- Consumer processing success: `>= 99.9%` (excluding poison DLQ events).
- Data correctness: zero duplicate projection writes.
- Queue health: no unbounded queue lag under expected load.

### 6.2 SLIs
- API latency SLI: percentile latency from API metrics.
- Processing success SLI: successful consumer messages / total processed.
- Duplicate write SLI: duplicate projection writes count.
- Queue lag SLI: queue depth and age-of-oldest trends.

### 6.3 Error Budget Policy
- If SLO breach risk exceeds threshold, pause non-critical changes and prioritize reliability remediation.

## 7. Dashboards
Create CloudWatch dashboards per environment:
1. **Executive Health**
- API success/error rates, latency, queue lag, DLQ depth.
2. **Ingestion/API**
- Request volume, auth failures, validation failures, `5xx`.
3. **Consumer Health**
- Per-consumer throughput, retries, failures, DLQ trend.
4. **Data Persistence**
- DB latency/errors, write success/failure, idempotency conflicts.
5. **Tracing Overview**
- End-to-end trace success and high-latency traces.

## 8. Alerting Plan
### 8.1 Severity Levels
- `SEV-1`: Critical outage or major data loss risk.
- `SEV-2`: Significant degradation impacting reliability/SLOs.
- `SEV-3`: Localized issue requiring investigation.

### 8.2 Alert Conditions (Initial)
- API `5xx` error rate above threshold for 5 minutes (`SEV-2`).
- API p95 latency > 500 ms sustained for 10 minutes (`SEV-2`).
- Any consumer DLQ depth > 0 for 10 minutes (`SEV-2`).
- Queue age of oldest message increasing continuously for 15 minutes (`SEV-2`).
- Consumer failure rate spike above baseline (`SEV-2`).
- DB connection errors above threshold (`SEV-1` or `SEV-2`, based on impact).
- Zero ingestion traffic during expected business windows (`SEV-3`).

### 8.3 Notification Targets
- Primary: Platform/DevOps on-call.
- Secondary: Data Engineering on-call.
- Escalation: Product owner + incident channel for `SEV-1`.

## 9. Runbooks
Maintain runbooks for:
1. API latency spike investigation.
2. Elevated API `5xx` errors.
3. Queue lag growth and consumer scaling response.
4. DLQ triage and replay procedure.
5. DB write failure and connection saturation.
6. Duplicate projection write investigation.

## 10. Retention and Access
- Log retention:
  - Dev: 14-30 days
  - Prod: 90 days minimum
- Metrics retention: default CloudWatch retention plus long-term exports if needed.
- Trace retention: environment-appropriate retention with sampling strategy.
- Access control: least privilege; read access for operations, restricted write/config changes.

## 11. Validation and Readiness Checklist
- Dashboards created and reviewed for Dev/Prod.
- Alerts configured, tested, and routed to on-call.
- Correlation IDs verified across API -> queue -> consumer -> DB.
- Failure injection tests completed (DLQ and alarm behavior).
- SLO dashboards available and baselines established.

## 12. Ownership and Review Cadence
- Observability owner: Platform/DevOps team.
- Metric quality owner: Service owners (Ingress and each consumer).
- Weekly review of alerts and false-positive rates.
- Monthly SLO/error-budget review with Product and Data Engineering.
