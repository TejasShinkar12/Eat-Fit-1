import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Inventory, ConsumptionLog, User
from app.db import SessionLocal
from datetime import datetime, timedelta

client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def seed_inventory(db):
    # Clear tables
    db.query(ConsumptionLog).delete()
    db.query(Inventory).delete()
    db.query(User).delete()
    db.commit()
    # Create a test user
    test_user = User(
        id=uuid.uuid4(),
        email="testuser@example.com",
        hashed_password="fakehashedpassword",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    # Add inventory items for the test user
    items = [
        Inventory(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name=f"Item {i}",
            quantity=10 + i,
            calories_per_serving=100 + i,
            protein_g_per_serving=5 + i,
            carbs_g_per_serving=10 + i,
            fats_g_per_serving=2 + i,
            serving_size_unit="g",
            expiry_date=datetime.utcnow().date() + timedelta(days=30),
            source="manual",
            added_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        for i in range(15)
    ]
    db.add_all(items)
    db.commit()
    return items


@pytest.fixture(scope="function")
def seed_inventory_with_logs(db, seed_inventory):
    # Add logs to the first inventory item
    inv = seed_inventory[0]
    logs = [
        ConsumptionLog(
            id=uuid.uuid4(),
            user_id=inv.user_id,
            inventory_item_id=inv.id,
            item_name=inv.name,
            quantity_consumed=1.0,
            calories_consumed=120.0,
            protein_consumed_g=10.0,
            carbs_consumed_g=15.0,
            fats_consumed_g=2.0,
            consumed_at=datetime.utcnow(),
        )
        for _ in range(3)
    ]
    db.add_all(logs)
    db.commit()
    return inv, logs


def test_paginated_list_endpoint(seed_inventory):
    # Default page 1, size 10
    resp = client.get("/api/v1/inventory/inventory")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 15
    assert data["page"] == 1
    assert data["size"] == 10
    assert len(data["items"]) == 10
    # Page 2
    resp2 = client.get("/api/v1/inventory/inventory?page=2&per_page=5")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["page"] == 2
    assert data2["size"] == 5
    assert len(data2["items"]) == 5


def test_detail_endpoint_without_logs(seed_inventory):
    inv = seed_inventory[0]
    resp = client.get(f"/api/v1/inventory/inventory/{inv.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(inv.id)
    assert data["name"] == inv.name
    assert data["consumption_logs"] == []


def test_detail_endpoint_with_logs(seed_inventory_with_logs):
    inv, logs = seed_inventory_with_logs
    resp = client.get(f"/api/v1/inventory/inventory/{inv.id}?include=consumption_logs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(inv.id)
    assert isinstance(data["consumption_logs"], list)
    assert len(data["consumption_logs"]) == 3
    log_ids = {log["id"] for log in data["consumption_logs"]}
    for log in logs:
        assert str(log.id) in log_ids


def test_empty_results(db):
    db.query(ConsumptionLog).delete()
    db.query(Inventory).delete()
    db.commit()
    resp = client.get("/api/v1/inventory/inventory")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_out_of_range_page(seed_inventory):
    resp = client.get("/api/v1/inventory/inventory?page=100&per_page=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []


def test_invalid_id(seed_inventory):
    resp = client.get(
        "/api/v1/inventory/inventory/00000000-0000-0000-0000-000000000000"
    )
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "Inventory item not found"


def test_create_inventory_success(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    payload = {
        "name": "Greek Yogurt",
        "quantity": 2.0,
        "calories_per_serving": 120.0,
        "protein_g_per_serving": 10.0,
        "carbs_g_per_serving": 15.0,
        "fats_g_per_serving": 2.0,
        "serving_size_unit": "g",
        "expiry_date": (datetime.utcnow().date() + timedelta(days=10)).isoformat(),
        "source": "manual"
    }
    headers = auth_header_for_user(test_user)
    resp = client.post("/api/v1/inventory/inventory/create", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["quantity"] == payload["quantity"]
    assert data["expiry_date"] == payload["expiry_date"]
    assert data["consumption_logs"] == []


def test_create_inventory_missing_required(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    payload = {"quantity": 2.0}
    headers = auth_header_for_user(test_user)
    resp = client.post("/api/v1/inventory/inventory/create", json=payload, headers=headers)
    assert resp.status_code == 422


def test_create_inventory_invalid_quantity(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    payload = {"name": "Greek Yogurt", "quantity": -5.0}
    headers = auth_header_for_user(test_user)
    resp = client.post("/api/v1/inventory/inventory/create", json=payload, headers=headers)
    assert resp.status_code == 422


def test_create_inventory_expiry_in_past(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    payload = {
        "name": "Greek Yogurt",
        "quantity": 2.0,
        "expiry_date": (datetime.utcnow().date() - timedelta(days=1)).isoformat()
    }
    headers = auth_header_for_user(test_user)
    resp = client.post("/api/v1/inventory/inventory/create", json=payload, headers=headers)
    assert resp.status_code == 422


def test_create_inventory_unauthorized():
    payload = {"name": "Greek Yogurt", "quantity": 2.0}
    resp = client.post("/api/v1/inventory/inventory/create", json=payload)
    assert resp.status_code == 401


def test_create_inventory_optional_fields(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    payload = {"name": "Apple", "quantity": 1.0}
    headers = auth_header_for_user(test_user)
    resp = client.post("/api/v1/inventory/inventory/create", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Apple"
    assert data["quantity"] == 1.0
    assert data.get("calories_per_serving") is None
