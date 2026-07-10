#!/usr/bin/env bash
set -euo pipefail

# JARVIS Restore Script
# Usage: ./restore.sh [target] [backup_file]

TARGET="${1:-all}"
BACKUP_FILE="${2:-}"

if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 [target] [backup_file]"
    echo "Targets: postgres, qdrant"
    exit 1
fi

echo "=== JARVIS Restore ==="
echo "Target: ${TARGET}"
echo "Backup File: ${BACKUP_FILE}"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

restore_postgres() {
    echo "Restoring PostgreSQL..."
    gunzip -c "${BACKUP_FILE}" | docker exec -i jarvis-postgres psql -U jarvis -d jarvis
    echo "  -> PostgreSQL restored"
}

restore_qdrant() {
    echo "Restoring Qdrant..."
    docker cp "${BACKUP_FILE}" jarvis-qdrant:/tmp/restore.tar.gz
    docker exec jarvis-qdrant tar xzf /tmp/restore.tar.gz -C /
    echo "  -> Qdrant restored"
}

case "${TARGET}" in
    postgres) restore_postgres ;;
    qdrant) restore_qdrant ;;
    *)
        echo "Unknown target: ${TARGET}"
        exit 1
        ;;
esac

echo "=== Restore Complete ==="
