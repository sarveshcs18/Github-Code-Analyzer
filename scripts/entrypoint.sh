#!/bin/bash
set -e

# Default paths from settings/env or standard mount locations
CERT_PATH=${CERT_PATH:-"/etc/certs/cert.pem"}
KEY_PATH=${KEY_PATH:-"/etc/certs/key.pem"}
PORT=${PORT:-443} # Default to 443 as per PRD

# Check environment
if [ "$ENV" = "prod" ]; then
    echo "Starting in PRODUCTION mode."
    
    # Fail fast if certs missing
    if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
        echo "ERROR: TLS Certificates not found at $CERT_PATH or $KEY_PATH."
        echo "Production mode requires HTTPS."
        exit 1
    fi
    
    echo "Certificates found. Starting Uvicorn with SSL on port $PORT..."
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port "$PORT" \
        --ssl-certfile "$CERT_PATH" \
        --ssl-keyfile "$KEY_PATH"
else
    echo "Starting in DEVELOPMENT mode (HTTP)."
    # Dev mode usually on 8000 or 443 without strict certs if not provided
    PORT=${PORT:-8000}
    echo "Listening on $PORT..."
    exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
fi
