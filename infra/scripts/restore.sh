#!/usr/bin/env bash
# Restaura una copia creada con backup.sh. ATENCIÓN: sustituye la base de datos actual y, si se
# indica, añade/sobrescribe los archivos del volumen `media`. Pide confirmación explícita.
# Uso: infra/scripts/restore.sh <archivo.dump> [media.tgz]
set -euo pipefail
cd "$(dirname "$0")/../.."
dump="${1:?Indica el archivo .dump a restaurar}"
media="${2:-}"
[ -f "$dump" ] || { echo "No existe $dump" >&2; exit 1; }
[ -z "$media" ] || [ -f "$media" ] || { echo "No existe $media" >&2; exit 1; }
read -r -p "Esto reemplazará la base de datos actual con $dump. Escribe RESTAURAR para continuar: " respuesta
[ "$respuesta" = "RESTAURAR" ] || { echo "Cancelado."; exit 1; }
if [ -n "$media" ]; then
  docker compose exec -T api sh -c 'tar xzf - -C /data/media' < "$media"
  echo "Archivos restaurados desde $media"
fi
docker compose stop api
docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner' < "$dump"
docker compose start api
echo "Restauración completada. Comprueba: curl -s localhost:\${WEB_PORT:-8080}/api/ready"
