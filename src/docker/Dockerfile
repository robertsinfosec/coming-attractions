# Multi-stage build for coming-attractions
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy package files (from src/ directory in build context)
COPY src/requirements.txt .
COPY src/setup.py .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/coming_attractions/ /app/coming_attractions/

# Create non-root user
RUN useradd -m -u 1000 trailers && \
    chown -R trailers:trailers /app

# Switch to non-root user
USER trailers

# Set Python path
ENV PYTHONPATH=/app

# Create data directory for trailers
RUN mkdir -p /data/trailers && \
    chown -R trailers:trailers /data

# Working directory for trailer operations
WORKDIR /data/trailers

# Declare volume for trailer storage
VOLUME ["/data/trailers"]

# Health check (verify imports work)
RUN python -c "from coming_attractions.cli import cli"

# Entry point
ENTRYPOINT ["python", "-m", "coming_attractions"]

# Default command (daemon mode)
CMD ["daemon", "--interval", "12h"]
