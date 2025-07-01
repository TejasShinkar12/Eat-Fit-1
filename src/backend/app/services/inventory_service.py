from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError
from app.models import Inventory
from app.schemas.inventory import InventoryCreate
from app.models.user import User
import uuid


def list_inventory(db: Session, page: int, per_page: int):
    total = db.query(Inventory).count()
    items = (
        db.query(Inventory)
        .order_by(Inventory.added_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return total, items


def get_inventory_detail(db: Session, id: uuid.UUID, include: str = None):
    query = db.query(Inventory)
    if include and "consumption_logs" in include.split(","):
        query = query.options(selectinload(Inventory.consumption_logs))
    item = query.filter(Inventory.id == id).first()
    if not item:
        return None
    return item


def create_inventory_item(db: Session, user: User, item_in: InventoryCreate):
    try:
        db_item = Inventory(
            user_id=user.id,
            name=item_in.name,
            quantity=item_in.quantity,
            calories_per_serving=item_in.calories_per_serving,
            protein_g_per_serving=item_in.protein_g_per_serving,
            carbs_g_per_serving=item_in.carbs_g_per_serving,
            fats_g_per_serving=item_in.fats_g_per_serving,
            serving_size_unit=item_in.serving_size_unit,
            expiry_date=item_in.expiry_date,
            source=item_in.source or "manual",
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError as e:
        db.rollback()
        raise e
