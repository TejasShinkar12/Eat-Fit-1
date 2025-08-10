import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_get_recipes_success():
    response = client.post(
        "/api/v1/recipe/recipes", json=["chicken", "rice", "broccoli"]
    )
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "ingredients" in data
    assert "directions" in data
    assert isinstance(data["title"], str)
    assert isinstance(data["ingredients"], list)
    assert isinstance(data["directions"], str)


def test_get_recipes_empty_ingredients():
    response = client.post("/api/v1/recipe/recipes", json=[])
    assert response.status_code == 400
    assert response.json() == {"detail": "Ingredients list cannot be empty."}


@pytest.mark.parametrize("model_path", ["invalid/path"])
def test_get_recipes_model_load_failure(monkeypatch, model_path):
    monkeypatch.setattr(settings, "RECIPE_MODEL_PATH", model_path)
    response = client.post(
        "/api/v1/recipe/recipes", json=["chicken", "rice", "broccoli"]
    )
    assert response.status_code == 500
    assert "Failed to load recipe generation model" in response.json()["detail"]
