# ===========================================================================
# CineMind AI — Multi-stage Docker build
# Stage 1: Build the React frontend
# Stage 2: Python backend + pre-built static assets
# ===========================================================================

# --- Stage 1: Frontend build -----------------------------------------------
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --ignore-scripts
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python backend -----------------------------------------------
FROM python:3.11-slim AS runtime

LABEL maintainer="CineMind <https://github.com/KINGHACKERjudewin>"
LABEL description="CineMind AI — Hybrid movie recommendation engine"

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY config.py ./
COPY api/ ./api/
COPY recommender/ ./recommender/

# Copy pre-built frontend static assets from stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Data and model files must be provided via volume mount at runtime:
#   docker run -v /path/to/data:/app/data -v /path/to/models:/app/models ...
# This keeps the image small and secrets out of the layer cache.

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
