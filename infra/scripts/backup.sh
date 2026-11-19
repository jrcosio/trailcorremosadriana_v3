#!/usr/bin/env bash
# Copia de seguridad: PostgreSQL (pg_dump, formato custom) y archivos subidos (volumen `media`)
# cuando ALMACENAMIENTO=local. Con S3/R2 la copia de objetos se gestiona en el bucket (ver
# docs/desarrollo.md). El procedimiento completo de restauración se prueba en la feature 011.
# Uso: infra/scripts/backup.sh [carpeta-destino]   (por defecto ./copias)
set -euo pipefail
cd "$(dirname "$0")/../.."
destino="${1:-copias}"
mkdir -p "$destino"
marca="$(date +%Y%m%d-%H%M%S)"

dump="$destino/trail-$marca.dump"
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner' > "$dump"
echo "Base de datos: $dump ($(wc -c < "$dump" | tr -d ' ') bytes)"

if [ "$(docker compose exec -T api printenv ALMACENAMIENTO | tr -d '\r')" = "local" ]; then
  media="$destino/media-$marca.tgz"
  docker compose exec -T api tar czf - -C /data/media . > "$media"
  echo "Archivos: $media ($(docker compose exec -T api sh -c 'ls /data/media | wc -l' | tr -d ' \r') archivos)"
else
  echo "Archivos: almacenamiento S3/R2 — copia gestionada en el bucket."
fi
