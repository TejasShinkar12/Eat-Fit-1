import pytest
from fastapi.testclient import TestClient
from fastapi import BackgroundTasks
from unittest.mock import MagicMock

from app.main import app
from app.models.user import User
from app.schemas.inventory import InventoryCreate
from app.services.inventory_service import create_inventory_item

client = TestClient(app)


@pytest.fixture
def mock_background_tasks(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(BackgroundTasks, "add_task", mock)
    return mock


def test_generate_recipes_from_inventory(
    db,
    mock_background_tasks,
    auth_header_for_user,
):
    # 1. Create a user and inventory
    user = User(email="test@example.com", hashed_password="password")
    db.add(user)
    db.commit()

    inventory_item = InventoryCreate(
        name="Oats",
        quantity=1,
        serving_size_unit="cup",
        calories_per_serving=150,
        protein_g_per_serving=5,
        carbs_g_per_serving=27,
        fats_g_per_serving=3,
        source="manual",
    )
    create_inventory_item(db, user, inventory_item)

    # 2. Call the new endpoint
    response = client.post(
        "/api/v1/recipe/generate-from-inventory",
        headers=auth_header_for_user(user),
    )

    # 3. Assert the response
    assert response.status_code == 202

    # 4. Assert that a background task was created
    mock_background_tasks.add_task.assert_called_once()
