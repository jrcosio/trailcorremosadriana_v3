#!/usr/bin/env bash
# Copia de seguridad de PostgreSQL (formato custom de pg_dump) desde el servicio `db`.
# Uso: infra/scripts/backup.sh [carpeta-destino]   (por defecto ./copias)
# Los archivos subidos (feature 003) se copiarán con este mismo script cuando exista su volumen.
# El procedimiento completo de copia y restauración se prueba en la feature 011.
set -euo pipefail
cd "$(dirname "$0")/../.."
destino="${1:-copias}"
mkdir -p "$destino"
marca="$(date +%Y%m%d-%H%M%S)"
archivo="$destino/trail-$marca.dump"
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner' > "$archivo"
echo "Copia creada: $archivo ($(wc -c < "$archivo") bytes)"
