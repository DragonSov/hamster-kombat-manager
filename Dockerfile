FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    build-base \
    && pip install --upgrade pip \
    && pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev

COPY src/ /app/src/

RUN mkdir -p ./sessions

ENV PYTHONPATH=/app

CMD ["poetry", "run", "python", "src/main.py", "--run-bot"]
