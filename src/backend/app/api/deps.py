from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.auth_service import JWTService
from app.core.config import Settings
from app.db import SessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.user_service import get_user_by_email

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_db() -> Generator:
    """
    Database dependency that provides a session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current user from a JWT token.

    Args:
        db: The database session.
        token: The JWT token from the Authorization header.

    Returns:
        The authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    token_payload: Optional[TokenPayload] = JWTService.verify_access_token(token)
    if not token_payload or not token_payload.sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_email(db, email=token_payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user 