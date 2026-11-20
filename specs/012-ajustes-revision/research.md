# Research: Ajustes de la revisión (012)

## R1 Fotos completas sin mover el diseño (US1, P6)

- **Decisión**: `object-fit: contain` y `object-position: center` en los 11 marcos de foto. El
  fondo del propio `<img>` es el relleno de las franjas:

  ```css
  background: linear-gradient(rgb(23 46 40 / .82), rgb(23 46 40 / .82)),
              var(--foto, none) center / cover no-repeat #172e28;
  ```

  `--foto` lleva la URL de la imagen y se fija con `fondoFoto(src)` (`lib/fotos.ts`).
- **Por qué**:
  - No hay elementos nuevos ni cambios de estructura, así que los selectores aprobados (`.x>img`)
    y el apilado de los textos superpuestos no cambian.
  - El marco conserva su tamaño.
  - La misma URL ya está en caché.
  - React aplica `--foto` por CSSOM, que la CSP no restringe.
- **Alternativas descartadas**:
  - Marco con la proporción de la foto: alargaría las tarjetas hasta 960 px y descolocaría la
    cuadrícula.
  - Barras de color liso: el propietario pidió «sin barras vacías» y quedan pobres.
  - Copia desenfocada en un elemento hermano: exige cambiar el DOM y las reglas de 8 selectores.
- **Escapado**: en la URL de `--foto` se codifican `"`, `\` y los saltos de línea. Las referencias
  ya están validadas en el servidor (`/reused`, `/media`, `https`); es defensa en profundidad.
- **Fuera de alcance**: el visor y la vista previa de subida ya usan `contain`; los logotipos
  también. Los fondos decorativos son `background-image` con degradado y no se tocan (supuesto de
  la spec).

## R2 Verificación geométrica

`scripts/verificar-fotos.mjs` recorre las rutas con fotos a 320/360/768/1024/1440 px y el panel si
hay credenciales. Para cada `<img>` de foto comprueba:

- que `object-fit` es `contain`;
- que el rectángulo pintado de la foto (calculado con la proporción natural) queda dentro del área
  visible de sus ancestros con `overflow` distinto de `visible`;
- que hay relleno `--foto` cuando la proporción de la foto difiere más de un 2 % de la del marco;
- que el tamaño del marco coincide con el medido antes del cambio (referencia guardada en un JSON
  de la carpeta `capturas/`, ignorada).

## R3 Despliegue en la MV de la web anterior (US2)

- **Situación en la MV** (`datos_iniciales/trailcorremosadriana_v2`):
  - `docker-compose.yml` con `app` (Reflex) y `caddy:latest` en los puertos 80/443;
  - `Caddyfile` con `trailpeñasagra.com` y `www.trailpeñasagra.com` → redirección 301;
  - certificados en el volumen `caddy_data` de ese proyecto.
- **Puertos**: la v3 usa los mismos, así que el cambio consiste en parar la v2
  (`docker compose down`, **sin** `-v`, para poder volver) y arrancar la v3. Vuelta atrás: el
  inverso.
- **Certificados**: la v3 tiene su propio volumen `caddy_data` y pide certificados nuevos a Let's
  Encrypt al arrancar, sin problema de límites para dos nombres. Con el DNS y los puertos ya
  apuntando a la MV, la emisión es automática.
- **Dominio con «ñ»**:
  - Caddy normaliza el nombre (probado: un sitio escrito con «ñ» responde a un `Host` en
    *punycode*).
  - El navegador envía el origen en *punycode*, así que `normalizar_origen` pasa el nombre a
    ASCII (IDNA). `meta` usa el origen normalizado.
- **Redirección de `www`**:
  - archivo `infra/caddy/redireccion-www.caddy` (`www.{$SITE_ADDRESS}` →
    `redir {$PUBLIC_ORIGIN}{uri} permanent`);
  - lo monta solo `compose.produccion.yaml` en `/etc/caddy/sitios/`;
  - el Caddyfile principal hace `import /etc/caddy/sitios/*.caddy`; sin archivos es válido
    (probado).
- **HSTS**: `Strict-Transport-Security "max-age=31536000"`, sin `includeSubDomains`, para no
  afectar a otros subdominios. Los navegadores lo ignoran por HTTP, así que no molesta en local.
- **Datos**: instalación limpia, sin restos de las pruebas locales:
  - `importar-inicial`;
  - las 3 clasificaciones de 2026 con `importar-clasificacion` desde los CSV que ya están en la
    MV, en la carpeta de la v2 (`datos/2026/`);
  - `crear-admin`.
- **Ensayo**: clon limpio, proyecto `trail-prod-ensayo`, `compose.produccion.yaml`,
  `SITE_ADDRESS=trailpeñasagra.localhost` y `PUBLIC_ORIGIN=https://trailpeñasagra.localhost`
  (con «ñ», para probar la normalización); puertos 80/443 de esta máquina y certificado interno de
  Caddy (los `.localhost` no usan ACME).
