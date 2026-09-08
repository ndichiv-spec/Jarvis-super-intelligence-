"""Simple test script to check backend imports"""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Change to project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Test 1: Import config...")
from core.config import settings

print(f"   Config loaded: {settings.APP_NAME}")

print("Test 2: Import main...")
import api.main as main

print("   Main imported OK")

print("Test 3: Create app...")
app = main.create_application()
print(f"   App created: {app.title}")

print("Test 4: Test health endpoint...")
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.get("/api/v1/health/status")
print(f"   Response: {response.status_code} - {response.json()}")

print("\nAll tests passed!")
