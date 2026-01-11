FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (optional but helpful for building packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the pyproject.toml to install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy the rest of the application code
COPY . .

# Set the Flask environment
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run Flask in production mode using gunicorn (optional, for dev just use `flask run`)
CMD ["flask", "run"]
