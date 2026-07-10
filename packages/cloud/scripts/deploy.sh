#!/usr/bin/env bash
set -euo pipefail

# JARVIS Deployment Script
# Usage: ./deploy.sh [environment] [version]

ENVIRONMENT="${1:-development}"
VERSION="${2:-latest}"

echo "=== JARVIS Deployment ==="
echo "Environment: ${ENVIRONMENT}"
echo "Version: ${VERSION}"

echo "Building images..."
docker compose -f docker/docker-compose.yml build

if [ "${ENVIRONMENT}" = "production" ]; then
    echo "Pushing images..."
    docker compose -f docker/docker-compose.yml push
fi

echo "Starting services..."
docker compose -f docker/docker-compose.yml up -d

echo "=== Deployment Complete ==="
echo "Health check: http://localhost:8000/health"
