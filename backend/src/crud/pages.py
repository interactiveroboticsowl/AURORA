from typing import List, Optional

from sqlalchemy import delete, func, insert
from sqlalchemy.orm import Session

from ..data import schemas
from ..data.models import Page, page_item_association


def create_page(db: Session, page: schemas.PageCreate) -> Page:
    max_order = (
        db.query(func.max(Page.order)).filter(Page.survey_id == page.survey_id).scalar()
        or 0
    )
    db_page = Page(**page.model_dump(), order=max_order + 1)
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page


def get_page(db: Session, page_id: int) -> Optional[Page]:
    return db.query(Page).filter(Page.id == page_id).first()


def update_page(db: Session, page_id: int, page: schemas.PageUpdate) -> Optional[Page]:
    db_page = get_page(db, page_id)
    if db_page:
        update_data = page.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_page, key, value)
        db.commit()
        db.refresh(db_page)
    return db_page


def delete_page(db: Session, page_id: int) -> bool:
    db_page = get_page(db, page_id)
    if db_page:
        db.delete(db_page)
        db.commit()
        return True
    return False


def add_item_to_page(db: Session, page_id: int, item_id: int) -> bool:
    """
    Adds an item to a page at the next available order.
    """
    # Get the next available order value for the item on the page
    max_order = (
        db.query(func.max(page_item_association.c.order))
        .filter(page_item_association.c.page_id == page_id)
        .scalar()
        or 0
    )
    order = max_order + 1

    # Insert new association with the next order value
    stmt = insert(page_item_association).values(
        page_id=page_id, item_id=item_id, order=order
    )
    try:
        db.execute(stmt)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error adding item to page: {e}")
        return False


def remove_item_from_page(db: Session, page_id: int, item_id: int) -> bool:
    """
    Removes an item from a page.
    """
    stmt = delete(page_item_association).where(
        page_item_association.c.page_id == page_id,
        page_item_association.c.item_id == item_id,
    )
    try:
        result = db.execute(stmt)
        db.commit()
        return result.rowcount > 0
    except Exception as e:
        db.rollback()
        print(f"Error removing item from page: {e}")
        return False


def reorder_items_on_page(
    db: Session, page_id: int, item_orders: List[schemas.PageItemOrderUpdate]
) -> bool:
    """
    Reorders items within a page by updating their order in the page_item_association table.
    """
    try:
        for item_order in item_orders:
            stmt = (
                page_item_association.update()
                .where(page_item_association.c.page_id == page_id)
                .where(page_item_association.c.item_id == item_order.id)
                .values(order=item_order.order)
            )
            db.execute(stmt)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error reordering items on page: {e}")
        return False


def get_pages_by_survey(db: Session, survey_id: int) -> List[Page]:
    return db.query(Page).filter(Page.survey_id == survey_id).order_by(Page.order).all()


def remove_page_from_survey(db: Session, survey_id: int, page_id: int) -> bool:
    """
    Removes a page from a survey.
    """
    db_page = (
        db.query(Page).filter(Page.id == page_id, Page.survey_id == survey_id).first()
    )
    if db_page:
        try:
            db.delete(db_page)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error removing page from survey: {e}")
            return False
    return False


def reorder_pages_on_survey(
    db: Session, survey_id: int, page_orders: List[schemas.PageItemOrderUpdate]
):
    """
    Reorders pages within a survey based on the provided list of page orders.
    """
    try:
        for page_order in page_orders:
            db_page = (
                db.query(Page)
                .filter(Page.id == page_order.id, Page.survey_id == survey_id)
                .first()
            )
            if db_page:
                db_page.order = page_order.order
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error reordering pages in survey: {e}")
