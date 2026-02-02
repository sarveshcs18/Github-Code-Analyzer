#!/bin/bash

# ==============================================================================
# GitHub Repo Analyzer - VM Run Script
# ==============================================================================
# Usage:
# 1. Copy this script to your GCE VM.
# 2. Make it executable: chmod +x vm_run.sh
# 3. Update the variables below or export them in your environment.
# 4. Run: ./vm_run.sh
# ==============================================================================

# --- Configuration (UPDATE THESE) ---
QUAY_USER="${QUAY_USER:-YOUR_QUAY_USERNAME}"
VERTEX_PROJECT_ID="${VERTEX_PROJECT_ID:-your-gcp-project-id}"
VERTEX_LOCATION="${VERTEX_LOCATION:-us-central1}"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-1.5-pro-001}"

# Paths on the VM (Ensure these files exist!)
HOST_CERT_PATH="${HOST_CERT_PATH:-/etc/ssl/certs/repo-analyzer.crt}"
HOST_KEY_PATH="${HOST_KEY_PATH:-/etc/ssl/private/repo-analyzer.key}"
HOST_SSH_KEY_PATH="${HOST_SSH_KEY_PATH:-/home/your-user/.ssh/id_rsa}"

# Port Configuration
# If you get "Permission denied" on port 443 (rootless mode), change this to 8443
HOST_PORT="${HOST_PORT:-443}"
# ------------------------------------

CONTAINER_NAME="repo-analyzer"
IMAGE_NAME="quay.io/$QUAY_USER/repo-analyzer:latest"

echo "--- Deploying $CONTAINER_NAME ---"
echo "Image: $IMAGE_NAME"

# 1. Check for Offline Image (Tar) or Pull
TAR_FILE="repo-analyzer.tar"

if [ -f "$TAR_FILE" ]; then
    echo "Found offline image: $TAR_FILE"
    echo "Loading image from file..."
    docker load -i "$TAR_FILE"
else
    echo "No offline tar file found ($TAR_FILE)."
    echo "Attempting to pull from Quay.io..."
    docker pull "$IMAGE_NAME"
fi

# 3. Stop/Remove existing container
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping existing container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# 4. Run new container
echo "Starting container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart always \
  -p "$HOST_PORT":443 \
  -e ENV=prod \
  -e VERTEX_PROJECT_ID="$VERTEX_PROJECT_ID" \
  -e VERTEX_LOCATION="$VERTEX_LOCATION" \
  -e GEMINI_MODEL="$GEMINI_MODEL" \
  -e CERT_PATH="/etc/certs/cert.pem" \
  -e KEY_PATH="/etc/certs/key.pem" \
  -e SSH_KEY_PATH="/etc/ssh/id_rsa" \
  -v "$HOST_CERT_PATH":/etc/certs/cert.pem:ro \
  -v "$HOST_KEY_PATH":/etc/certs/key.pem:ro \
  -v "$HOST_SSH_KEY_PATH":/etc/ssh/id_rsa:ro \
  "$IMAGE_NAME"

echo "Done! App should be running at https://<vm-ip>:$HOST_PORT/"
