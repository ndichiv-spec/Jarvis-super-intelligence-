#!/usr/bin/env bash
set -euo pipefail

# JARVIS Backup Script
# Usage: ./backup.sh [target]

TARGET="${1:-all}"
BACKUP_DIR="/data/backups/$(date +%Y%m%d%H%M%S)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== JARVIS Backup ==="
echo "Target: ${TARGET}"
echo "Backup Dir: ${BACKUP_DIR}"

mkdir -p "${BACKUP_DIR}"

backup_postgres() {
    echo "Backing up PostgreSQL..."
    docker exec jarvis-postgres pg_dump -U jarvis -d jarvis > "${BACKUP_DIR}/postgres_${TIMESTAMP}.sql"
    gzip "${BACKUP_DIR}/postgres_${TIMESTAMP}.sql"
    echo "  -> ${BACKUP_DIR}/postgres_${TIMESTAMP}.sql.gz"
}

backup_redis() {
    echo "Backing up Redis..."
    docker exec jarvis-redis redis-cli SAVE
    echo "  -> Redis RDB saved"
}

backup_qdrant() {
    echo "Backing up Qdrant..."
    docker exec jarvis-qdrant tar czf "/tmp/qdrant_${TIMESTAMP}.tar.gz" /qdrant/storage
    docker cp "jarvis-qdrant:/tmp/qdrant_${TIMESTAMP}.tar.gz" "${BACKUP_DIR}/"
    echo "  -> ${BACKUP_DIR}/qdrant_${TIMESTAMP}.tar.gz"
}

case "${TARGET}" in
    all)
        backup_postgres
        backup_redis
        backup_qdrant
        ;;
    postgres) backup_postgres ;;
    redis) backup_redis ;;
    qdrant) backup_qdrant ;;
    *)
        echo "Unknown target: ${TARGET}"
        echo "Usage: $0 [all|postgres|redis|qdrant]"
        exit 1
        ;;
esac

echo "=== Backup Complete ==="
echo "Location: ${BACKUP_DIR}"
