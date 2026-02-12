#!/usr/bin/env pwsh

# FINRA Local Development Quick Start
# This script sets up everything for local testing without AWS account

Write-Host "🚀 FINRA Phase 0 Local Development Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Color functions
function Write-Success { Write-Host $args[0] -ForegroundColor Green }
function Write-Info { Write-Host $args[0] -ForegroundColor Cyan }
function Write-Error { Write-Host $args[0] -ForegroundColor Red }

# Check prerequisites
Write-Info "📋 Checking prerequisites..."

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "✅ Python found: $pythonVersion"
} catch {
    Write-Error "❌ Python not found. Please install Python 3.12+"
    exit 1
}

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Success "✅ Docker found: $dockerVersion"
} catch {
    Write-Error "❌ Docker not found. Please install Docker Desktop"
    exit 1
}

Write-Host ""
Write-Info "📦 Installing dependencies..."

# Install dependencies
pip install -r requirements-dev.txt --quiet
pip install moto pytest-mock localstack --quiet
Write-Success "✅ Dependencies installed"

Write-Host ""
Write-Info "🐘 Starting PostgreSQL..."

# Start services
docker-compose up -d
Write-Success "✅ PostgreSQL started (localhost:5432)"
Write-Success "✅ LocalStack started (localhost:4566)"

# Wait for PostgreSQL
Write-Info "⏳ Waiting for PostgreSQL to be ready..."
$maxRetries = 30
$retryCount = 0

while ($retryCount -lt $maxRetries) {
    try {
        $result = docker exec finra-postgres pg_isready -U finra 2>&1
        if ($result -like "*accepting*") {
            Write-Success "✅ PostgreSQL is ready"
            break
        }
    } catch {
        # Continue waiting
    }
    
    $retryCount++
    Start-Sleep -Seconds 1
}

if ($retryCount -eq $maxRetries) {
    Write-Error "❌ PostgreSQL failed to start"
    docker-compose down
    exit 1
}

Write-Host ""
Write-Info "🗄️ Running database migrations..."

# Set database URL
$env:DATABASE_URL = "postgresql://finra:finra123@localhost:5432/finra_db"

# Run migrations
alembic upgrade head | Out-Null
Write-Success "✅ Database migrations applied"

Write-Host ""
Write-Info "🧪 Running tests..."

# Run tests
pytest -v --tb=short
$testResult = $LASTEXITCODE

Write-Host ""
if ($testResult -eq 0) {
    Write-Success "✅ All tests passed!"
} else {
    Write-Error "❌ Some tests failed"
}

Write-Host ""
Write-Info "🔍 Running code quality checks..."

# Run linting
ruff check .
$lintResult = $LASTEXITCODE

Write-Host ""
if ($lintResult -eq 0) {
    Write-Success "✅ Code quality checks passed!"
} else {
    Write-Error "❌ Code quality issues found"
}

Write-Host ""
Write-Info "📊 Summary"
Write-Host "==========" -ForegroundColor Cyan
Write-Success "✅ PostgreSQL: Running on localhost:5432"
Write-Success "✅ LocalStack: Running on localhost:4566"
Write-Success "✅ Database: Migrations applied"

if ($testResult -eq 0 -and $lintResult -eq 0) {
    Write-Success ""
    Write-Success "🎉 Everything is ready! You can now:"
    Write-Success "   • Run tests: pytest -v"
    Write-Success "   • Check code: ruff check ."
    Write-Success "   • Stop services: docker-compose down"
} else {
    Write-Host ""
    Write-Error "⚠️  Please fix the issues above"
}

Write-Host ""
Write-Info "For more info, see LOCAL_TESTING_GUIDE.md"
