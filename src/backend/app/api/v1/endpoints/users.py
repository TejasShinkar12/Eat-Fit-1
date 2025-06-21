from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import app.api.deps as deps
import app.schemas.user as user_schema
import app.services.user_service as user_service
import app.models.user as user_model

router = APIRouter()

@router.post("/", response_model=user_schema.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: user_schema.UserCreate,
):
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = user_service.create_user(db, user_in=user_in)
    return user


@router.get("/me", response_model=user_schema.User)
def read_users_me(
    current_user: user_model.User = Depends(deps.get_current_user),
):
    return current_user 