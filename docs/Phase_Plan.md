# Phase-wise Development Plan
## Project: AWS Event Ingestion Data Pipeline

**Version:** 1.0  
**Date:** February 11, 2026  
**Source Documents:** `docs/BRD.md`, `docs/PRD.md`, `docs/Technical-Requirements.md`

## 1. Objective
Deliver the application incrementally, starting with a bare minimum end-to-end vertical slice and progressively adding reliability, security, observability, and scale.

## 2. Delivery Cadence
- Default phase duration: 2 weeks
- End of each phase: demo, validation, and go/no-go gate

## 3. Phase Overview
| Phase | Goal | Key Outcome |
|---|---|---|
| Phase 0 | Foundation setup | Development and deployment baseline ready |
| Phase 1 | Bare minimum vertical slice | One complete event flow from API to DB |
| Phase 2 | Reliability baseline | Idempotency, retries, DLQ behavior |
| Phase 3 | Full fan-out | Two independent consumers live |
| Phase 4 | Observability and operations | Dashboards, tracing, alarms, runbooks |
| Phase 5 | Security and CI/CD hardening | Stronger controls and release confidence |
| Phase 6 | Performance and release readiness | SLO validation and production readiness |

## 4. Detailed Phase Plan
### Phase 0: Foundation
**Scope**
- Create service skeletons (Ingress Lambda + Consumer Lambda).
- Initialize AWS CDK project structure in Python.
- Setup base CI pipeline (lint + unit test hooks).
- Setup Alembic migration framework.
- Define local configuration and environment variable conventions.

**Deliverables**
- Deployable baseline stack in Dev.
- Seed migration and DB connectivity check.
- Minimal README for local setup and deployment.

**Exit Criteria**
- Team can deploy stack in Dev successfully.
- CI pipeline executes for pull requests.

### Phase 1: Bare Minimum Vertical Slice (MVP)
**Scope**
- Implement `POST /v1/events` through API Gateway + Lambda.
- Enable Cognito JWT auth check.
- Add payload validation (`event_type`, `occurred_at`, `source`, `payload`).
- Build versioned event envelope with generated `event_id`.
- Publish to SNS.
- Connect one SQS queue and one consumer Lambda.
- Persist raw event + one projection record in Postgres.
- Return `202` for accepted requests and `400` for invalid payloads.

**Deliverables**
- Working end-to-end flow: API -> SNS -> SQS -> Consumer -> Postgres.
- Basic structured logs with `event_id` correlation.

**Exit Criteria**
- Valid request returns `202` with `event_id`.
- Invalid payload returns `400` with validation details.
- Raw and projection records are persisted for accepted events.

### Phase 2: Reliability Baseline
**Scope**
- Enforce idempotent projection writes using `(consumer_name, event_id)`.
- Configure retry behavior with native SQS + Lambda.
- Add per-consumer DLQ with `maxReceiveCount = 5`.
- Support partial batch failure reporting in consumer.
- Add duplicate replay validation paths.

**Deliverables**
- Idempotency constraints and duplicate-safe consumer behavior.
- DLQ routing and retry configurations.

**Exit Criteria**
- Duplicate replay does not create duplicate projection rows.
- Poison messages route to DLQ after configured retries.

### Phase 3: Full Fan-Out Processing
**Scope**
- Add second SQS queue and second consumer Lambda.
- Add second projection model/table as needed.
- Ensure failure isolation between consumers.
- Validate independent processing and scalability controls.

**Deliverables**
- Two independent consumer paths active.
- Per-consumer queue and failure handling.

**Exit Criteria**
- Single accepted event is processed by both consumers.
- Failure in one consumer does not block the other consumer.

### Phase 4: Observability and Operations
**Scope**
- Implement structured logging standard (JSON).
- Add correlation IDs (`request_id`, `trace_id`, `event_id`).
- Enable X-Ray tracing across API and Lambda paths.
- Build CloudWatch dashboards for API, queues, consumers, and DB.
- Configure alerts for latency, errors, DLQ depth, and queue lag.
- Create incident/runbook documentation.

**Deliverables**
- Operational dashboards and actionable alerts.
- Traceability from API request to DB persistence.

**Exit Criteria**
- Failure injection triggers expected alerts.
- Teams can diagnose failures from dashboards/logs/traces.

### Phase 5: Security and Deployment Hardening
**Scope**
- Validate encryption at rest for SNS, SQS, RDS, and secrets.
- Harden IAM permissions with least privilege.
- Improve secret/config handling by environment.
- Harden CI/CD with migration checks and deployment gates.
- Verify Dev/Prod account separation in deployment workflows.

**Deliverables**
- Security control checklist completion.
- CI/CD gates for safer releases.

**Exit Criteria**
- Security review passes for V1 baseline.
- Deployment gates prevent unsafe schema/app rollouts.

### Phase 6: Performance and Release Readiness
**Scope**
- Run load and latency tests for API and consumer paths.
- Tune Lambda concurrency, queue settings, and batch sizes.
- Tune DB path (including RDS Proxy configuration).
- Finalize rollback/replay procedures.
- Execute full release readiness checklist.

**Deliverables**
- Performance report with tuning outcomes.
- Production readiness sign-off package.

**Exit Criteria**
- API p95 latency target `<= 500 ms` achieved under expected load.
- Queue lag remains bounded under expected traffic.
- Go-live checklist approved by Product, Platform, and Data teams.

## 5. Testing Strategy by Phase
1. Phase 1: Basic API, auth, validation, and single consumer E2E tests.
2. Phase 2: Retry, DLQ, idempotency, duplicate replay tests.
3. Phase 3: Multi-consumer fan-out and isolation tests.
4. Phase 4: Observability and alert validation tests.
5. Phase 5: Security and deployment gate verification tests.
6. Phase 6: Load/performance and production readiness tests.

## 6. Definition of Done (Each Phase)
- Code completed for scoped phase items.
- Automated tests for phase scope are passing.
- Dev deployment successful.
- Documentation updated for new behavior.
- Demo completed and accepted by stakeholders.

## 7. Risks in Incremental Delivery
- Scope creep in early phases delaying MVP.
- Under-defined API contract causing rework.
- Late discovery of data model or idempotency issues.
- Operational gaps if observability is delayed too long.

## 8. Mitigation for Delivery Risks
- Keep Phase 1 strictly minimal and end-to-end.
- Freeze API contract for V1 after Phase 1 exit.
- Add idempotency in Phase 2 before scaling consumers.
- Treat observability as mandatory in Phase 4 before hard launch.
