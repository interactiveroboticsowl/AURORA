import csv
import io
import json
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..crud import answers as answers_crud
from ..crud import items as items_crud
from ..data import schemas
from ..data.database import get_db
from ..data.models import Item

router = APIRouter()


@router.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return items_crud.create_item(db, item)


@router.get("/items/", response_model=List[schemas.Item])
def read_all_items(db: Session = Depends(get_db)):
    return items_crud.get_items(db)


@router.post("/items/import_csv", response_model=List[schemas.ItemResponse])
def import_items_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = file.file.read().decode("utf-8").splitlines()
        csv_reader = csv.DictReader(contents)

        created_items = []

        for row in csv_reader:
            item_data = {
                "title": row.get("title") or None,
                "prompt": row.get("prompt") or None,
                "item_type": row.get("item_type") or None,
                "question_type": row.get("question_type") or None,
                "options": row["options"].split(",") if row.get("options") else None,
                "scale_min": int(row["scale_min"]) if row.get("scale_min") else None,
                "scale_max": int(row["scale_max"]) if row.get("scale_max") else None,
                "statements": row["statements"].split(",") if row.get("statements") else None,
                "matrix_options": row["matrix_options"].split(",") if row.get("matrix_options") else None,
                "image_url": row.get("image_url") or None,
                "video_url": row.get("video_url") or None,
                "text_content": row.get("text_content") or None,
            }

            item_create = schemas.ItemCreate(**item_data)
            new_item = items_crud.create_item(db, item_create)
            created_items.append(new_item)

        return [
            schemas.ItemResponse.model_validate(item).model_dump()
            for item in created_items
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred during CSV import. Please check the server logs for details.",
        )

    finally:
        file.file.close()


@router.get("/items/export_csv", response_class=StreamingResponse)
def get_items_csv(db: Session = Depends(get_db)):
    try:
        items: List[Item] = items_crud.get_items(db)

        csv_file = io.StringIO()
        csv_writer = csv.writer(csv_file)

        # TODO: does it work using .to_dict?
        headers = [
            "id",
            "title",
            "prompt",
            "item_type",
            "question_type",
            "options",
            "scale_min",
            "scale_max",
            "statements",
            "matrix_options",
            "image_url",
            "video_url",
            "text_content",
        ]
        csv_writer.writerow(headers)

        for item in items:
            row = [getattr(item, header, "") or "" for header in headers]
            csv_writer.writerow(row)

        csv_file.seek(0)

        response = StreamingResponse(csv_file, media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=items.csv"
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = items_crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = items_crud.update_item(db, item_id, item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.delete("/items/{item_id}", response_model=bool)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    success = items_crud.delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return success


@router.get("/items/{item_id}/answers/", response_model=List[schemas.Answer])
def read_answers_by_item(item_id: int, db: Session = Depends(get_db)):
    return answers_crud.get_answers_by_item(db, item_id)

# TODO: maybe rebuild using minio?
# @app.post("/items/upload/", response_model=survey_design_schemas.Item)
# async def upload_item(
#     item_type: str,  # Should be 'image' or 'video'
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     file_extension = os.path.splitext(file.filename)[1].lower()

#     if item_type == "image" and file_extension not in [".jpg", ".jpeg", ".png", ".gif"]:
#         raise HTTPException(status_code=400, detail="Invalid image file type")
#     elif item_type == "video" and file_extension not in [".mp4", ".avi", ".mkv"]:
#         raise HTTPException(status_code=400, detail="Invalid video file type")

#     # Generate a unique file name to prevent overwriting
#     file_path = os.path.join(UPLOAD_DIR, f"{uuid().hex}{file_extension}")

#     # Save the file
#     with open(file_path, "wb") as f:
#         f.write(await file.read())

#     # Create the item in the database
#     item_data = {
#         "item_type": item_type,
#         "title": file.filename,
#         "prompt": None,
#         "image_url": file_path if item_type == "image" else None,
#         "video_url": file_path if item_type == "video" else None,
#     }
#     item = survey_design_schemas.ItemCreate(**item_data)

#     return items_crud.create_item(db=db, item=item)


# @app.get("/items/{item_id}/file/")
# async def get_item_file(item_id: int, db: Session = Depends(get_db)):
#     db_item = items_crud.get_item(db=db, item_id=item_id)
#     if not db_item:
#         raise HTTPException(status_code=404, detail="Item not found")

#     if db_item.item_type == "image":
#         return JSONResponse({"file_url": db_item.image_url})
#     elif db_item.item_type == "video":
#         return JSONResponse({"file_url": db_item.video_url})
#     else:
#         raise HTTPException(
#             status_code=400, detail="This item is not an image or video"
#         )