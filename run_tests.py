#!/usr/bin/env python3
"""
Launcher script for test.py
Handles environment setup and runs the test suite
"""
import os
import sys
import subprocess
from pathlib import Path

def check_virtual_env():
    """Check if virtual environment exists, create if not"""
    venv_path = Path(__file__).parent / ".venv"
    if not venv_path.exists():
        print("⚠️  Virtual environment not found. Creating...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✅ Virtual environment created")
    return venv_path

def install_dependencies():
    """Install project dependencies"""
    print("📥 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("✅ Dependencies installed")

def check_docker_services():
    """Check if Docker services are running"""
    print("🐳 Checking Docker services...")
    try:
        result = subprocess.run(
            ["docker", "compose", "ps"],
            capture_output=True,
            text=True,
            check=True
        )
        if "Up" in result.stdout:
            print("✅ Docker services are running")
            return True
        else:
            print("⚠️  Docker services may not be running")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Docker not available or services not running")
        return False

def start_docker_services():
    """Start Docker services"""
    print("🚀 Starting Docker services...")
    try:
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
        print("⏳ Waiting 10 seconds for services to initialize...")
        import time
        time.sleep(10)
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to start Docker services")
        return False

def check_user_service():
    """Check if User Service is healthy"""
    print("🏥 Checking User Service health...")
    try:
        import requests
        response = requests.get("http://localhost:8041/health", timeout=2)
        if response.status_code == 200:
            print("✅ User Service is healthy")
            return True
    except Exception:
        pass
    
    print("⚠️  User Service may not be ready yet")
    print("   Waiting additional 10 seconds...")
    import time
    time.sleep(10)
    return False

def main():
    """Main launcher function"""
    print("🚀 Launching AI DIAL Simple Agent Test Suite")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Check virtual environment
    venv_path = check_virtual_env()
    
    # Determine Python executable (use venv if available)
    if venv_path.exists():
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        if python_exe.exists():
            python_cmd = str(python_exe)
        else:
            python_cmd = sys.executable
    else:
        python_cmd = sys.executable
    
    # Install dependencies
    install_dependencies()
    
    # Check DIAL_API_KEY
    if not os.getenv("DIAL_API_KEY"):
        print("⚠️  DIAL_API_KEY not set. Using default from test.py")
        print("   To set: export DIAL_API_KEY='your-key-here'")
    else:
        print("✅ DIAL_API_KEY is set")
    
    # Check Docker services
    if not check_docker_services():
        if input("Start Docker services? (y/n): ").lower() == 'y':
            if not start_docker_services():
                print("❌ Cannot proceed without Docker services")
                sys.exit(1)
        else:
            print("⚠️  Proceeding without Docker services (tests may fail)")
    
    # Check User Service
    check_user_service()
    
    # Run tests
    print("\n🧪 Running test suite...")
    print("=" * 50)
    
    try:
        subprocess.run([python_cmd, "test.py"], check=True)
        print("\n✅ Test suite completed!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test suite failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Test suite interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main()

