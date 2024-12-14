
# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/
COPY data/ ./data/
COPY .env .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create directory for logs
RUN mkdir -p /app/logs

# Set permissions
RUN chmod -R 755 /app

# Expose port for Gradio
EXPOSE 7860

# Command to run the application
CMD ["python", "src/extract_information.py"]