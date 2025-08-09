from fastapi import (
    BackgroundTasks,
    APIRouter,
    Depends,
    Query,
    HTTPException,
    Body,
    UploadFile,
    File,
    Path,
)
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
import os
from app.services.storage_service import StorageService
from app.models.image_upload import ImageUpload
from app.schemas.image_upload import ImageUploadRead
from app.enums import ImageUploadStatus
from app.utils.logger import get_logger
from app.services.detection_task import run_detection_task
from app.schemas.image_upload import ImageUploadReview
from app.schemas.image_upload import InventoryFromDetectionPayload
from app.schemas.inventory import InventoryRead
from typing import List

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
    status_code=201,
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


@router.delete(
    "/inventory/{item_id}",
    status_code=200,
    responses={
        200: {
            "description": "Item deleted successfully",
            "content": {
                "application/json": {"example": {"detail": "Item deleted successfully"}}
            },
        },
        404: {"description": "Inventory item not found"},
        403: {"description": "Not authorized to delete this item"},
    },
)
def delete_inventory_item(
    *,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
    item_id: uuid.UUID,
):
    """
    Delete an inventory item. Only the owner can delete their items.
    Returns the updated item, or 404/403 if not found/unauthorized.
    """
    try:
        db_item = inventory_service.delete_inventory_item(db, user, item_id)
        if not db_item:
            # Could be not found or not owned by user
            raise HTTPException(status_code=404, detail="Inventory item not found")
        return {"detail": "Item deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


@router.post(
    "/upload-image",
    response_model=ImageUploadRead,
    status_code=201,
    responses={
        201: {
            "description": "Image uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "file_path": "uploaded_images/123e4567-e89b-12d3-a456-426614174000_20240720123456789012.jpg",
                        "status": "pending",
                        "error_message": None,
                        "created_at": "2024-07-20T12:34:56.789Z",
                        "updated_at": "2024-07-20T12:34:56.789Z",
                    }
                }
            },
        },
        400: {
            "description": "Invalid file type or size",
            "content": {
                "application/json": {
                    "example": {"detail": "Unsupported file type: text/plain"}
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
async def upload_inventory_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
):
    logger = get_logger("UploadImage")
    # Validate file size (max 10MB)
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        logger.error(f"File too large: {file.filename} ({len(file_bytes)} bytes)")
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Validate extension
    allowed_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        logger.error(f"Unsupported file extension: {file.filename}")
        raise HTTPException(
            status_code=400, detail=f"Unsupported file extension: {ext}"
        )

    # Validate MIME type
    if not file.content_type.startswith("image/"):
        logger.error(f"Unsupported MIME type: {file.content_type}")
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {file.content_type}"
        )

    # Store image and create DB record
    try:
        file_path = StorageService.store_image(file_bytes, file.filename, current_user)
    except Exception as e:
        logger.error(f"Failed to store image: {e}")
        raise HTTPException(status_code=500, detail="Failed to store image: " + str(e))

    # Create ImageUpload DB record (transactional)
    try:
        image_upload = ImageUpload(
            user_id=current_user.id,
            file_path=file_path,
            status=ImageUploadStatus.pending,
            error_message=None,
        )
        db.add(image_upload)
        db.commit()
        db.refresh(image_upload)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create ImageUpload DB record: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create image upload record: " + str(e)
        )

    # Trigger detection in background
    try:
        background_tasks.add_task(
            run_detection_task,
            image_upload.id,
            current_user.id,
            file_path,
        )
    except Exception as e:
        logger.error(f"Failed to schedule detection task: {e}")
        # Do not fail the upload, just log

    logger.info(
        f"Image uploaded: {file_path} (user={current_user.id}, id={image_upload.id})"
    )
    return ImageUploadRead.model_validate(image_upload)


@router.get(
    "/image-status/{image_id}",
    response_model=ImageUploadRead,
    responses={
        200: {
            "description": "Image upload and detection status",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "file_path": "uploaded_images/123e4567-e89b-12d3-a456-426614174000_20240720123456789012.jpg",
                        "status": "complete",
                        "detection_results_json": [
                            {
                                "object_name": "apple",
                                "confidence": 0.95,
                                "bbox": [1, 2, 3, 4],
                            }
                        ],
                        "error_message": None,
                        "created_at": "2024-07-20T12:34:56.789Z",
                        "updated_at": "2024-07-20T12:34:56.789Z",
                    }
                }
            },
        },
        404: {
            "description": "Image upload not found",
            "content": {
                "application/json": {"example": {"detail": "Image upload not found"}}
            },
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this image upload"}
                }
            },
        },
    },
)
def get_image_upload_status(
    image_id: uuid.UUID = Path(..., description="Image upload record ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
):
    logger = get_logger("ImageStatus")
    image_upload = db.query(ImageUpload).filter(ImageUpload.id == image_id).first()
    if not image_upload:
        logger.error(f"ImageUpload not found: {image_id}")
        raise HTTPException(status_code=404, detail="Image upload not found")
    if image_upload.user_id != current_user.id:
        logger.warning(
            f"Unauthorized access attempt: user={current_user.id}, image_id={image_id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to access this image upload"
        )
    logger.info(
        f"Image status checked: user={current_user.id}, image_id={image_id}, status={image_upload.status}"
    )
    return ImageUploadRead.model_validate(image_upload)


@router.post(
    "/review-detections/{image_id}",
    response_model=ImageUploadRead,
    responses={
        200: {
            "description": "Detection review successful",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "file_path": "uploaded_images/123e4567-e89b-12d3-a456-426614174000_20240720123456789012.jpg",
                        "status": "reviewed",
                        "reviewed_results": [
                            {
                                "object_name": "apple",
                                "quantity": 2,
                                "confidence": 0.95,
                                "bbox": [1, 2, 3, 4],
                            }
                        ],
                        "error_message": None,
                        "created_at": "2024-07-20T12:34:56.789Z",
                        "updated_at": "2024-07-20T12:34:56.789Z",
                    }
                }
            },
        },
        404: {
            "description": "Image upload not found",
            "content": {
                "application/json": {"example": {"detail": "Image upload not found"}}
            },
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this image upload"}
                }
            },
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {"example": {"detail": "Invalid review payload"}}
            },
        },
    },
)
def review_detections(
    image_id: uuid.UUID = Path(..., description="Image upload record ID"),
    review: ImageUploadReview = Body(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
):
    logger = get_logger("ReviewDetections")
    image_upload = db.query(ImageUpload).filter(ImageUpload.id == image_id).first()
    if not image_upload:
        logger.error(f"ImageUpload not found: {image_id}")
        raise HTTPException(status_code=404, detail="Image upload not found")
    if image_upload.user_id != current_user.id:
        logger.warning(
            f"Unauthorized review attempt: user={current_user.id}, image_id={image_id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to access this image upload"
        )
    try:
        image_upload.reviewed_results = [
            obj.model_dump() for obj in review.reviewed_results
        ]
        db.commit()
        db.refresh(image_upload)
        logger.info(
            f"Detection review updated: user={current_user.id}, image_id={image_id}"
        )
        return ImageUploadRead.model_validate(image_upload)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update reviewed results: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to update reviewed results: " + str(e)
        )


@router.post(
    "/create-from-detections/{image_id}",
    response_model=List[InventoryRead],
    responses={
        200: {
            "description": "Inventory items created from detections",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "b3b7c7e2-8c2a-4e2a-9e2a-123456789abc",
                            "name": "Apple",
                            "quantity": 2.0,
                            "calories_per_serving": 52.0,
                            "protein_g_per_serving": 0.3,
                            "carbs_g_per_serving": 14.0,
                            "fats_g_per_serving": 0.2,
                            "serving_size_unit": "g",
                            "expiry_date": "2024-12-31",
                            "source": "image",
                            "added_at": "2024-07-20T12:34:56.789Z",
                            "updated_at": "2024-07-20T12:34:56.789Z",
                        }
                    ]
                }
            },
        },
        404: {
            "description": "Image upload not found",
            "content": {
                "application/json": {"example": {"detail": "Image upload not found"}}
            },
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this image upload"}
                }
            },
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid inventory creation payload"}
                }
            },
        },
    },
)
def create_inventory_from_detections(
    image_id: uuid.UUID = Path(..., description="Image upload record ID"),
    payload: InventoryFromDetectionPayload = Body(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
):
    logger = get_logger("CreateFromDetections")
    image_upload = db.query(ImageUpload).filter(ImageUpload.id == image_id).first()
    if not image_upload:
        logger.error(f"ImageUpload not found: {image_id}")
        raise HTTPException(status_code=404, detail="Image upload not found")
    if image_upload.user_id != current_user.id:
        logger.warning(
            f"Unauthorized inventory creation attempt: user={current_user.id}, image_id={image_id}"
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to access this image upload"
        )
    created_items = []
    try:
        for item_data in payload.items:
            # Convert expiry_date to date if present
            if item_data.expiry_date:
                from datetime import datetime

                expiry_date = datetime.strptime(
                    item_data.expiry_date, "%Y-%m-%d"
                ).date()
            else:
                expiry_date = None
            inventory_in = {
                "name": item_data.name,
                "quantity": item_data.quantity,
                "calories_per_serving": item_data.calories_per_serving,
                "protein_g_per_serving": item_data.protein_g_per_serving,
                "carbs_g_per_serving": item_data.carbs_g_per_serving,
                "fats_g_per_serving": item_data.fats_g_per_serving,
                "serving_size_unit": item_data.serving_size_unit,
                "expiry_date": expiry_date,
                "source": item_data.source or "image",
            }
            db_item = inventory_service.create_inventory_item(
                db, current_user, type("Obj", (), inventory_in)()
            )
            created_items.append(InventoryRead.model_validate(db_item))
        # Optionally update ImageUpload status
        db.commit()
        db.refresh(image_upload)
        logger.info(
            f"Inventory created from detections: user={current_user.id}, image_id={image_id}, count={len(created_items)}"
        )
        return created_items
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create inventory from detections: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create inventory from detections: " + str(e),
        )
