import uuid
import pytest
from datetime import datetime, date, timedelta
from pydantic import ValidationError
from app.schemas.inventory import InventoryCreate, InventoryRead, InventoryUpdate, InventoryInDB


def test_inventory_create_valid():
    """Test valid InventoryCreate serialization/deserialization."""
    data = {
        "name": "Greek Yogurt",
        "quantity": 2.0,
        "calories_per_serving": 120.0,
        "protein_g_per_serving": 10.0,
        "carbs_g_per_serving": 15.0,
        "fats_g_per_serving": 2.0,
        "serving_size_unit": "g",
        "expiry_date": (date.today() + timedelta(days=10)).isoformat(),
        "source": "manual"
    }
    schema = InventoryCreate(**data)
    assert schema.name == "Greek Yogurt"
    assert schema.quantity == 2.0
    assert schema.expiry_date > date.today()


def test_inventory_create_missing_required():
    """Test missing required fields raises ValidationError."""
    with pytest.raises(ValidationError):
        InventoryCreate(quantity=1.0)
    with pytest.raises(ValidationError):
        InventoryCreate(name="Test")


def test_inventory_create_negative_quantity():
    """Test negative quantity raises ValidationError."""
    data = {"name": "Test", "quantity": -1.0}
    with pytest.raises(ValidationError):
        InventoryCreate(**data)


def test_inventory_create_expiry_in_past():
    """Test expiry_date in the past raises ValidationError."""
    data = {"name": "Test", "quantity": 1.0, "expiry_date": (date.today() - timedelta(days=1)).isoformat()}
    with pytest.raises(ValidationError):
        InventoryCreate(**data)


def test_inventory_read_security():
    """Test InventoryRead does not leak user_id or internal fields."""
    data = {
        "id": uuid.uuid4(),
        "name": "Greek Yogurt",
        "quantity": 2.0,
        "calories_per_serving": 120.0,
        "protein_g_per_serving": 10.0,
        "carbs_g_per_serving": 15.0,
        "fats_g_per_serving": 2.0,
        "serving_size_unit": "g",
        "expiry_date": (date.today() + timedelta(days=10)),
        "source": "manual",
        "added_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    schema = InventoryRead(**data)
    assert not hasattr(schema, "user_id")


def test_inventory_update_partial():
    """Test InventoryUpdate allows partial updates."""
    schema = InventoryUpdate(quantity=5.0)
    assert schema.quantity == 5.0
    assert schema.name is None


def test_inventory_update_extra_fields():
    """Test InventoryUpdate ignores extra fields (Pydantic v2 default)."""
    schema = InventoryUpdate(quantity=5.0, extra_field=123)
    assert schema.quantity == 5.0
    assert not hasattr(schema, "extra_field") 