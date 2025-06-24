import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

class ConsumptionLogBase(BaseModel):
    """Shared fields for ConsumptionLog (not exposed directly)."""
    inventory_item_id: Optional[uuid.UUID] = Field(None, description="ID of the inventory item consumed (nullable)", json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"})
    item_name: str = Field(..., description="Snapshot of the item name at time of consumption", json_schema_extra={"example": "Greek Yogurt"})
    quantity_consumed: float = Field(..., description="Quantity consumed", json_schema_extra={"example": 1.0})
    calories_consumed: float = Field(..., description="Calories consumed", json_schema_extra={"example": 120.0})
    protein_consumed_g: float = Field(..., description="Protein consumed (g)", json_schema_extra={"example": 10.0})
    carbs_consumed_g: float = Field(..., description="Carbs consumed (g)", json_schema_extra={"example": 15.0})
    fats_consumed_g: float = Field(..., description="Fats consumed (g)", json_schema_extra={"example": 2.0})

    @field_validator('quantity_consumed', 'calories_consumed', 'protein_consumed_g', 'carbs_consumed_g', 'fats_consumed_g')
    @classmethod
    def non_negative(cls, v, info):
        if v < 0:
            raise ValueError(f'{info.field_name.replace("_", " ").capitalize()} must be non-negative')
        return v

class ConsumptionLogCreate(ConsumptionLogBase):
    """Fields required for creating a consumption log entry."""
    pass

class ConsumptionLogUpdate(BaseModel):
    """Fields for updating a consumption log entry (all optional)."""
    inventory_item_id: Optional[uuid.UUID] = Field(None, json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"})
    item_name: Optional[str] = Field(None, json_schema_extra={"example": "Greek Yogurt"})
    quantity_consumed: Optional[float] = Field(None, json_schema_extra={"example": 1.0})
    calories_consumed: Optional[float] = Field(None, json_schema_extra={"example": 120.0})
    protein_consumed_g: Optional[float] = Field(None, json_schema_extra={"example": 10.0})
    carbs_consumed_g: Optional[float] = Field(None, json_schema_extra={"example": 15.0})
    fats_consumed_g: Optional[float] = Field(None, json_schema_extra={"example": 2.0})

    @field_validator('quantity_consumed', 'calories_consumed', 'protein_consumed_g', 'carbs_consumed_g', 'fats_consumed_g')
    @classmethod
    def non_negative(cls, v, info):
        if v is not None and v < 0:
            raise ValueError(f'{info.field_name.replace("_", " ").capitalize()} must be non-negative')
        return v

class ConsumptionLogRead(ConsumptionLogBase):
    """Fields returned in API responses for consumption logs."""
    id: uuid.UUID = Field(..., json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"})
    consumed_at: datetime = Field(..., json_schema_extra={"example": "2024-06-01T12:00:00Z"})

    model_config = ConfigDict(from_attributes=True)

class ConsumptionLogInDB(ConsumptionLogRead):
    """Internal schema for consumption log (includes user_id)."""
    user_id: uuid.UUID = Field(..., json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"})
    model_config = ConfigDict(from_attributes=True) 