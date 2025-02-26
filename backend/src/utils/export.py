import csv
import io
import json
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import RelationshipProperty, Session

from ..crud import surveys as surveys_crud
from ..crud import items as items_crud
from ..data.models import Survey


def get_survey_answers(db: Session, survey_id: int) -> Dict[str, Any]:
    survey = surveys_crud.get_survey(db, survey_id)
    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey_dict = model_to_dict(survey)

    if survey_dict is None:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Add answers to each item
    for page in survey_dict.get("pages", []):
        for item in page.get("items", []):
            item_model = items_crud.get_item(db, item["id"])
            if item_model is None:
                raise HTTPException(status_code=404, detail="Item not found")
            item["answers"] = [model_to_dict(answer) for answer in item_model.answers]

    return survey_dict


def is_relationship(obj, attr):
    return isinstance(getattr(type(obj), attr).property, RelationshipProperty)


def safe_getattr(obj, attr):
    try:
        return getattr(obj, attr)
    except AttributeError:
        return None


def model_to_dict(obj, visited=None):
    if visited is None:
        visited = set()

    if obj in visited:
        return None  # Prevent circular references

    visited.add(obj)

    result = {}
    for c in obj.__table__.columns:
        value = safe_getattr(obj, c.name)
        if value is not None:
            if isinstance(value, (int, float, str, bool)):
                result[c.name] = value
            else:
                # For more complex types (like dates), convert to string
                result[c.name] = str(value)

    # Include non-circular relationships
    for attr, _ in inspect(obj.__class__).relationships.items():
        if not is_relationship(obj, attr):
            continue
        value = safe_getattr(obj, attr)
        if value is None:
            continue
        if isinstance(value, list):
            result[attr] = [
                model_to_dict(item, visited.copy())
                for item in value
                if item is not None
            ]
        else:
            result[attr] = model_to_dict(value, visited.copy())

    visited.remove(obj)
    return result


def survey_to_dict(survey: Survey) -> Optional[Dict[str, Any]]:
    return model_to_dict(survey)


def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_project_dict(project):
    project_dict = {
        "id": project.id,
        "title": project.title,
        "survey": [],
    }

    if project.survey:
        survey_dict = get_survey_dict(project.survey)
        project_dict["survey"].append(survey_dict)

    return project_dict


def get_survey_dict(survey):
    survey_dict = {
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "pages": [],
    }

    for page in survey.pages:
        page_dict = get_page_dict(page)
        survey_dict["pages"].append(page_dict)

    return survey_dict


def get_page_dict(page):
    page_dict = {
        "id": page.id,
        "name": page.name,
        "description": page.description,
        "order": page.order,
        "items": [],
    }

    for item in page.items:
        item_dict = get_item_dict(item)
        page_dict["items"].append(item_dict)

    return page_dict


def get_item_dict(item):
    return {
        "id": item.id,
        "title": item.title,
        "prompt": item.prompt,
        "item_type": item.item_type,
        "question_type": item.question_type,
        "options": item.options,
        "scale_min": item.scale_min,
        "scale_max": item.scale_max,
        "statements": item.statements,
        "matrix_options": item.matrix_options,
        "image_url": item.image_url,
        "video_url": item.video_url,
        "text_content": item.text_content,
    }


def generate_csv(survey_dict: Dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    # Write survey-level data
    writer.writerow(["Survey Information"])
    survey_info = {k: v for k, v in survey_dict.items() if k != "pages"}
    for key, value in survey_info.items():
        writer.writerow([key, value])

    writer.writerow([])  # Empty row for separation

    # Write page and item data
    writer.writerow(
        [
            "Page ID",
            "Page Name",
            "Page Order",
            "Item ID",
            "Item Title",
            "Item Type",
            "Item Prompt",
            "Options",
            "Question Type",
        ]
    )

    for page in survey_dict.get("pages", []):
        for item in page.get("items", []):
            options = json.dumps(item.get("options", [])) if item.get("options") else ""
            writer.writerow(
                [
                    page.get("id", ""),
                    page.get("name", ""),
                    page.get("order", ""),
                    item.get("id", ""),
                    item.get("title", ""),
                    item.get("item_type", ""),
                    item.get("prompt", ""),
                    options,
                    item.get("question_type", ""),
                ]
            )

    return output.getvalue()
