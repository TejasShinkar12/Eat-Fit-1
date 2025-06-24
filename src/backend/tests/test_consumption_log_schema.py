import uuid
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.consumption_log import ConsumptionLogCreate, ConsumptionLogRead, ConsumptionLogUpdate

def test_consumption_log_create_valid():
    """Test valid ConsumptionLogCreate serialization/deserialization."""
    data = {
        "inventory_item_id": str(uuid.uuid4()),
        "item_name": "Greek Yogurt",
        "quantity_consumed": 1.0,
        "calories_consumed": 120.0,
        "protein_consumed_g": 10.0,
        "carbs_consumed_g": 15.0,
        "fats_consumed_g": 2.0,
    }
    schema = ConsumptionLogCreate(**data)
    assert schema.item_name == "Greek Yogurt"
    assert schema.quantity_consumed == 1.0


def test_consumption_log_create_missing_required():
    """Test missing required fields raises ValidationError."""
    with pytest.raises(ValidationError):
        ConsumptionLogCreate(item_name="Test")
    with pytest.raises(ValidationError):
        ConsumptionLogCreate(quantity_consumed=1.0)


def test_consumption_log_create_negative_values():
    """Test negative nutrition values raise ValidationError."""
    data = {
        "item_name": "Test",
        "quantity_consumed": -1.0,
        "calories_consumed": 120.0,
        "protein_consumed_g": 10.0,
        "carbs_consumed_g": 15.0,
        "fats_consumed_g": 2.0,
    }
    with pytest.raises(ValidationError):
        ConsumptionLogCreate(**data)
    data["quantity_consumed"] = 1.0
    data["calories_consumed"] = -10.0
    with pytest.raises(ValidationError):
        ConsumptionLogCreate(**data)


def test_consumption_log_read_security():
    """Test ConsumptionLogRead does not leak user_id or internal fields."""
    data = {
        "id": uuid.uuid4(),
        "inventory_item_id": uuid.uuid4(),
        "item_name": "Greek Yogurt",
        "quantity_consumed": 1.0,
        "calories_consumed": 120.0,
        "protein_consumed_g": 10.0,
        "carbs_consumed_g": 15.0,
        "fats_consumed_g": 2.0,
        "consumed_at": datetime.utcnow(),
    }
    schema = ConsumptionLogRead(**data)
    assert not hasattr(schema, "user_id")


def test_consumption_log_update_partial():
    """Test ConsumptionLogUpdate allows partial updates."""
    schema = ConsumptionLogUpdate(quantity_consumed=2.0)
    assert schema.quantity_consumed == 2.0
    assert schema.item_name is None


def test_consumption_log_update_extra_fields():
    """Test ConsumptionLogUpdate ignores extra fields (Pydantic v2 default)."""
    schema = ConsumptionLogUpdate(quantity_consumed=2.0, extra_field=123)
    assert schema.quantity_consumed == 2.0
    assert not hasattr(schema, "extra_field") 