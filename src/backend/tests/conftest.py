import os
from dotenv import load_dotenv

load_dotenv()

if os.environ.get("DATABASE_URL_TEST"):
    os.environ["DATABASE_URL"] = os.environ["DATABASE_URL_TEST"]

import pytest
from app.db import engine, SessionLocal
from app.auth.auth_service import JWTService
import sqlalchemy


@pytest.fixture(scope="function")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_header_for_user():
    def _make(user):
        token = JWTService.create_access_token({"sub": str(user.email)})
        return {"Authorization": f"Bearer {token}"}

    return _make


@pytest.fixture(autouse=True)
def clean_tables(db):
    meta = sqlalchemy.MetaData()
    meta.reflect(bind=db.get_bind())
    for table in reversed(meta.sorted_tables):
        db.execute(table.delete())
    db.commit()
