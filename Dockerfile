# Use the official Python image from the Python 3.12 Alpine version
FROM python:3.12-alpine

# Set environment variables to prevent Python from writing pyc files to disk and ensure unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    build-base \
    && pip install --upgrade pip \
    && pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy only the pyproject.toml and poetry.lock to install dependencies
COPY pyproject.toml poetry.lock /app/

# Install the dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev

# Copy the rest of the code from the src directory
COPY src/ /app/src/

# Create the sessions directory
RUN mkdir -p ./sessions

# Expose port (if needed)
# EXPOSE 8000

# Run the application
CMD ["poetry", "run", "python", "src/main.py", "--run-bot"]
