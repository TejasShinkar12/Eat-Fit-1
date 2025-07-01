import uuid
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, ConfigDict


class InventoryBase(BaseModel):
    """Shared fields for Inventory (not exposed directly)."""

    name: str = Field(
        ...,
        description="Name of the inventory item",
        json_schema_extra={"example": "Greek Yogurt"},
    )
    quantity: float = Field(
        ...,
        description="Quantity of the item (number of servings)",
        json_schema_extra={"example": 2.0},
    )
    calories_per_serving: float = Field(
        ...,
        description="Calories per serving",
        json_schema_extra={"example": 120.0},
    )
    protein_g_per_serving: float = Field(
        ...,
        description="Protein per serving (g)",
        json_schema_extra={"example": 10.0},
    )
    carbs_g_per_serving: float = Field(
        ...,
        description="Carbs per serving (g)",
        json_schema_extra={"example": 15.0},
    )
    fats_g_per_serving: float = Field(
        ...,
        description="Fats per serving (g)",
        json_schema_extra={"example": 2.0},
    )
    serving_size_unit: str = Field(
        ...,
        description="Unit for serving size (e.g., g, ml, piece)",
        json_schema_extra={"example": "g"},
    )
    expiry_date: Optional[date] = Field(
        None,
        description="Expiry date (YYYY-MM-DD)",
        json_schema_extra={"example": "2024-12-31"},
    )
    source: str = Field(
        ...,
        description="Source of the item (e.g., manual, image)",
        json_schema_extra={"example": "manual"},
    )

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v):
        if v < 0:
            raise ValueError("Quantity must be non-negative")
        return v

    @field_validator("expiry_date")
    @classmethod
    def expiry_date_in_future(cls, v):
        if v is not None and v < date.today():
            raise ValueError("Expiry date must be today or in the future")
        return v


class InventoryCreate(InventoryBase):
    """Fields required for creating an inventory item."""

    pass


class InventoryUpdate(BaseModel):
    """Fields for updating an inventory item (all optional)."""

    name: Optional[str] = Field(None, json_schema_extra={"example": "Greek Yogurt"})
    quantity: Optional[float] = Field(None, json_schema_extra={"example": 2.0})
    calories_per_serving: Optional[float] = Field(
        None, json_schema_extra={"example": 120.0}
    )
    protein_g_per_serving: Optional[float] = Field(
        None, json_schema_extra={"example": 10.0}
    )
    carbs_g_per_serving: Optional[float] = Field(
        None, json_schema_extra={"example": 15.0}
    )
    fats_g_per_serving: Optional[float] = Field(
        None, json_schema_extra={"example": 2.0}
    )
    serving_size_unit: Optional[str] = Field(None, json_schema_extra={"example": "g"})
    expiry_date: Optional[date] = Field(
        None, json_schema_extra={"example": "2024-12-31"}
    )
    source: Optional[str] = Field(None, json_schema_extra={"example": "manual"})

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("Quantity must be non-negative")
        return v

    @field_validator("expiry_date")
    @classmethod
    def expiry_date_in_future(cls, v):
        if v is not None and v < date.today():
            raise ValueError("Expiry date must be today or in the future")
        return v


class InventoryRead(InventoryBase):
    """Fields returned in API responses for inventory items."""

    id: uuid.UUID = Field(
        ..., json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"}
    )
    added_at: datetime = Field(
        ..., json_schema_extra={"example": "2024-06-01T12:00:00Z"}
    )
    updated_at: datetime = Field(
        ..., json_schema_extra={"example": "2024-06-01T12:00:00Z"}
    )

    model_config = ConfigDict(from_attributes=True)


class InventoryInDB(InventoryRead):
    """Internal schema for inventory (includes user_id)."""

    user_id: uuid.UUID = Field(
        ..., json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"}
    )
    model_config = ConfigDict(from_attributes=True)


class InventorySummary(BaseModel):
    """
    Lightweight summary for inventory list responses.
    Includes only the most essential fields for list views.
    """

    id: uuid.UUID = Field(
        ...,
        description="Inventory item ID",
        json_schema_extra={"example": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc"},
    )
    name: str = Field(
        ...,
        description="Name of the inventory item",
        json_schema_extra={"example": "Greek Yogurt"},
    )
    quantity: float = Field(
        ...,
        description="Quantity of the item (number of servings)",
        json_schema_extra={"example": 2.0},
    )
    expiry_date: Optional[date] = Field(
        None,
        description="Expiry date (YYYY-MM-DD)",
        json_schema_extra={"example": "2024-12-31"},
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc",
                "name": "Greek Yogurt",
                "quantity": 2.0,
                "expiry_date": "2024-12-31",
            }
        },
    )


from .consumption_log import ConsumptionLogSummary


class InventoryDetail(InventoryRead):
    """
    Detailed inventory response schema.
    Includes all inventory fields and, optionally, nested consumption logs if requested.
    """

    consumption_logs: Optional[list[ConsumptionLogSummary]] = Field(
        None,
        description="List of consumption logs for this inventory item (if included)",
        json_schema_extra={
            "example": [
                {
                    "id": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc",
                    "item_name": "Greek Yogurt",
                    "quantity_consumed": 1.0,
                    "consumed_at": "2024-06-01T12:00:00Z",
                }
            ]
        },
    )
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc",
                "name": "Greek Yogurt",
                "quantity": 2.0,
                "calories_per_serving": 120.0,
                "protein_g_per_serving": 10.0,
                "carbs_g_per_serving": 15.0,
                "fats_g_per_serving": 2.0,
                "serving_size_unit": "g",
                "expiry_date": "2024-12-31",
                "source": "manual",
                "added_at": "2024-06-01T12:00:00Z",
                "updated_at": "2024-06-01T12:00:00Z",
                "consumption_logs": [
                    {
                        "id": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc",
                        "item_name": "Greek Yogurt",
                        "quantity_consumed": 1.0,
                        "consumed_at": "2024-06-01T12:00:00Z",
                    }
                ],
            }
        },
    )


class InventoryPaginatedResponse(BaseModel):
    """
    Paginated response for inventory list endpoint.
    Contains pagination metadata and a list of inventory summaries.
    """

    total: int = Field(..., description="Total number of inventory items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    items: list[InventorySummary] = Field(
        ..., description="List of inventory summaries for this page"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 100,
                "page": 1,
                "size": 10,
                "items": [
                    {
                        "id": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc",
                        "name": "Greek Yogurt",
                        "quantity": 2.0,
                        "expiry_date": "2024-12-31",
                    }
                ],
            }
        }
    )
