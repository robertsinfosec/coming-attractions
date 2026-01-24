# Multi-stage build for coming-attractions
FROM python:3.14-slim as builder

# OCI Image Metadata Labels
# https://github.com/opencontainers/image-spec/blob/main/annotations.md
LABEL org.opencontainers.image.title="Coming Attractions" \
      org.opencontainers.image.description="Automated movie trailer fetcher and manager for Plex/Jellyfin. Downloads trailers from TMDb/YouTube with configurable retention policies." \
      org.opencontainers.image.authors="robertsinfosec" \
      org.opencontainers.image.vendor="robertsinfosec" \
      org.opencontainers.image.url="https://github.com/robertsinfosec/coming-attractions" \
      org.opencontainers.image.source="https://github.com/robertsinfosec/coming-attractions" \
      org.opencontainers.image.documentation="https://github.com/robertsinfosec/coming-attractions/blob/main/README.md" \
      org.opencontainers.image.licenses="MIT"

# Install system dependencies in single layer
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

# Install Python dependencies with wheel support for faster builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/coming_attractions/ /app/coming_attractions/

# Create data directory for trailers (must be done as root)
RUN mkdir -p /data/trailers

# Create non-root user and set ownership
RUN useradd -m -u 1000 trailers && \
    chown -R trailers:trailers /app /data

# Switch to non-root user
USER trailers

# Set Python path
ENV PYTHONPATH=/app

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
