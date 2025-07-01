import pytest
from app.auth.auth_service import JWTService

def pytest_configure():
    # Optionally, set up any global test config here
    pass

@pytest.fixture
def auth_header_for_user():
    def _make(user):
        token = JWTService.create_access_token({"sub": str(user.email)})
        return {"Authorization": f"Bearer {token}"}
    return _make 