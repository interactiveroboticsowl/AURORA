from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..crud import items as items_crud
from ..crud import pages as pages_crud
from ..data import schemas
from ..data.database import get_db

router = APIRouter()


@router.get("/pages/{page_id}", response_model=schemas.Page)
def read_page(page_id: int, db: Session = Depends(get_db)):
    db_page = pages_crud.get_page(db, page_id)
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")
    return db_page


@router.put("/pages/{page_id}", response_model=schemas.Page)
def update_page(page_id: int, page: schemas.PageUpdate, db: Session = Depends(get_db)):
    db_page = pages_crud.update_page(db, page_id, page)
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")
    return db_page


@router.delete("/pages/{page_id}", response_model=bool)
def delete_page(page_id: int, db: Session = Depends(get_db)):
    success = pages_crud.delete_page(db, page_id)
    if not success:
        raise HTTPException(status_code=404, detail="Page not found")
    return success


@router.post("/pages/{page_id}/items/", response_model=bool)
def add_item_to_page(
    page_id: int, request: schemas.PageAddItemRequest, db: Session = Depends(get_db)
):
    """
    Adds an item to a page, always at the last available order.
    """
    try:
        # Extract item_id from request body
        item_id = request.item_id
        # Call the CRUD function with page_id and item_id
        success = pages_crud.add_item_to_page(db, page_id, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Failed to add item to page")
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/pages/{page_id}/items/{item_id}", response_model=bool)
def remove_item_from_page(page_id: int, item_id: int, db: Session = Depends(get_db)):
    """
    Removes an item from a page.
    """
    try:
        success = pages_crud.remove_item_from_page(db, page_id, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found on the page")
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/pages/{page_id}/items/order", response_model=bool)
def reorder_items_on_page(
    page_id: int,
    item_orders: List[schemas.PageItemOrderUpdate],
    db: Session = Depends(get_db),
):
    """
    Reorders items within a page.
    """
    try:
        success = pages_crud.reorder_items_on_page(db, page_id, item_orders)
        if not success:
            raise HTTPException(
                status_code=400, detail="Failed to reorder items on page"
            )
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pages/{page_id}/items/", response_model=List[schemas.Item])
def read_items(page_id: int, db: Session = Depends(get_db)):
    db_page = pages_crud.get_page(db, page_id)
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")
    return items_crud.get_items_by_page(db, page_id)
