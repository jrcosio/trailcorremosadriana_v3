#!/usr/bin/env bash
# Restaura una copia creada con backup.sh en el servicio `db`.
# ATENCIÓN: sustituye el contenido actual de la base. Pide confirmación explícita.
# Uso: infra/scripts/restore.sh <archivo.dump>
set -euo pipefail
cd "$(dirname "$0")/../.."
archivo="${1:?Indica el archivo .dump a restaurar}"
[ -f "$archivo" ] || { echo "No existe $archivo" >&2; exit 1; }
read -r -p "Esto reemplazará la base de datos actual con $archivo. Escribe RESTAURAR para continuar: " respuesta
[ "$respuesta" = "RESTAURAR" ] || { echo "Cancelado."; exit 1; }
docker compose stop api
docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner' < "$archivo"
docker compose start api
echo "Restauración completada. Comprueba: curl -s localhost:\${WEB_PORT:-8080}/api/ready"
