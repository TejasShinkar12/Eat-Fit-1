from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.openapi.models import Response as OpenAPIResponse
from sqlalchemy.orm import Session
import app.api.deps as deps
import app.schemas.user as user_schema
import app.services.user_service as user_service
import app.models.user as user_model

router = APIRouter()

@router.post(
    "/",
    response_model=user_schema.User,
    responses={
        400: {
            "description": "User already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "The user with this username already exists in the system."}
                }
            }
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    }
)
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