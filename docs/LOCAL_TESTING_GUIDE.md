# Local Development & Testing Guide (No AWS Account Required)

This guide shows how to test and develop Phase 0 locally using mocking and Docker.

---

## Prerequisites

Install on your machine:

```powershell
# Check Python version (should be 3.12+)
python --version

# Install Docker Desktop (for local services)
# Download from: https://www.docker.com/products/docker-desktop

# Verify Docker
docker --version
```

---

## Setup Local Development Environment

### 1. Install Dependencies

```powershell
cd c:\Rohit\1_Interview\FINRA_INTERVIEW

# Install development dependencies
pip install -r requirements-dev.txt

# Install testing tools
pip install moto pytest-mock  # Mock AWS services
pip install localstack         # Alternative: Full AWS emulation
```

### 2. Run All Tests Locally

```powershell
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_ingress_handler.py -v
pytest tests/test_consumer_handler.py -v
pytest tests/test_cdk_stack.py -v

# Run with coverage
pytest --cov=src
```

### 3. Run Linting & Code Quality

```powershell
# Check code quality
ruff check .

# Auto-fix formatting
ruff format .

# Check for unused imports
ruff check . --select F401
```

---

## Setup Local Database (PostgreSQL)

### Option A: Using Docker (Recommended)

**1. Start PostgreSQL in Docker**

```powershell
# Pull PostgreSQL image
docker pull postgres:15

# Run PostgreSQL container
docker run --name finra-postgres `
  -e POSTGRES_USER=finra `
  -e POSTGRES_PASSWORD=finra123 `
  -e POSTGRES_DB=finra_db `
  -p 5432:5432 `
  -d postgres:15

# Verify container is running
docker ps
```

**2. Run Alembic Migrations**

```powershell
# Set database connection (update alembic.ini or use env var)
$env:DATABASE_URL = "postgresql://finra:finra123@localhost:5432/finra_db"

# View migration status
alembic current

# Run migrations
alembic upgrade head

# Check if tables were created
# (Connect with: psql -U finra -d finra_db -h localhost)
```

**3. Stop PostgreSQL when done**

```powershell
docker stop finra-postgres
docker rm finra-postgres
```

### Option B: Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: finra
      POSTGRES_PASSWORD: finra123
      POSTGRES_DB: finra_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Then run:

```powershell
docker-compose up -d        # Start
docker-compose down         # Stop
docker-compose logs -f      # View logs
```

---

## Mock AWS Services Locally

### Option 1: Using `moto` (Recommended for Tests)

Moto allows you to mock AWS services in unit tests.

**Example: Mock SQS in tests**

Create `tests/test_with_mocks.py`:

```python
import json
import boto3
from moto import mock_sqs
from src.services.ingress.handler import lambda_handler

@mock_sqs
def test_ingress_with_mock_sqs():
    # Create mock SQS queue
    sqs = boto3.client('sqs', region_name='us-east-1')
    response = sqs.create_queue(QueueName='test-queue')
    queue_url = response['QueueUrl']
    
    # Set environment variable
    import os
    os.environ['QUEUE_URL'] = queue_url
    
    # Call handler
    response = lambda_handler({"hello": "world"}, None)
    
    # Verify
    assert response["statusCode"] == 200
    
    # Check SQS messages
    messages = sqs.receive_message(QueueUrl=queue_url)
    assert 'Messages' in messages
```

Run it:

```powershell
pytest tests/test_with_mocks.py -v
```

### Option 2: Using LocalStack (Full AWS Emulation)

LocalStack runs **all AWS services** locally in Docker.

**1. Install LocalStack**

```powershell
pip install localstack
```

**2. Start LocalStack**

```powershell
# Run LocalStack in Docker
docker run -d `
  -p 4566:4566 `
  -e SERVICES=sqs,lambda,dynamodb `
  -v /var/run/docker.sock:/var/run/docker.sock `
  localstack/localstack:latest

# Verify it's running
docker logs $(docker ps --filter name=localstack -q)
```

**3. Configure AWS SDK to use LocalStack**

```python
# Create a LocalStack client
import boto3

sqs = boto3.client(
    'sqs',
    endpoint_url='http://localhost:4566',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

# Create queue
response = sqs.create_queue(QueueName='test-queue')
print(response)
```

**4. Stop LocalStack**

```powershell
docker stop $(docker ps --filter name=localstack -q)
```

---

## Complete Local Testing Workflow

### Run Everything Locally

```powershell
# 1. Start services
docker-compose up -d

# 2. Run migrations
$env:DATABASE_URL = "postgresql://finra:finra123@localhost:5432/finra_db"
alembic upgrade head

# 3. Run tests
pytest -v

# 4. Run linting
ruff check .

# 5. Stop services
docker-compose down
```

---

## Local CI/CD Simulation

Run the exact same checks as GitHub Actions locally:

```powershell
# 1. Install dependencies
pip install -r requirements-dev.txt

# 2. Lint (same as CI)
ruff check .

# 3. Unit tests (same as CI)
pytest -q
```

---

## Development Commands Reference

| Command | Purpose |
|---------|---------|
| `pytest -v` | Run all tests with details |
| `pytest tests/test_ingress_handler.py -v` | Run specific test file |
| `pytest -k "test_name"` | Run tests matching pattern |
| `pytest --pdb` | Drop into debugger on failure |
| `ruff check .` | Check code quality |
| `ruff format .` | Auto-fix formatting |
| `docker-compose up -d` | Start local services |
| `docker-compose down` | Stop local services |
| `alembic upgrade head` | Apply migrations |
| `alembic downgrade -1` | Rollback 1 migration |

---

## Example: Full Local Test Session

```powershell
# 1. Start PostgreSQL
docker-compose up -d
Write-Host "Waiting for PostgreSQL to be ready..."
Start-Sleep -Seconds 3

# 2. Set database URL
$env:DATABASE_URL = "postgresql://finra:finra123@localhost:5432/finra_db"

# 3. Run migrations
alembic upgrade head
Write-Host "✅ Migrations complete"

# 4. Run tests
pytest -v
Write-Host "✅ Tests complete"

# 5. Run linting
ruff check .
Write-Host "✅ Linting complete"

# 6. Stop services
docker-compose down
Write-Host "✅ Services stopped"
```

---

## Troubleshooting

### PostgreSQL Connection Refused

```powershell
# Check if container is running
docker ps | findstr postgres

# View logs
docker logs finra-postgres

# Restart container
docker restart finra-postgres
```

### Alembic Migration Fails

```powershell
# Check current migration status
alembic current

# Downgrade and try again
alembic downgrade -1
alembic upgrade head

# View migration history
alembic history --verbose
```

### Import Errors in Tests

```powershell
# Ensure you're in the project root
cd c:\Rohit\1_Interview\FINRA_INTERVIEW

# Verify PYTHONPATH
$env:PYTHONPATH = (Get-Location).Path

# Run tests again
pytest -v
```

---

## What's Ready for Local Testing

✅ **All unit tests** - Run locally with pytest  
✅ **Code quality** - Check with ruff  
✅ **Lambda handlers** - Call as functions  
✅ **Database migrations** - Run with Alembic  
✅ **SQS simulation** - Mock with moto or LocalStack  
✅ **CI/CD checks** - Run same checks locally  

---

## Next Steps

1. **Run the setup**: `docker-compose up -d`
2. **Apply migrations**: `alembic upgrade head`
3. **Run tests**: `pytest -v`
4. **Check quality**: `ruff check .`
5. **Stop services**: `docker-compose down`

**You have everything you need to develop Phase 0 locally! 🚀**

For AWS deployment later, you'll only need Phase 1+ when actual AWS resources are required.
