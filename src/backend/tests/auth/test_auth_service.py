import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from app.auth.auth_service import JWTService
from app.core.config import Settings

settings = Settings()


def test_create_access_token():
    """
    Tests the creation of a valid access token.
    """
    user_id = "test_user_123"
    data = {"sub": user_id}

    token = JWTService.create_access_token(data)

    assert isinstance(token, str)

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["sub"] == user_id

        # Check if 'exp' claim exists and is a future time
        assert "exp" in payload
        expire_time = datetime.utcfromtimestamp(payload["exp"])
        assert expire_time > datetime.utcnow()

    except JWTError as e:
        pytest.fail(f"Token decoding failed: {e}")


def test_create_access_token_with_custom_expiry():
    """
    Tests creating a token with a custom expiration time.
    """
    user_id = "test_user_456"
    custom_delta = timedelta(minutes=15)
    data = {"sub": user_id}

    token = JWTService.create_access_token(data, expires_delta=custom_delta)

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        expire_time = datetime.utcfromtimestamp(payload["exp"])
        expected_expire_time_approx = datetime.utcnow() + custom_delta

        # Allow a small tolerance for the time difference
        time_diff = abs(expire_time - expected_expire_time_approx)
        assert time_diff < timedelta(seconds=5)

    except JWTError as e:
        pytest.fail(f"Token decoding failed with custom expiry: {e}")


def test_invalid_payload():
    """
    Tests that a ValueError is raised for an invalid payload.
    """
    # Payload with a non-string 'sub' field, which should fail validation
    invalid_data = {"sub": 12345}

    with pytest.raises(ValueError, match="Invalid token payload"):
        JWTService.create_access_token(invalid_data)


def test_create_access_token_with_extra_claims():
    """
    Tests creating a token with additional claims in the payload.
    """
    user_id = "test_user_789"
    extra_data = {"role": "admin", "permissions": ["read", "write"]}
    data = {"sub": user_id, **extra_data}

    token = JWTService.create_access_token(data)

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["sub"] == user_id
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]
    except JWTError as e:
        pytest.fail(f"Token decoding failed with extra claims: {e}")


def test_create_token_with_negative_expiry():
    """
    Tests that a token created with a negative expiry raises an ExpiredSignatureError.
    """
    user_id = "test_user_000"
    # Create a token that is already expired
    expired_delta = timedelta(minutes=-5)
    data = {"sub": user_id}

    token = JWTService.create_access_token(data, expires_delta=expired_delta)

    with pytest.raises(ExpiredSignatureError, match="Signature has expired."):
        jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
