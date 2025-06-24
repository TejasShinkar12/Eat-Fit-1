from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT access token",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."},
    )
    token_type: str = Field(
        ..., description="Type of the token", json_schema_extra={"example": "bearer"}
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
                "token_type": "bearer",
            }
        }
    )


class TokenData(BaseModel):
    username: str | None = Field(
        None,
        description="Username associated with the token",
        json_schema_extra={"example": "johndoe"},
    )
    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    sub: Optional[str] = Field(
        None,
        description="Subject (user identifier)",
        json_schema_extra={"example": "user_id"},
    )
    exp: Optional[int] = Field(
        None,
        description="Expiration time (as UNIX timestamp)",
        json_schema_extra={"example": 1712345678},
    )

    model_config = ConfigDict(extra="allow")
