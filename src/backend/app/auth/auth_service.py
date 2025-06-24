from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from pydantic import ValidationError

from app.core.config import Settings
from app.schemas.token import TokenPayload

settings = Settings()


class JWTService:
    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Creates a new access token.

        Args:
            data: The data to be encoded in the token.
            expires_delta: The expiration time for the token.

        Returns:
            The encoded JWT access token.
        """
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": int(expire.timestamp())})
        try:
            TokenPayload(**to_encode)
        except ValidationError as e:
            # Handle or log the validation error appropriately
            raise ValueError(f"Invalid token payload: {e}") from e

        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_access_token(token: str) -> Optional[TokenPayload]:
        """
        Verifies the access token.

        Args:
            token: The token to be verified.

        Returns:
            The token payload if the token is valid, otherwise None.
        """
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return TokenPayload(**payload)
        except (JWTError, ValidationError):
            return None
