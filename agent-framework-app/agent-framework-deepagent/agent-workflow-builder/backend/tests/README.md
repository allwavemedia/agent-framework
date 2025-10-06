# Testing Guide

This directory contains tests for the Agent Workflow Builder backend.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── api/                     # API endpoint tests
│   ├── __init__.py
│   ├── test_agents.py      # Agent API tests
│   └── test_websocket.py   # WebSocket API tests
└── workflows/               # Workflow component tests
    ├── __init__.py
    └── test_workflow_validator.py  # Workflow validator tests
```

## Running Tests

### Install Dependencies

First, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/workflows/test_workflow_validator.py
```

### Run Specific Test Class

```bash
pytest tests/api/test_agents.py::TestAgentEndpoints
```

### Run Specific Test

```bash
pytest tests/api/test_agents.py::TestAgentEndpoints::test_create_agent
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

This will generate a coverage report in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Fast Tests (excluding slow tests)

```bash
pytest -m "not slow"
```

## Test Categories

Tests are marked with the following markers:

- `@pytest.mark.asyncio` - Async tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests

## Writing New Tests

### Test File Naming

- Test files must start with `test_` or end with `_test.py`
- Place API tests in `tests/api/`
- Place workflow tests in `tests/workflows/`
- Place service tests in `tests/services/` (create directory if needed)

### Test Class Naming

Test classes should start with `Test`:

```python
class TestAgentService:
    def test_create_agent(self):
        pass
```

### Test Function Naming

Test functions should start with `test_`:

```python
def test_agent_validation():
    pass
```

### Async Tests

For async tests, use the `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Using Fixtures

Fixtures are defined in `conftest.py` and can be used in tests:

```python
def test_with_database(session):
    # session fixture provides a test database session
    agent = Agent(name="Test")
    session.add(agent)
    session.commit()
```

### Using Test Client

For API endpoint tests, use the `client` fixture:

```python
def test_api_endpoint(client):
    response = client.get("/api/agents/")
    assert response.status_code == 200
```

## Test Coverage

We aim for high test coverage of critical functionality:

- **Required**: Core business logic (validators, services)
- **Required**: API endpoints
- **Recommended**: WebSocket functionality
- **Optional**: Utility functions

## Continuous Integration

Tests are automatically run in CI/CD pipeline on:

- Pull requests
- Commits to main branch
- Release tags

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running tests from the backend directory:

```bash
cd backend
pytest
```

### Database Errors

Tests use an in-memory SQLite database. If you encounter database errors, check that:

1. SQLModel is properly installed
2. Models are imported in conftest.py
3. Database is properly initialized in fixtures

### Async Test Errors

For async test errors, ensure:

1. Test function is marked with `@pytest.mark.asyncio`
2. pytest-asyncio is installed
3. Event loop is properly configured in conftest.py

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
