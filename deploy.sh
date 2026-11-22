#!/usr/bin/env bash
# «cond && ok … || falla …» es intencionado: ok() siempre termina bien.
# shellcheck disable=SC2015
# Trail Peñasagra — despliegue en la máquina virtual (feature 012, US12; docs/operacion.md §0).
#
# Instala o actualiza la web con una sola orden, y se puede repetir sin riesgo:
#   1. comprueba Docker y el .env;              2. descarga el código (git pull);
#   3. hace una copia si ya hay datos;          4. construye y migra la base;
#   5. carga los datos iniciales en una base vacía (nunca sobrescribe datos existentes);
#   6. crea la cuenta del panel si no hay ninguna;
#   7. para la web anterior que ocupe los puertos 80/443 (sin borrar sus datos);
#   8. arranca y espera a que la web responda por HTTPS (si falla, vuelve a la web anterior);
#   9. comprueba redirecciones, cabeceras y certificado;  10. programa la copia diaria.
#
# Uso, en la carpeta del repositorio y con el .env de producción copiado en ella:
#   sudo ./deploy.sh
# Opciones: --sin-descargar (no hace git pull).
# Variables opcionales: DEPLOY_ESPERA (segundos de espera al arrancar; 180 por defecto).
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$RAIZ"
ESTADO_DIR="$RAIZ/.despliegue"
ESPERA="${DEPLOY_ESPERA:-180}"
DESCARGAR=si
for arg in ${@+"$@"}; do
  case "$arg" in
    --sin-descargar) DESCARGAR=no ;;
    -h | --help) sed -n '4,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Opción desconocida: $arg" >&2; exit 2 ;;
  esac
done

# --- Utilidades -------------------------------------------------------------------------------
paso() { printf '\n==> %s\n' "$*"; }
info() { printf '    %s\n' "$*"; }
aviso() { printf '    AVISO: %s\n' "$*"; }
ok() { printf '    OK     %s\n' "$*"; }
falla() { printf '    FALLO  %s\n' "$*"; FALLOS=$((FALLOS + 1)); }
error() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }
FALLOS=0

# Lee una variable del .env sin ejecutarlo (la última aparición manda; sin comillas exteriores).
leer_env() {
  local valor
  valor="$(sed -n "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*//p" .env | tail -n 1 | sed 's/[[:space:]]*$//')"
  valor="${valor#\"}"; valor="${valor%\"}"; valor="${valor#\'}"; valor="${valor%\'}"
  printf '%s' "$valor"
}
dc() { docker compose -f compose.yaml -f compose.produccion.yaml "$@"; }
# psql dentro del contenedor de la base, con sus propias variables.
# shellcheck disable=SC2016  # las variables se expanden dentro del contenedor
sql() { dc exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "$0"' "$1"; }
corriendo() { [ -n "$(dc ps -q --status running "$1" 2>/dev/null)" ]; }
puerto_ocupado() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }

# --- 1. Comprobaciones previas ----------------------------------------------------------------
paso "1/10 Comprobaciones previas"
command -v docker >/dev/null || error "Docker no está instalado (docs/operacion.md §1)."
docker info >/dev/null 2>&1 || error "No hay acceso a Docker. Ejecuta el script con sudo."
version="$(docker compose version --short 2>/dev/null || true)"
[ -n "$version" ] || error "Falta Docker Compose v2 (docker compose)."
mayor="${version%%.*}"; resto="${version#*.}"; menor="${resto%%.*}"
if [ "$mayor" -lt 2 ] || { [ "$mayor" -eq 2 ] && [ "$menor" -lt 24 ]; }; then
  error "Docker Compose $version es antiguo: hace falta la 2.24 o posterior."
fi
for orden in git curl; do command -v "$orden" >/dev/null || error "Falta la orden «${orden}»."; done
[ -f .env ] || error "Falta el archivo .env en $RAIZ. Copia aquí el .env de producción."
chmod 600 .env
grep -vE '^[[:space:]]*(#|$)' .env | grep -qE '(CAMBIAR|<[a-z_-]+>)' && error "El .env tiene valores sin rellenar (CAMBIAR o <…>)."
DOMINIO="$(leer_env SITE_ADDRESS)"
ORIGEN="$(leer_env PUBLIC_ORIGIN)"
PROYECTO="$(leer_env COMPOSE_PROJECT_NAME)"; PROYECTO="${PROYECTO:-trail-penasagra}"
COPIAS_DIR="$(leer_env COPIAS_DIR)"; COPIAS_DIR="${COPIAS_DIR:-/srv/copias-trail}"
case "$DOMINIO" in "" | :* | *://*) error "SITE_ADDRESS debe ser el dominio, sin https:// (ahora: «${DOMINIO}»)." ;; esac
[ "$ORIGEN" = "https://$DOMINIO" ] || aviso "PUBLIC_ORIGIN ($ORIGEN) no es https://$DOMINIO."
mkdir -p "$COPIAS_DIR" "$ESTADO_DIR"
if [ -z "${DEPLOY_LOG:-}" ]; then
  DEPLOY_LOG="$COPIAS_DIR/despliegue-$(date +%Y%m%d-%H%M%S).log"
  export DEPLOY_LOG
fi
# En la relanzada tras descargar, la salida ya pasa por el registro.
[ "${DEPLOY_RELANZADO:-}" = 1 ] || exec > >(tee -a "$DEPLOY_LOG") 2>&1
info "Docker Compose $version · proyecto $PROYECTO · dominio $DOMINIO"
info "Registro: $DEPLOY_LOG"
dc config >/dev/null || error "La configuración de Compose no es válida (revisa el .env)."
ok "configuración válida"

# --- 2. Código --------------------------------------------------------------------------------
paso "2/10 Código"
git_() { git -c safe.directory="$RAIZ" "$@"; }
if [ "$DESCARGAR" = si ] && [ "${DEPLOY_RELANZADO:-}" != 1 ]; then
  [ -z "$(git_ status --porcelain --untracked-files=no)" ] ||
    error "Hay cambios locales en archivos del repositorio (git status). Deshazlos antes de desplegar."
  antes="$(git_ rev-parse HEAD)"
  git_ pull --ff-only || error "No se ha podido descargar el código (git pull)."
  if ! git_ diff --quiet "$antes" HEAD -- deploy.sh; then
    info "deploy.sh ha cambiado: se relanza la versión nueva."
    DEPLOY_RELANZADO=1 exec "$RAIZ/deploy.sh" ${@+"$@"}
  fi
fi
ok "versión $(git_ log -1 --format='%h %s' | cut -c1-90)"

# Web anterior: otros contenedores que publican los puertos 80 o 443 (no los de este proyecto).
ANTERIOR_PROYECTO=""; ANTERIOR_DIR=""; ANTERIOR_SUELTOS=""
while IFS='|' read -r id proyecto carpeta puertos; do
  [ -n "$id" ] || continue
  [ "$proyecto" = "$PROYECTO" ] && continue
  grep -Eq ':(80|443)->' <<<"$puertos" || continue
  if [ -n "$proyecto" ]; then ANTERIOR_PROYECTO="$proyecto"; ANTERIOR_DIR="$carpeta"
  else ANTERIOR_SUELTOS="$ANTERIOR_SUELTOS $id"; fi
done <<EOF
$(docker ps --format '{{.ID}}|{{.Label "com.docker.compose.project"}}|{{.Label "com.docker.compose.project.working_dir"}}|{{.Ports}}')
EOF
manual="$(leer_env WEB_ANTERIOR_DIR)"
[ -n "$manual" ] && ANTERIOR_DIR="$manual"
if [ -n "$ANTERIOR_PROYECTO$ANTERIOR_SUELTOS" ]; then
  info "Web anterior en 80/443: ${ANTERIOR_PROYECTO:-contenedores$ANTERIOR_SUELTOS} ${ANTERIOR_DIR:+($ANTERIOR_DIR)}"
fi

# --- 3. Copia previa --------------------------------------------------------------------------
paso "3/10 Copia de seguridad previa"
if corriendo db && [ "$(sql "SELECT to_regclass('public.ediciones') IS NOT NULL" 2>/dev/null)" = t ]; then
  infra/scripts/backup.sh "$COPIAS_DIR"
  ok "copia en $COPIAS_DIR"
else
  info "No hay una base en marcha: no hace falta copia."
fi

# --- 4. Construcción y esquema ----------------------------------------------------------------
paso "4/10 Construcción y esquema de la base"
dc build
dc up -d --wait db
dc run --rm -T api alembic upgrade head
ok "esquema al día"

# --- 5. Datos iniciales (solo en una base vacía) ----------------------------------------------
paso "5/10 Datos iniciales"
ediciones="$(sql 'SELECT count(*) FROM ediciones')"
if [ "$ediciones" = 0 ]; then
  dc run --rm -T api python -m app.cli importar-inicial
  csv_dir="$(leer_env CSV_2026_DIR)"
  if [ -z "$csv_dir" ] && [ -n "$ANTERIOR_DIR" ]; then
    encontrado="$(find "$ANTERIOR_DIR" -maxdepth 4 -name Clasificacion_27km.csv -path '*2026*' 2>/dev/null | head -n 1 || true)"
    [ -z "$encontrado" ] || csv_dir="$(dirname "$encontrado")"
  fi
  if [ -n "$csv_dir" ] && [ -d "$csv_dir" ]; then
    info "Clasificaciones de 2026 desde $csv_dir"
    while IFS='|' read -r carrera archivo titulo; do
      if [ -f "$csv_dir/$archivo" ]; then
        dc run --rm -T api python -m app.cli importar-clasificacion --carrera "$carrera" --edicion 2026 \
          --titulo "$titulo" --archivo "$archivo" --publicar <"$csv_dir/$archivo"
      else
        aviso "no está $csv_dir/$archivo: súbela desde el panel (Clasificaciones)."
      fi
    done <<'EOF'
trail-27k|Clasificacion_27km.csv|Clasificación Trail Peñasagra 2026
speed-14k|Clasificacion_14km.csv|Clasificación Speed Trail 2026
familiar-7k|Clasificacion_marcha.csv|Clasificación Familiar Peñasagra 2026
EOF
  else
    aviso "no se encuentran los CSV de 2026 (define CSV_2026_DIR en el .env o súbelos desde el panel)."
  fi
  ok "datos iniciales cargados"
else
  info "La base ya tiene datos: no se importa nada (no se sobrescribe)."
fi

# --- 6. Cuenta del panel ----------------------------------------------------------------------
paso "6/10 Cuenta del panel"
ADMIN_USUARIO="$(leer_env ADMIN_USUARIO)"
cuentas="$(dc run --rm -T api python -m app.cli listar-admins)"
if grep -q 'No hay administradores' <<<"$cuentas"; then
  ADMIN_PASSWORD="$(leer_env ADMIN_PASSWORD)"
  if [ -n "$ADMIN_USUARIO" ] && [ -n "$ADMIN_PASSWORD" ]; then
    printf '%s\n' "$ADMIN_PASSWORD" |
      dc run --rm -T api python -m app.cli crear-admin "$ADMIN_USUARIO" --password-stdin
    ok "cuenta «${ADMIN_USUARIO}» creada (la contraseña está en ADMIN_PASSWORD del .env)"
  else
    aviso "no hay cuentas y faltan ADMIN_USUARIO o ADMIN_PASSWORD en el .env."
    aviso "créala con: docker compose -f compose.yaml -f compose.produccion.yaml run --rm api python -m app.cli crear-admin <usuario>"
  fi
else
  info "Ya hay cuentas del panel: no se cambia ninguna."
fi

# --- 7. Web anterior --------------------------------------------------------------------------
paso "7/10 Web anterior"
PARADA=no
volver_a_la_anterior() {
  if [ -n "$ANTERIOR_PROYECTO" ]; then
    if [ -d "$ANTERIOR_DIR" ]; then (cd "$ANTERIOR_DIR" && docker compose -p "$ANTERIOR_PROYECTO" up -d)
    else docker compose -p "$ANTERIOR_PROYECTO" up -d; fi
  fi
  if [ -n "$ANTERIOR_SUELTOS" ]; then
    # shellcheck disable=SC2086
    docker start $ANTERIOR_SUELTOS >/dev/null
  fi
}
if [ -n "$ANTERIOR_PROYECTO$ANTERIOR_SUELTOS" ]; then
  {
    echo "proyecto=$ANTERIOR_PROYECTO"; echo "carpeta=$ANTERIOR_DIR"; echo "contenedores=$ANTERIOR_SUELTOS"
    echo "parada=$(date '+%Y-%m-%d %H:%M:%S')"
  } >"$ESTADO_DIR/web-anterior"
  if [ -n "$ANTERIOR_PROYECTO" ]; then
    info "Parando «${ANTERIOR_PROYECTO}» (sin borrar sus datos)…"
    if [ -d "$ANTERIOR_DIR" ]; then (cd "$ANTERIOR_DIR" && docker compose -p "$ANTERIOR_PROYECTO" down)
    else docker compose -p "$ANTERIOR_PROYECTO" down; fi
  fi
  if [ -n "$ANTERIOR_SUELTOS" ]; then
    # shellcheck disable=SC2086
    docker stop $ANTERIOR_SUELTOS >/dev/null
  fi
  PARADA=si
  ok "web anterior parada; datos en $ESTADO_DIR/web-anterior"
else
  info "Ninguna otra web ocupa los puertos 80/443."
fi
if ! corriendo web; then
  for p in 80 443; do
    if puerto_ocupado "$p"; then
      [ "$PARADA" = si ] && volver_a_la_anterior
      error "El puerto $p está ocupado por un programa que no es Docker. Libéralo y repite."
    fi
  done
fi

# --- 8. Arranque ------------------------------------------------------------------------------
paso "8/10 Arranque"
dc up -d --remove-orphans
CURL_TLS=""
case "$DOMINIO" in *.localhost) CURL_TLS="-k" ;; esac # solo ensayos: certificado de la CA interna
https_() { # https_ <host> <ruta> [opciones de curl…]
  local host="$1" ruta="$2"; shift 2
  curl -s $CURL_TLS --max-time 10 --resolve "$host:443:127.0.0.1" "$@" "https://$host$ruta"
}
info "Esperando a https://$DOMINIO/api/ready (hasta $ESPERA s; la primera vez Caddy pide el certificado)…"
inicio=$SECONDS; listo=no
while [ $((SECONDS - inicio)) -lt "$ESPERA" ]; do
  r="$(https_ "$DOMINIO" /api/ready || true)"
  case "$r" in *'"disponible"'*) listo=si; break ;; esac
  sleep 3
done
if [ "$listo" != si ]; then
  echo; echo "---- Últimas líneas de web y api ----"
  dc logs --tail 40 web api || true
  if [ "$PARADA" = si ]; then
    paso "Vuelta atrás: la web nueva no responde; se recupera la anterior"
    dc down
    volver_a_la_anterior
    error "La web nueva no respondió en $ESPERA s. La web anterior vuelve a estar en marcha; los datos de la nueva se conservan."
  fi
  error "La web no respondió en $ESPERA s. Revisa los registros: docker compose -f compose.yaml -f compose.produccion.yaml logs web api"
fi
ok "https://$DOMINIO/api/ready → disponible ($((SECONDS - inicio)) s)"

# --- 9. Comprobaciones ------------------------------------------------------------------------
paso "9/10 Comprobaciones (docs/operacion.md §6)"
r="$(curl -s -o /dev/null --max-time 10 --resolve "$DOMINIO:80:127.0.0.1" -w '%{http_code} %{redirect_url}' "http://$DOMINIO/" || true)"
[ "$r" = "308 https://$DOMINIO/" ] && ok "HTTP → HTTPS ($r)" || falla "HTTP → HTTPS: «${r}»"
r=""
for _ in 1 2 3 4 5 6 7 8 9 10; do
  r="$(https_ "www.$DOMINIO" /noticias -o /dev/null -w '%{http_code} %{redirect_url}' || true)"
  [ "$r" = "301 https://$DOMINIO/noticias" ] && break
  sleep 3
done
[ "$r" = "301 https://$DOMINIO/noticias" ] && ok "www → dominio principal ($r)" || falla "www.$DOMINIO: «${r}»"
cabeceras="$(https_ "$DOMINIO" / -I | tr '[:upper:]' '[:lower:]' || true)"
for c in content-security-policy strict-transport-security x-content-type-options referrer-policy; do
  grep -q "^$c:" <<<"$cabeceras" && ok "cabecera $c" || falla "falta la cabecera $c"
done
for ruta in /no-existe /pantallas; do
  r="$(https_ "$DOMINIO" "$ruta" -o /dev/null -w '%{http_code}' || true)"
  [ "$r" = 404 ] && ok "$ruta → 404" || falla "$ruta → $r (se esperaba 404)"
done
actual="$(dc run --rm -T api alembic current 2>/dev/null || true)"
grep -q '(head)' <<<"$actual" && ok "base en la última versión del esquema" || falla "alembic current no está en head"
if command -v openssl >/dev/null; then
  emisor="$(echo | openssl s_client -connect 127.0.0.1:443 -servername "$DOMINIO" 2>/dev/null | openssl x509 -noout -issuer 2>/dev/null || true)"
  info "Certificado: ${emisor:-no se ha podido leer}"
fi

# --- 10. Copias programadas y limpieza -------------------------------------------------------
paso "10/10 Copias programadas y limpieza"
if [ "$(leer_env COPIAS_PROGRAMADAS)" = no ]; then
  info "Copias programadas desactivadas (COPIAS_PROGRAMADAS=no)."
elif command -v crontab >/dev/null; then
  marca="# trail-penasagra-copias"
  linea="0 4 * * * cd $RAIZ && PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin infra/scripts/backup.sh $COPIAS_DIR >>$COPIAS_DIR/copias.log 2>&1; find $COPIAS_DIR -maxdepth 1 -type f \\( -name 'trail-*.dump' -o -name 'media-*.tgz' \\) -mtime +14 -delete $marca"
  # Se lee la tabla entera antes de escribirla: conserva las demás tareas y sustituye la nuestra.
  actual="$(crontab -l 2>/dev/null || true)"
  { [ -z "$actual" ] || grep -vF "$marca" <<<"$actual" || true; echo "$linea"; } | crontab -
  ok "copia diaria a las 04:00 en $COPIAS_DIR (se conservan 14 días)"
else
  aviso "no hay crontab: programa la copia a mano (docs/operacion.md §7)."
fi
docker image prune -f >/dev/null && ok "imágenes sin uso eliminadas"

echo
echo "=============================================================="
if [ "$FALLOS" -eq 0 ]; then echo " Despliegue terminado: todo correcto."
else echo " Despliegue terminado con $FALLOS comprobación(es) fallida(s): revisa arriba."; fi
echo
echo " Web:    https://$DOMINIO"
echo " Panel:  https://$DOMINIO/admin  (usuario: ${ADMIN_USUARIO:-el que ya existía})"
echo "         La contraseña inicial está en ADMIN_PASSWORD del .env."
echo " Copias: $COPIAS_DIR   ·   Registro: $DEPLOY_LOG"
if [ -f "$ESTADO_DIR/web-anterior" ]; then
  echo
  ant_proyecto="$(sed -n 's/^proyecto=//p' "$ESTADO_DIR/web-anterior")"
  ant_carpeta="$(sed -n 's/^carpeta=//p' "$ESTADO_DIR/web-anterior")"
  ant_sueltos="$(sed -n 's/^contenedores=//p' "$ESTADO_DIR/web-anterior")"
  echo " Volver a la web anterior si hiciera falta (sus datos se conservan):"
  echo "   cd $RAIZ && docker compose -f compose.yaml -f compose.produccion.yaml down"
  [ -z "$ant_proyecto" ] || echo "   cd $ant_carpeta && docker compose -p $ant_proyecto up -d"
  [ -z "$ant_sueltos" ] || echo "   docker start$ant_sueltos"
fi
echo "=============================================================="
[ "$FALLOS" -eq 0 ]
