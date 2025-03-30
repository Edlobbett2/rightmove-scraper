FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies and verify gunicorn installation
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==21.2.0 && \
    pip show gunicorn && \
    which gunicorn && \
    ls -l $(which gunicorn)

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PATH="/usr/local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

# Use the full path to gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"] 