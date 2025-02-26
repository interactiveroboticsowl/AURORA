
FROM python:3.12

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

EXPOSE 8080

CMD ["poetry", "run", "python", "src/survey_controller.py"]

