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

## R4 Logotipo nuevo en la cabecera (US3, P7)

- **Origen**: `datos_iniciales/new_logo.png`, de 2172 × 724 px y 393 KB, RGBA con fondo
  transparente.
  - Contenido útil: (55, 15)–(2161, 684).
  - Colores: texto casi negro, montañas en verde `#1b4433` y silueta en naranja.
- **Variantes**:
  - Recorte al contenido con 6 px de margen: 2118 × 681, proporción 3,11.
  - Redimensionado con Lanczos a 480 × 154 y 720 × 232.
  - WebP con calidad 90 y alfa sin pérdidas (Pillow): unos 26 KB y 40 KB. El WebP sin pérdidas
    pesaba más (32 KB y 68 KB) sin diferencia visible.
- **Tamaño en pantalla**: lo limita la altura de la cabecera, que no cambia. El logotipo no supera
  el ancho de la marca anterior, medida antes del cambio:

  | Tramo | Cabecera | Marca anterior (ancho) | Altura del logotipo | Ancho resultante |
  |---|---|---|---|---|
  | ≥ 1201 px | 92 px | 261 px | 80 px | ≈ 249 px |
  | 1001–1200 px | 92 px | 219 px | 70 px | ≈ 218 px |
  | 701–1000 px | 80 px | 216 px | 68 px | ≈ 212 px |
  | 360–700 px | 75 px | 182 px | 58 px | ≈ 181 px |
  | < 360 px | 75 px | 155 px | 49 px | ≈ 153 px |

  El nombre dentro del logotipo ocupa el 22 % de su altura. Queda entre el 92 % y el 97 % del
  tamaño del texto anterior en cada tramo.
- **Nitidez**: `srcset` con 480w y 720w, y `sizes` igual al ancho de cada tramo. Una pantalla 2×
  o 3× descarga la de 720 cuando hace falta. `width`/`height` en el `<img>` reservan la
  proporción antes de la carga, así que la cabecera no salta.
- **Filtro**: la regla aprobada `.brand img` oscurece el icono anterior
  (`filter: brightness(.13)`). El logotipo nuevo lleva sus propios colores, así que se anula con
  `filter: none`.
- **Accesibilidad**: el enlace conserva `aria-label="Trail Peñasagra. Inicio"`. El `alt` del
  `<img>` describe el logotipo («Trail Peñasagra · Corremos por Adriana»), por si se quitara la
  etiqueta. El logotipo es texto en imagen, pero WCAG 1.4.5 exime los logotipos.
- **Alternativas descartadas**:
  - Servir el PNG original: 393 KB y 2172 px para mostrarse a 250 px.
  - SVG: no hay vectorial del propietario, y vectorizar a mano alteraría el dibujo.
  - Ampliar la cabecera para un logotipo mayor: movería todo el diseño aprobado.
  - Poner el logotipo también en el pie y en el panel: el texto oscuro no se lee sobre el verde
    oscuro (supuesto de la spec). *(La US4 lo cambia para el pie con una versión en negativo; véase
    R5.)*
- **Ajuste durante la implementación**:
  - El problema: a 360–371 px la cabecera ya iba justa (el botón de menú sobresalía unos 12 px de
    su contenedor, dentro del margen). Por eso el ancho de la marca decide dónde quedan
    «INSCRIPCIONES» y el menú, y un logotipo 1 px más estrecho los desplazaba 1 px.
  - La solución: el enlace conserva en cada tramo el ancho medido de la marca anterior (261,2 /
    218,8 / 215,7 / 181,8 / 155,2 px). El logotipo va dentro, alineado a la izquierda, y la
    posición del resto no depende de su ancho.
- **Medida de la nitidez**: con `srcset`, `naturalWidth` y `naturalHeight` vienen en píxeles CSS
  redondeados. El script mide los píxeles reales del archivo descargado (`currentSrc`).
- **Verificación** (`scripts/verificar-logo.mjs`):
  - Con `--referencia`, guarda la geometría de la cabecera antes del cambio.
  - Con `--comparar`, comprueba a 320–1440 px y en los anchos de cambio de diseño:
    - el logotipo cargado y completo;
    - que no supera el ancho anterior;
    - la cabecera con la misma altura;
    - la navegación, «INSCRIPCIONES» y el menú en la misma posición;
    - que no queda texto de marca en la cabecera;
    - que no hay desbordamiento;
    - la variante descargada (densidad 1 y 2);
    - el pie y el panel sin cambios.

## R5. Logotipo en el pie (US4, decisión P8)

- **Versión en negativo**: el pie tiene fondo `--forest-deep` (#10241e), así que el texto casi
  negro y las montañas verde oscuro del original no se leerían. La tinta tiene tres colores:
  - casi negro (texto), con R ≈ 0–32;
  - verde oscuro (montañas), con R ≈ 16–32;
  - naranja (niña y rayas), con R ≈ 208–240.

  Cada píxel se mezcla hacia el blanco según su rojo: k = (R − 80) / 80, limitado a [0, 1]. La
  tinta oscura pasa a blanco, el naranja queda igual y los bordes suavizados no hacen escalones.
  El alfa no cambia.
- **Mismo recorte que la cabecera**: contenido más 6 px, 2118 × 681. Variantes de 480 y 720 px
  (Lanczos, WebP con calidad 90).
- **Tamaño**: el ancho es el de la marca anterior del pie o el de la columna si es menor.
  - Marca anterior: silueta de 57 px, separación de 12 px y texto de 164,7 px, en total 233,7 px
    medidos. En CSS, 233 px.
  - Columna menor: 228 px a 701 px, donde el texto anterior ya se partía en dos líneas.

  Queda así:
  - el nombre «TRAIL PEÑASAGRA» del logotipo, ≈ 16 px de alto, frente a los 17 px de antes;
  - el logotipo, 74,8 px de alto (73,2 a 701 px), frente a los 52 de la marca anterior (64 a
    701 px).

  El resto de la primera columna baja 22,8 px. El pie crece según cómo se reparten las columnas
  en cada ancho:

  | Ancho | El pie crece |
  |---|---|
  | ≤ 700 px (primera columna a lo ancho) | 22,8 px |
  | 1000 px y 1200–1440 px | 11 px |
  | 701–768 px y 1001 px (las columnas de enlaces son más altas) | 0 px |
- **Carga diferida**: el pie queda fuera de la primera pantalla. El `<img>` lleva
  `loading="lazy"`, y `width`/`height` reservan su hueco.
- **Contraste**: el blanco y el naranja medidos sobre `--forest-deep` se comprueban en el script.
  El naranja debe tener al menos 3:1 (gráfico) y el blanco, al menos 4,5:1. WCAG exime los
  logotipos, pero se mide igualmente.
- **Componente**: `Logo` sirve a la cabecera y al pie (variante y `sizes`). `Brand`, con la
  silueta y el texto, deja de usarse en la web pública y se elimina. El panel tiene su propio
  marcado.
- **Alternativas descartadas**:
  - Logotipo original sobre una placa clara: añade un recuadro blanco que no está en el diseño.
  - `filter: brightness(0) invert(1)`: lo vuelve todo blanco y pierde el naranja de la niña.
  - Mantener el alto de 52 px: el lema quedaría con ≈ 5 px de alto, ilegible.
- **Ajustes durante la verificación**:
  - Problema 1: con `scroll-behavior: smooth`, un `scrollTo` no es instantáneo. La primera
    referencia midió una vista a mitad de animación, con 3 px de desfase.
    - Solución: el script se desplaza con `behavior: 'instant'` y mide en coordenadas de
      documento.
    - La referencia se repitió con el pie anterior, restaurado solo para medir.
  - Problema 2: por el mismo motivo, `cargarTodo` (`scripts/comun.mjs`) no llegaba al pie, así que
    las capturas no cargaban su logotipo diferido.
    - Solución: ahora también usa el desplazamiento instantáneo y baja hasta el final.
- **Verificación** (`scripts/verificar-logo.mjs`, ampliado):
  - Referencia nueva antes del cambio: `capturas/pie-antes-012.json`, con la huella de la marca
    anterior, las columnas y el contenido de la primera columna.
  - Con `--comparar`:
    - la cabecera, con 0 px de diferencia, como en la US3;
    - el pie con el logotipo en negativo, completo y sin deformar;
    - sin texto de marca y con el enlace a la portada;
    - el ancho, no mayor que el de la marca anterior ni que su columna;
    - las columnas 2.ª a 4.ª, con la misma `x` y el mismo ancho;
    - lo que baja, no más que lo que crece el logotipo;
    - el contraste;
    - la variante descargada en densidad 2;
    - el panel, sin cambios.

## R6. Frase de autoría del pie (US5, decisión P9)

- **Decisión**: en `Footer` (`Site.tsx`), la segunda línea de `.footer-bottom` pasa a ser el texto
  literal «Hecho por la Escuela Hacker Cosío», sin enlace. El aviso «© año Asociación Peñasagra»
  no cambia.
- **Estilo**: lo da la regla de `.footer-bottom` de `globals.css` (color #99afa1 y tamaño de la
  línea), así que no hace falta CSS nuevo. La regla de A-002 que subraya los enlaces de esa línea
  ya no tiene a qué aplicarse. Se conserva: si el propietario da una dirección, el enlace saldrá
  subrayado (AA) sin tocar el CSS. Su comentario lo indica.
- **Alternativas descartadas**:
  - Enlazar la frase a `jrblanco.es`: la frase ya no nombra a JR BLANCO y sería un enlace que el
    propietario no ha pedido.
  - Enlazar a una web de la Escuela Hacker Cosío: no hay dirección aprobada y no se inventan
    enlaces (constitución VI).
- **Verificación**:
  - vitest (`tests/pie.test.tsx`): renderiza `Site` en 13 rutas públicas, incluida una
    inexistente. Comprueba que la línea inferior tiene el aviso de copyright y la frase nueva, sin
    enlaces y sin restos de la frase anterior en toda la página. Falla antes del cambio.
  - `verificar-logo.mjs --comparar capturas/pie-antes-012.json`, ampliado con la línea inferior:
    las dos líneas, sin enlaces, con el mismo color y tamaño, y sin restos de la frase anterior.
    Detecta la frase anterior en la versión previa. La cabecera y el resto del pie se comprueban
    como en la US4.
  - axe, desbordamiento y capturas. Comparación píxel a píxel con las de la US4: solo cambia la
    línea inferior del pie.
