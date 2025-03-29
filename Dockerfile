FROM python:3.11-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for GCS credentials
RUN mkdir -p /app/secrets

# Copy environment file for build if it exists
COPY .env.build .env.build

# Expose port
EXPOSE 8000

# Set environment variables
ENV PORT=8000

# Command to run the application
CMD ["sh", "-c", "cd /app && exec uvicorn main:app --host 0.0.0.0 --port ${PORT}"]