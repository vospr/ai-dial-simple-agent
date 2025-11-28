# Launch script for test.py (PowerShell)
# Usage: .\run_tests.ps1

Write-Host "🚀 Launching AI DIAL Simple Agent Test Suite" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Navigate to project directory
Set-Location $PSScriptRoot

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Install/upgrade dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip
pip install -r requirements.txt

# Check if DIAL_API_KEY is set
if (-not $env:DIAL_API_KEY) {
    Write-Host "⚠️  DIAL_API_KEY not set. Using default from test.py" -ForegroundColor Yellow
    Write-Host "   To set: `$env:DIAL_API_KEY='your-key-here'" -ForegroundColor Yellow
} else {
    Write-Host "✅ DIAL_API_KEY is set" -ForegroundColor Green
}

# Check if Docker services are running
Write-Host "🐳 Checking Docker services..." -ForegroundColor Cyan
$dockerStatus = docker compose ps 2>&1
if ($dockerStatus -match "Up") {
    Write-Host "✅ Docker services are running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker services may not be running" -ForegroundColor Yellow
    Write-Host "   Starting Docker services..." -ForegroundColor Yellow
    docker compose up -d
    Write-Host "   Waiting 10 seconds for services to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# Check User Service health
Write-Host "🏥 Checking User Service health..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8041/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ User Service is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  User Service may not be ready yet" -ForegroundColor Yellow
    Write-Host "   Waiting additional 10 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# Run tests
Write-Host ""
Write-Host "🧪 Running test suite..." -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
python test.py

Write-Host ""
Write-Host "✅ Test suite completed!" -ForegroundColor Green

