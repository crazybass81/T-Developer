# Multi-stage build for T-Developer v2
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .

# Create virtual environment and install dependencies
RUN uv venv .venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Copy application code
COPY packages/ ./packages/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Run tests and quality checks
RUN . .venv/bin/activate && \
    python -m pytest tests/ --no-cov && \
    python -m mypy packages/ --ignore-missing-imports && \
    python -m black --check packages/

# Production stage
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv .venv
COPY --from=builder --chown=appuser:appuser /app/packages ./packages
COPY --from=builder --chown=appuser:appuser /app/scripts ./scripts

# Copy configuration files
COPY --chown=appuser:appuser .env.example .

# Set environment variables
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Security settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Switch to non-root user
USER appuser

# Default command (can be overridden)
CMD ["python", "-m", "packages.mcp.server.main"]