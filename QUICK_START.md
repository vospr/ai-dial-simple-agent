# Quick Start Guide - Running Tests

## 🚀 Quick Launch Options

### Option 1: Using Python Launcher (Recommended - Cross-platform)
```bash
# From project root
python run_tests.py
```

### Option 2: Using Shell Script (Linux/WSL)
```bash
# Make executable (first time only)
chmod +x run_tests.sh

# Run
./run_tests.sh
```

### Option 3: Using PowerShell Script (Windows)
```powershell
# Run from PowerShell
.\run_tests.ps1
```

### Option 4: Direct Python Execution
```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux/WSL
# OR
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Run tests
python test.py
```

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **Docker** running (for User Service)
3. **DIAL API Key** (optional - defaults to test key if not set)

## 🔧 Setup (First Time)

### 1. Create Virtual Environment
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment

**Linux/WSL:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set DIAL API Key (Optional)
```bash
# Linux/WSL
export DIAL_API_KEY='your-key-here'

# Windows PowerShell
$env:DIAL_API_KEY='your-key-here'
```

### 5. Start Docker Services
```bash
docker compose up -d
```

## 🧪 Running Tests

The test suite includes:
- ✅ Web Search Tool test
- ✅ Search Users by Name
- ✅ Create User (with web search)
- ✅ Search for created user
- ✅ Get User by ID
- ✅ Update User Information
- ✅ Search Users by Gender
- ✅ Complex Query - User Profile Enhancement

## 📝 Manual Testing

For interactive testing:
```bash
python task/app.py
```

## 🐛 Troubleshooting

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Docker Services Not Running
```bash
# Check status
docker compose ps

# Start services
docker compose up -d

# Check logs
docker compose logs
```

### User Service Not Responding
```bash
# Check health
curl http://localhost:8041/health

# Restart service
docker compose restart userservice
```

### DIAL API Key Issues
- Default key is used if not set
- To use custom key: `export DIAL_API_KEY='your-key'`
- Ensure you're connected to EPAM VPN for internal API access

## 📊 Expected Output

When tests run successfully, you should see:
- Test case titles with separators
- User queries
- Assistant responses
- Test summary with pass/fail counts
- Success rate percentage

