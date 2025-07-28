# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only the dependency files to leverage Docker cache
COPY poetry.lock pyproject.toml ./

# Install project dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-root

# Copy the rest of the application code
COPY ./app /app/app

# Command to run the API
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 