import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Inventory, ConsumptionLog, User
from app.db import SessionLocal
from datetime import datetime, timedelta
from app.schemas.inventory import InventoryRead

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
        "source": "manual",
    }
    headers = auth_header_for_user(test_user)
    resp = client.post(
        "/api/v1/inventory/inventory/create", json=payload, headers=headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["quantity"] == payload["quantity"]
    assert data["expiry_date"] == payload["expiry_date"]
    assert data["consumption_logs"] == []


def test_create_inventory_missing_required(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    # Omit required fields one by one
    base_payload = {
        "name": "Greek Yogurt",
        "quantity": 2.0,
        "calories_per_serving": 120.0,
        "protein_g_per_serving": 10.0,
        "carbs_g_per_serving": 15.0,
        "fats_g_per_serving": 2.0,
        "serving_size_unit": "g",
        "source": "manual",
    }
    required_fields = [
        "name",
        "quantity",
        "calories_per_serving",
        "protein_g_per_serving",
        "carbs_g_per_serving",
        "fats_g_per_serving",
        "serving_size_unit",
        "source",
    ]
    headers = auth_header_for_user(test_user)
    for field in required_fields:
        payload = base_payload.copy()
        del payload[field]
        resp = client.post(
            "/api/v1/inventory/inventory/create", json=payload, headers=headers
        )
        assert resp.status_code == 422


def test_create_inventory_invalid_quantity(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    payload = {"name": "Greek Yogurt", "quantity": -5.0}
    headers = auth_header_for_user(test_user)
    resp = client.post(
        "/api/v1/inventory/inventory/create", json=payload, headers=headers
    )
    assert resp.status_code == 422


def test_create_inventory_expiry_in_past(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    payload = {
        "name": "Greek Yogurt",
        "quantity": 2.0,
        "expiry_date": (datetime.utcnow().date() - timedelta(days=1)).isoformat(),
    }
    headers = auth_header_for_user(test_user)
    resp = client.post(
        "/api/v1/inventory/inventory/create", json=payload, headers=headers
    )
    assert resp.status_code == 422


def test_create_inventory_unauthorized():
    payload = {"name": "Greek Yogurt", "quantity": 2.0}
    resp = client.post("/api/v1/inventory/inventory/create", json=payload)
    assert resp.status_code == 401


def test_create_inventory_optional_fields(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    # Only expiry_date is optional
    payload = {
        "name": "Apple",
        "quantity": 1.0,
        "calories_per_serving": 52.0,
        "protein_g_per_serving": 0.3,
        "carbs_g_per_serving": 14.0,
        "fats_g_per_serving": 0.2,
        "serving_size_unit": "g",
        "source": "manual",
    }
    headers = auth_header_for_user(test_user)
    resp = client.post(
        "/api/v1/inventory/inventory/create", json=payload, headers=headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Apple"
    assert data["quantity"] == 1.0
    assert data.get("expiry_date") is None


def test_patch_inventory_success_partial(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    item = db.query(Inventory).filter(Inventory.user_id == test_user.id).first()
    payload = {"quantity": 99.0}
    headers = auth_header_for_user(test_user)
    resp = client.patch(
        f"/api/v1/inventory/inventory/{item.id}", json=payload, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(item.id)
    assert data["quantity"] == 99.0
    # unchanged fields
    assert data["name"] == item.name
    assert data["consumption_logs"] == []


def test_patch_inventory_success_full(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    item = db.query(Inventory).filter(Inventory.user_id == test_user.id).first()
    payload = {
        "name": "Updated Name",
        "quantity": 5.0,
        "calories_per_serving": 50.0,
        "protein_g_per_serving": 5.0,
        "carbs_g_per_serving": 10.0,
        "fats_g_per_serving": 2.0,
        "serving_size_unit": "ml",
        "expiry_date": (datetime.utcnow().date() + timedelta(days=5)).isoformat(),
        "source": "manual",
    }
    headers = auth_header_for_user(test_user)
    resp = client.patch(
        f"/api/v1/inventory/inventory/{item.id}", json=payload, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    for k, v in payload.items():
        if k == "expiry_date":
            assert data[k] == payload[k]
        else:
            assert data[k] == v


def test_patch_inventory_not_found(db, auth_header_for_user):
    test_user = db.query(User).first()
    fake_id = uuid.uuid4()
    payload = {"quantity": 10.0}
    headers = auth_header_for_user(test_user)
    resp = client.patch(
        f"/api/v1/inventory/inventory/{fake_id}", json=payload, headers=headers
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Inventory item not found"


def test_patch_inventory_forbidden(db, seed_inventory):
    # Create a second user
    user2 = User(
        id=uuid.uuid4(),
        email="otheruser@example.com",
        hashed_password="fakehashedpassword",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user2)
    db.commit()
    db.refresh(user2)
    # Get an item owned by the first user
    item = db.query(Inventory).first()
    # Auth header for user2
    from app.auth.auth_service import JWTService

    headers = {
        "Authorization": f"Bearer {JWTService.create_access_token({'sub': user2.email})}"
    }
    payload = {"quantity": 10.0}
    resp = client.patch(
        f"/api/v1/inventory/inventory/{item.id}", json=payload, headers=headers
    )
    # Should return 404 for security (not revealing existence)
    assert resp.status_code == 404


def test_patch_inventory_invalid_data(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    item = db.query(Inventory).filter(Inventory.user_id == test_user.id).first()
    # Negative quantity
    payload = {"quantity": -5.0}
    headers = auth_header_for_user(test_user)
    resp = client.patch(
        f"/api/v1/inventory/inventory/{item.id}", json=payload, headers=headers
    )
    assert resp.status_code == 422
    # Expiry in past
    payload = {
        "expiry_date": (datetime.utcnow().date() - timedelta(days=1)).isoformat()
    }
    resp = client.patch(
        f"/api/v1/inventory/inventory/{item.id}", json=payload, headers=headers
    )
    assert resp.status_code == 422


def test_patch_inventory_no_fields(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    item = db.query(Inventory).filter(Inventory.user_id == test_user.id).first()
    headers = auth_header_for_user(test_user)
    resp = client.patch(
        f"/api/v1/inventory/inventory/{item.id}", json={}, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    # All fields should remain unchanged
    assert data["id"] == str(item.id)
    assert data["name"] == item.name
    assert data["quantity"] == item.quantity


def test_patch_inventory_immutable_fields(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    item = db.query(Inventory).filter(Inventory.user_id == test_user.id).first()
    payload = {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "added_at": "2000-01-01T00:00:00Z",
        "updated_at": "2000-01-01T00:00:00Z",
        "quantity": 42.0,
    }
    headers = auth_header_for_user(test_user)
    resp = client.patch(
        f"/api/v1/inventory/inventory/{item.id}", json=payload, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    # Immutable fields should not change
    assert data["id"] == str(item.id)
    assert data["quantity"] == 42.0
    # user_id, added_at, updated_at should remain as before
    db.refresh(item)
    assert item.user_id == test_user.id


def test_patch_inventory_only_provided_fields_change(
    db, seed_inventory, auth_header_for_user
):
    test_user = db.query(User).first()
    item = db.query(Inventory).filter(Inventory.user_id == test_user.id).first()
    old_name = item.name
    old_quantity = item.quantity
    payload = {"quantity": old_quantity + 1}
    headers = auth_header_for_user(test_user)
    resp = client.patch(
        f"/api/v1/inventory/inventory/{item.id}", json=payload, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["quantity"] == old_quantity + 1
    assert data["name"] == old_name


def test_patch_inventory_updated_at_changes(db, seed_inventory, auth_header_for_user):
    test_user = db.query(User).first()
    item = db.query(Inventory).filter(Inventory.user_id == test_user.id).first()
    old_updated_at = item.updated_at
    payload = {"quantity": item.quantity + 1}
    headers = auth_header_for_user(test_user)
    resp = client.patch(
        f"/api/v1/inventory/inventory/{item.id}", json=payload, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    # updated_at should be newer
    new_updated_at = datetime.fromisoformat(data["updated_at"])
    assert new_updated_at >= old_updated_at
