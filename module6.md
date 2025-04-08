# Flask API Testing Commands

## Testing Commands for module6.py Flask API

This document provides commands for testing the various endpoints of the Flask API implemented in module6.py. Commands are provided in both curl format (for Linux/Mac) and PowerShell format (for Windows).

## PowerShell Commands

### 1. Test the models endpoint (GET)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/models" -Method GET

# Using curl alias
curl -Uri "http://localhost:5000/api/models" -Method GET
```

### 2. Test the memory types endpoint (GET)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/memory-types" -Method GET

# Using curl alias
curl -Uri "http://localhost:5000/api/memory-types" -Method GET
```

### 3. Test the parameters endpoint (GET)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/parameters" -Method GET

# Using curl alias
curl -Uri "http://localhost:5000/api/parameters" -Method GET
```

### 4. Test the chat endpoint (POST)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/chat" `
                 -Method POST `
                 -Headers @{"Content-Type"="application/json"} `
                 -Body '{"message": "Hello, how are you?", "model": "llama3-8b-8192"}'

# Using curl alias
curl -Uri "http://localhost:5000/api/chat" `
     -Method POST `
     -Headers @{"Content-Type"="application/json"} `
     -Body '{"message": "Hello, how are you?", "model": "llama3-8b-8192"}'
```

### 5. Test the clear conversation endpoint (POST)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/clear" `
                 -Method POST `
                 -Headers @{"Content-Type"="application/json"} `
                 -Body '{"session_id": "test-session"}'

# Using curl alias
curl -Uri "http://localhost:5000/api/clear" `
     -Method POST `
     -Headers @{"Content-Type"="application/json"} `
     -Body '{"session_id": "test-session"}'
```

### 6. Test the sessions endpoint (GET)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/sessions" -Method GET

# Using curl alias
curl -Uri "http://localhost:5000/api/sessions" -Method GET
```

### 7. Check if server is running
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/" -Method GET

# Using curl alias
curl -Uri "http://localhost:5000/" -Method GET
```

## Linux/Mac Curl Commands

### 1. Test the models endpoint (GET)
```bash
curl http://localhost:5000/api/models
```

### 2. Test the memory types endpoint (GET)
```bash
curl http://localhost:5000/api/memory-types
```

### 3. Test the parameters endpoint (GET)
```bash
curl http://localhost:5000/api/parameters
```

### 4. Test the chat endpoint (POST)
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "model": "llama3-8b-8192"}'
```

### 5. Test the clear conversation endpoint (POST)
```bash
curl -X POST http://localhost:5000/api/clear \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session"}'
```

### 6. Test the sessions endpoint (GET)
```bash
curl http://localhost:5000/api/sessions
```

### 7. Check if server is running
```bash
curl http://localhost:5000/
```

## Python Script for Testing

You can also use this Python script to test the API endpoints:

```python
import requests

# Base URL for the API
base_url = "http://localhost:5000"

# Test models endpoint
def test_models():
    response = requests.get(f"{base_url}/api/models")
    print("Models API Response:", response.status_code)
    print(response.json())

# Test chat endpoint
def test_chat(message="Hello, how are you?", model="llama3-8b-8192"):
    response = requests.post(
        f"{base_url}/api/chat",
        json={"message": message, "model": model}
    )
    print("Chat API Response:", response.status_code)
    print(response.json())

# Test clear conversation endpoint
def test_clear(session_id="test-session"):
    response = requests.post(
        f"{base_url}/api/clear",
        json={"session_id": session_id}
    )
    print("Clear API Response:", response.status_code)
    print(response.json())

# Run the tests
test_models()
test_chat()
test_clear()
```

## Troubleshooting

If you receive a 404 "URL not found" error, check:
1. The Flask server is running
2. You're using the correct URL path
3. You're using the correct HTTP method (GET/POST)
4. The API_URL in your client code (module7.py) matches the server address