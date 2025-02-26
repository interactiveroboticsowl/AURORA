from enum import StrEnum


# Define the possible types of items in a survey
class ItemType(StrEnum):
    QUESTION = "question"
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "static_text"  # For static texts or statements


# Define the possible types of questions
class QuestionType(StrEnum):
    FREE_TEXT = "free_text"
    MULTIPLE_CHOICE_SINGLE = "multiple_choice_single"
    MULTIPLE_CHOICE_MULTIPLE = "multiple_choice_multiple"
    SCALE = "scale"
    MATRIX_SCALE = "matrix_scale"
    LIKERT_SCALE = "likert_scale"
