import pytest
from app.main import app
from app.core.auth import get_current_user

@pytest.fixture(autouse=True)
def override_auth():
    # Automatically override auth for all tests to simulate a logged-in USER
    # and to satisfy ownership checks.
    def mock_get_current_user():
        return {
            "id": "admin-1", # Make admin to bypass ownership
            "email": "admin@example.com",
            "role": "ADMIN"
        }
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()
