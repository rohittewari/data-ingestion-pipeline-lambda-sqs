# AWS Event Ingestion Data Pipeline (Phase 0 Baseline)

This repository contains the Phase 0 baseline for the event ingestion pipeline:
- Python service skeletons (`ingress` and `consumer`)
- AWS CDK baseline stack
- Alembic migration framework with initial seed migration
- Local environment conventions
- CI pipeline with lint and unit tests

## Prerequisites
- Python 3.11+
- AWS CLI configured for your Dev account
- Node.js (required by AWS CDK CLI)
- PostgreSQL (local or remote)

## Project Structure
- `app.py`: CDK app entrypoint
- `infra/stacks/baseline_stack.py`: baseline AWS infrastructure
- `src/services/ingress/handler.py`: ingress Lambda skeleton
- `src/services/consumer/handler.py`: consumer Lambda skeleton
- `migrations/`: Alembic configuration and migrations
- `scripts/db_connectivity_check.py`: DB connectivity check script
- `.github/workflows/ci.yml`: CI lint/test workflow

## Local Setup
1. Create and activate a virtual environment.
2. Install dependencies:
```bash
pip install -r requirements-dev.txt
```
3. Copy environment template:
```bash
cp .env.example .env
```

## Run Lint and Tests
```bash
ruff check .
pytest -q
```

## Database Migration (Alembic)
Set `DB_URL` first, then run:
```bash
alembic upgrade head
```

Connectivity check:
```bash
python scripts/db_connectivity_check.py
```

## CDK Baseline Deployment (Dev)
Bootstrap once per account/region:
```bash
cdk bootstrap aws://$CDK_DEFAULT_ACCOUNT/$CDK_DEFAULT_REGION
```

Synthesize:
```bash
cdk synth
```

Deploy:
```bash
cdk deploy EventIngestionBaselineStack
```

## Environment Conventions
Use `.env.example` as the source of truth for required variables:
- `APP_ENV`
- `LOG_LEVEL`
- `AWS_REGION`
- `CDK_DEFAULT_ACCOUNT`
- `CDK_DEFAULT_REGION`
- `DB_URL`
- `QUEUE_URL` (injected by infrastructure for Lambda runtime)

