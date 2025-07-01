from fastapi import APIRouter, Depends, Query, HTTPException, Body, status
from sqlalchemy.orm import Session, selectinload
from app.api import deps
from app.models import Inventory, ConsumptionLog
from app.schemas.inventory import (
    InventorySummary,
    InventoryPaginatedResponse,
    InventoryDetail,
    InventoryCreate,
    InventoryUpdate,
)
from app.schemas.consumption_log import ConsumptionLogSummary
from app.api.deps import get_current_user
from app.models.user import User
from sqlalchemy.exc import SQLAlchemyError
import uuid
from app.services import inventory_service

router = APIRouter()


@router.get("/inventory", response_model=InventoryPaginatedResponse)
def list_inventory(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """
    List inventory items with pagination.

    - **page**: Page number (1-based)
    - **per_page**: Number of items per page (default 10, max 100)

    Returns a paginated response with inventory summaries and pagination metadata.
    """
    total, items = inventory_service.list_inventory(db, page, per_page)
    summaries = [InventorySummary.model_validate(item) for item in items]
    return InventoryPaginatedResponse(
        total=total, page=page, size=per_page, items=summaries
    )


@router.get("/inventory/{item_id}", response_model=InventoryDetail)
def get_inventory_detail(
    *,
    db: Session = Depends(deps.get_db),
    item_id: uuid.UUID,
    include: str = Query(
        None,
        description="Comma-separated list of related data to include (e.g., 'consumption_logs')",
    ),
):
    """
    Get detailed information for a single inventory item by ID.

    - **item_id**: Inventory item UUID
    - **include**: Comma-separated list of related data to include (e.g., 'consumption_logs')

    If 'consumption_logs' is included, the response will nest related consumption logs.
    Returns an InventoryDetail object.
    """
    item = inventory_service.get_inventory_detail(db, item_id, include)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    detail = InventoryDetail.model_validate(item)
    if include and "consumption_logs" in include.split(","):
        logs = [
            ConsumptionLogSummary.model_validate(log)
            for log in getattr(item, "consumption_logs", [])
        ]
        detail.consumption_logs = logs
    return detail


@router.post(
    "/inventory/create",
    response_model=InventoryDetail,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Inventory item created successfully",
            "content": {
                "application/json": {
                    "example": {"id": "123e4567-e89b-12d3-a456-426614174000"}
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Unauthorized"}}},
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "name"],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    }
                }
            },
        },
    },
)
def add_inventory_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: InventoryCreate = Body(...),
    current_user: User = Depends(get_current_user),
):
    """
    Add a new inventory item.
    -  **item**: Inventory item to add
    -  **current_user**: Authenticated user
    """
    try:
        db_item = inventory_service.create_inventory_item(db, current_user, item_in)
        detail = InventoryDetail.model_validate(db_item)
        detail.consumption_logs = []
        return detail
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


@router.patch(
    "/inventory/{item_id}",
    response_model=InventoryDetail,
    status_code=200,
    responses={
        200: {
            "description": "Inventory item updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Apple",
                        "quantity": 1.0,
                        "calories_per_serving": None,
                        "protein_g_per_serving": None,
                        "carbs_g_per_serving": None,
                        "fats_g_per_serving": None,
                        "serving_size_unit": None,
                        "expiry_date": None,
                        "source": None,
                        "added_at": "2024-06-01T12:00:00Z",
                        "updated_at": "2024-06-01T12:00:00Z",
                        "consumption_logs": [],
                    }
                }
            },
        },
        404: {"description": "Inventory item not found"},
        403: {"description": "Not authorized to update this item"},
        422: {"description": "Validation error"},
    },
)
def update_inventory_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: uuid.UUID,
    item_in: InventoryUpdate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Partially update an inventory item. Only the owner can update their items.
    Returns the updated item, or 404/403 if not found/unauthorized.
    """
    try:
        db_item = inventory_service.update_inventory_item(
            db, current_user, item_id, item_in
        )
        if not db_item:
            # Could be not found or not owned by user
            raise HTTPException(status_code=404, detail="Inventory item not found")
        detail = InventoryDetail.model_validate(db_item)
        detail.consumption_logs = []
        return detail
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
