from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, selectinload
from app.api import deps
from app.models import Inventory, ConsumptionLog
from app.schemas.inventory import (
    InventorySummary,
    InventoryPaginatedResponse,
    InventoryDetail,
)
from app.schemas.consumption_log import ConsumptionLogSummary
import uuid

router = APIRouter()


@router.get("/inventory", response_model=InventoryPaginatedResponse)
def list_inventory(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    List inventory items with pagination.

    - **page**: Page number (1-based)
    - **per_page**: Number of items per page (default 10, max 100)

    Returns a paginated response with inventory summaries and pagination metadata.
    """
    total = db.query(Inventory).count()
    items = (
        db.query(Inventory)
        .order_by(Inventory.added_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    summaries = [InventorySummary.model_validate(item) for item in items]
    return InventoryPaginatedResponse(
        total=total, page=page, size=per_page, items=summaries
    )


@router.get("/inventory/{id}", response_model=InventoryDetail)
def get_inventory_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: uuid.UUID,
    include: str = Query(
        None,
        description="Comma-separated list of related data to include (e.g., 'consumption_logs')",
    )
):
    """
    Get detailed information for a single inventory item by ID.

    - **id**: Inventory item UUID
    - **include**: Comma-separated list of related data to include (e.g., 'consumption_logs')

    If 'consumption_logs' is included, the response will nest related consumption logs.
    Returns an InventoryDetail object.
    """
    query = db.query(Inventory)
    if include and "consumption_logs" in include.split(","):
        query = query.options(selectinload(Inventory.consumption_logs))
    item = query.filter(Inventory.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    detail = InventoryDetail.model_validate(item)
    if include and "consumption_logs" in include.split(","):
        logs = [
            ConsumptionLogSummary.model_validate(log) for log in item.consumption_logs
        ]
        detail.consumption_logs = logs
    return detail
