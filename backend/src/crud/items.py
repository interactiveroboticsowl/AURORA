from typing import List, Optional

from sqlalchemy.orm import Session

from ..data import schemas
from ..data.models import Answer, Item


# Create a new item (question, image, video, text, etc.)
def create_item(db: Session, item: schemas.ItemCreate):
    db_item = Item(**item.model_dump(exclude_unset=True))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# Get all items
def get_items(db: Session):
    return db.query(Item).all()


# Get a specific item by ID
def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()


def update_item(db: Session, item_id: int, item: schemas.ItemUpdate) -> Optional[Item]:
    db_item = get_item(db, item_id)
    if not db_item:
        return None

    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item_answers(db: Session, item_id: int, survey_id: int, page_id: int):
    return (
        db.query(Answer)
        .join(Item)
        .filter(
            Answer.item_id == item_id,
            Item.survey_id == survey_id,
            Item.page_id == page_id,
        )
        .all()
    )


# Delete an item
def delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    if not db_item:
        return False

    db.delete(db_item)
    db.commit()
    return True


def get_items_by_page(db: Session, page_id: int) -> List[Item]:
    return db.query(Item).filter(Item.page_id == page_id).all()
