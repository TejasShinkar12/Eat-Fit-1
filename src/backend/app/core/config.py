from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    PostgresDsn,
    field_validator,
    constr,
    Field,
    model_validator,
    AnyHttpUrl,
)


class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "PantryFit"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Environment
    ENVIRONMENT: str = Field("dev", description="Environment name (dev, prod, etc.)")

    # Database
    DATABASE_URL: PostgresDsn

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = Field(
        "HS256", pattern="^(HS256|HS384|HS512|RS256|RS384|RS512)$"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, gt=0)

    # Password Settings
    PASSWORD_MIN_LENGTH: int = Field(6, gt=0)
    PASSWORD_MAX_LENGTH: int = Field(18, gt=0)

    @model_validator(mode="after")
    def validate_password_lengths(self) -> "Settings":
        if self.PASSWORD_MIN_LENGTH > self.PASSWORD_MAX_LENGTH:
            raise ValueError(
                "minimum password length cannot be greater than maximum length"
            )
        return self

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(5, gt=0)

    @field_validator("RATE_LIMIT_PER_MINUTE")
    @classmethod
    def validate_rate_limit(cls, v: int) -> int:
        if v < 1:
            raise ValueError("rate limit must be positive")
        return v

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["*"])

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
