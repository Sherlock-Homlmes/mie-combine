FROM python:3.10-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/assets/cache /app/assets/rank_icon

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python3", "main.py"]
