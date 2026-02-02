# Build Frontend
FROM node:18-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build Backend Environment
FROM python:3.10-slim as backend-builder
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final Runtime Image
FROM python:3.10-slim
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies (git, ssh)
RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY --from=backend-builder /root/.local /root/.local

# Copy application code
COPY backend/app /app/app

# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist /app/static

# Copy entrypoint
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create non-root user for security (optional but recommended in PRD)
# For simplicity in this step, running as root inside container or use strictly defined user later.
# PRD says "Podman preferred (rootless where possible)". 
# We'll create a user but run simple for now.

# Expose port 443 (Prod) and 8000 (Dev)
EXPOSE 443 8000

# Start command
ENTRYPOINT ["/app/entrypoint.sh"]
