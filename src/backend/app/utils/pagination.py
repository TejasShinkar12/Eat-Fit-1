from typing import Any, Dict, Tuple
from sqlalchemy.orm import Query


def paginate_query(
    query: Query, page: int = 1, per_page: int = 10
) -> Tuple[list, Dict[str, Any]]:
    """
    Paginate a SQLAlchemy query.

    Args:
        query (Query): SQLAlchemy query object.
        page (int): Current page number (1-indexed).
        per_page (int): Number of items per page.

    Returns:
        Tuple[list, Dict[str, Any]]: (results, meta_info)
            results: List of items for the current page.
            meta_info: Dict with pagination metadata.
    """
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    meta = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page if per_page else 0,
        "has_next": page * per_page < total,
        "has_prev": page > 1,
    }
    return items, meta
