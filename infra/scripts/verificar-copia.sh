#!/usr/bin/env bash
# Verifica de extremo a extremo una copia de seguridad (feature 011, FR-008):
#   1. huellas de la base (una por tabla) y de los archivos locales;
#   2. backup.sh;
#   3. cambio controlado: se modifica el teléfono de contacto y se borra un archivo subido;
#   4. restore.sh (con la confirmación RESTAURAR);
#   5. nuevas huellas: deben coincidir con las del paso 1.
# SOLO para entornos de prueba o ensayo: modifica datos temporalmente y los recupera de la copia.
# Uso: infra/scripts/verificar-copia.sh [carpeta-destino]   (por defecto ./copias)
set -euo pipefail
cd "$(dirname "$0")/../.."
destino="${1:-copias}"

read -r -p "Este script modifica datos y restaura una copia. Escribe VERIFICAR para continuar: " respuesta
[ "$respuesta" = "VERIFICAR" ] || { echo "Cancelado."; exit 1; }

huellas() {
  # Una línea «tabla|md5» por tabla del esquema public (filas ordenadas por su texto).
  docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -v ON_ERROR_STOP=1' <<'SQL'
SELECT format(
  'SELECT %L || ''|'' || md5(coalesce(string_agg(t::text, ''§'' ORDER BY t::text), '''')) FROM %I t',
  tablename, tablename)
FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename
\gexec
SQL
  if [ "$(docker compose exec -T api printenv ALMACENAMIENTO | tr -d '\r')" = "local" ]; then
    docker compose exec -T api sh -c 'cd /data/media && find . -type f -exec sha256sum {} + | sort -k2'
  fi
}

antes="$(mktemp)"; despues="$(mktemp)"; salida="$(mktemp)"
trap 'rm -f "$antes" "$despues" "$salida"' EXIT

huellas > "$antes"
echo "Huellas tomadas: $(grep -c '|' "$antes") tablas y $(grep -vc '|' "$antes") archivos."

infra/scripts/backup.sh "$destino" | tee "$salida"
dump="$(sed -n 's/^Base de datos: \(.*\.dump\) .*/\1/p' "$salida")"
media="$(sed -n 's/^Archivos: \(.*\.tgz\) .*/\1/p' "$salida")"
[ -f "$dump" ] || { echo "No se encontró el volcado de la copia." >&2; exit 1; }

echo "Cambio controlado..."
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -c "UPDATE configuracion SET telefono = '\''000000000'\''"' >/dev/null
archivo="$(docker compose exec -T api sh -c 'ls /data/media | head -1' | tr -d '\r')"
if [ -n "$archivo" ]; then
  docker compose exec -T api rm -f "/data/media/$archivo"
fi
huellas > "$despues"
if cmp -s "$antes" "$despues"; then
  echo "El cambio controlado no ha modificado las huellas." >&2
  exit 1
fi

echo "RESTAURAR" | infra/scripts/restore.sh "$dump" ${media:+"$media"}
for _ in $(seq 1 60); do
  docker compose exec -T api python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/ready', timeout=2)" 2>/dev/null && break
  sleep 1
done

huellas > "$despues"
if diff -u "$antes" "$despues"; then
  echo "OK: la restauración deja las $(grep -c '|' "$antes") tablas y los $(grep -vc '|' "$antes") archivos idénticos a la copia."
else
  echo "FALLO: la restauración no coincide con la copia (ver diferencias arriba)." >&2
  exit 1
fi
