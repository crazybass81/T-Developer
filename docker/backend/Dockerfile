FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install uv

# Copy requirements and install Python dependencies using uv
COPY backend/requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY backend/src/ ./src/

# Create basic environment file
RUN echo "ENVIRONMENT=development" > .env && \
    echo "AWS_REGION=us-east-1" >> .env

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "src/main_api.py"]
