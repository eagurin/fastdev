# FastDEV Usage Examples

This document shows how to use FastDEV from an AI agent conversation.

## Starting a server

```python
# AI Agent command
fastdev.ensure_running("my-api", path="./examples", mode="dev")

# FastDEV response
{
  "status": "started",
  "server": {
    "name": "my-api",
    "port": 8000,
    "mode": "dev",
    "status": "running",
    "url": "http://localhost:8000",
    "docs_url": "http://localhost:8000/docs"
  },
  "message": "Server 'my-api' started on port 8000"
}
```

## Checking server status

```python
# AI Agent command
fastdev.health_check("my-api")

# FastDEV response
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "system": {
    "cpu_percent": 15.2,
    "memory": {
      "percent": 45.3
    }
  },
  "checks": {
    "server_running": true,
    "port_accessible": true,
    "memory_ok": true,
    "cpu_ok": true
  },
  "recommendations": []
}
```

## Getting logs

```python
# AI Agent command
fastdev.get_logs("my-api", tail=10)

# FastDEV response
[
  "INFO:     Started server process [12345]",
  "INFO:     Waiting for application startup.",
  "INFO:     Application startup complete.",
  "INFO:     Uvicorn running on http://0.0.0.0:8000",
  "INFO:     127.0.0.1:52341 - \"GET / HTTP/1.1\" 200 OK",
  "INFO:     127.0.0.1:52342 - \"GET /docs HTTP/1.1\" 200 OK"
]
```

## Running code analysis

```python
# AI Agent command
fastdev.analyze_code("./examples")

# FastDEV response
{
  "path": "./examples",
  "issues": {
    "critical": [],
    "warnings": [
      {
        "severity": "warning",
        "message": "Missing type annotation",
        "tool": "mypy",
        "file": "example_app.py",
        "line": 45
      }
    ],
    "style": [
      {
        "severity": "style",
        "message": "Imports need sorting",
        "tool": "isort"
      }
    ]
  },
  "auto_fixable": 2,
  "score": 9.2,
  "summary": {
    "total_issues": 3,
    "tools_run": 7,
    "tools_failed": 0
  }
}
```

## Diagnosing crashes

```python
# AI Agent command
fastdev.diagnose_crash("my-api")

# FastDEV response
{
  "error": "ModuleNotFoundError: No module named 'httpx'",
  "solution": "Run: pip install httpx",
  "context": "The module 'httpx' is imported but not installed",
  "similar_issues": ["#45", "#89"],
  "crashed_at": "2024-01-15T10:25:30",
  "file": "main.py",
  "line": 5
}
```

## Running tests

```python
# AI Agent command
fastdev.run_tests("my-api", watch=True)

# FastDEV response
{
  "status": "success",
  "tests_run": 15,
  "passed": 14,
  "failed": 1,
  "skipped": 0,
  "coverage": 87.5,
  "failed_tests": [
    {
      "name": "test_create_item_invalid_price",
      "error": "AssertionError: Expected 400, got 422"
    }
  ]
}
```

## Common Patterns

### Development workflow

1. Ensure server is running
2. Make code changes
3. Server auto-reloads (no action needed)
4. Run tests to verify
5. Check logs if issues

### Production deployment

1. Run code analysis with fix
2. Run all tests
3. Start server in prod mode
4. Monitor health metrics

### Debugging workflow

1. Check if server is running
2. Get recent logs
3. If crashed, diagnose crash
4. Fix issue based on diagnosis
5. Restart server if needed
