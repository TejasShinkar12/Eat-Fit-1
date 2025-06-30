import pytest
from pydantic import ValidationError
from app.core.config import Settings
import os


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    yield
    # Clean up
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("JWT_SECRET_KEY", None)


def test_settings_default_values():
    """Test that default values are set correctly"""
    settings = Settings()
    assert settings.PROJECT_NAME == "FitEats"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.PASSWORD_MIN_LENGTH == 6
    assert settings.PASSWORD_MAX_LENGTH == 18
    assert settings.RATE_LIMIT_PER_MINUTE == 5


def test_settings_env_override(monkeypatch):
    """Test that environment variables override default values"""
    test_db_url = "postgresql://test2:test2@localhost:5432/test_db2"
    monkeypatch.setenv("PROJECT_NAME", "TestApp")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-2")
    monkeypatch.setenv("DATABASE_URL", test_db_url)

    settings = Settings()
    assert settings.PROJECT_NAME == "TestApp"
    assert settings.JWT_SECRET_KEY == "test-secret-key-2"
    assert str(settings.DATABASE_URL) == test_db_url


def test_required_settings_missing(monkeypatch):
    """Test that required settings raise error when missing"""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_invalid_settings_values():
    """Test that invalid values raise validation error"""
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
            JWT_SECRET_KEY="test-key",
            PASSWORD_MIN_LENGTH=20,  # Max is 18
        )

    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
            JWT_SECRET_KEY="test-key",
            RATE_LIMIT_PER_MINUTE=0,
        )


def test_cors_settings():
    """Test CORS settings"""
    settings = Settings()
    assert settings.BACKEND_CORS_ORIGINS == ["*"]  # Allow all origins in development


def test_password_length_validation():
    """Test password length validation edge cases"""
    # Test minimum length at boundary
    settings = Settings(
        DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
        JWT_SECRET_KEY="test-key",
        PASSWORD_MIN_LENGTH=6,
    )
    assert settings.PASSWORD_MIN_LENGTH == 6

    # Test maximum length at boundary
    settings = Settings(
        DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
        JWT_SECRET_KEY="test-key",
        PASSWORD_MAX_LENGTH=18,
    )
    assert settings.PASSWORD_MAX_LENGTH == 18

    # Test invalid: min > max
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
            JWT_SECRET_KEY="test-key",
            PASSWORD_MIN_LENGTH=10,
            PASSWORD_MAX_LENGTH=8,
        )

    # Test invalid: negative values
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
            JWT_SECRET_KEY="test-key",
            PASSWORD_MIN_LENGTH=-1,
        )


def test_jwt_settings():
    """Test JWT settings validation"""
    # Test valid algorithm
    settings = Settings(
        DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
        JWT_SECRET_KEY="test-key",
        JWT_ALGORITHM="HS256",
    )
    assert settings.JWT_ALGORITHM == "HS256"

    # Test valid token expiration
    settings = Settings(
        DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
        JWT_SECRET_KEY="test-key",
        ACCESS_TOKEN_EXPIRE_MINUTES=60,
    )
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60

    # Test invalid token expiration
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
            JWT_SECRET_KEY="test-key",
            ACCESS_TOKEN_EXPIRE_MINUTES=-30,
        )


def test_rate_limit_validation():
    """Test rate limit validation"""
    # Test valid rate limit
    settings = Settings(
        DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
        JWT_SECRET_KEY="test-key",
        RATE_LIMIT_PER_MINUTE=10,
    )
    assert settings.RATE_LIMIT_PER_MINUTE == 10

    # Test zero rate limit
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
            JWT_SECRET_KEY="test-key",
            RATE_LIMIT_PER_MINUTE=0,
        )

    # Test negative rate limit
    with pytest.raises(ValidationError):
        Settings(
            DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
            JWT_SECRET_KEY="test-key",
            RATE_LIMIT_PER_MINUTE=-5,
        )


def test_debug_mode():
    """Test debug mode settings"""
    # Test default debug mode
    settings = Settings()
    assert settings.DEBUG is True

    # Test debug mode override
    settings = Settings(
        DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
        JWT_SECRET_KEY="test-key",
        DEBUG=False,
    )
    assert settings.DEBUG is False
