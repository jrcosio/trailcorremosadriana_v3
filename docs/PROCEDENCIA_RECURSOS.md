# Procedencia y licencias de recursos reutilizados

Fuentes (consultadas en `datos_iniciales/`, que no se versiona):

- **PROP**: propuesta aprobada `Trail_Penasagra_Desarrollo/proyecto`, commit fuente
  `9e0768887bcdfac5c361a4c4256ff59d76b5c296` (exportación 2026-11-19).
- **PROD**: web en producción `trailcorremosadriana_v2`, commit `1799a73`, licencia MIT
  (© 2026 José Ramón Blanco).

## Código

| Destino | Origen | Cambios |
|---|---|---|
| `frontend/src/components/{Site,Results,ClassificationTable,DorsalSolidario}.tsx`, `frontend/src/components/admin/*.tsx` | PROP `components/` | Se quita `'use client'` |
| `frontend/src/lib/{data,classifications,registration}.ts` | PROP `lib/` | Ninguno |
| `frontend/src/styles/globals.css` | PROP `app/globals.css` | Ninguno (los arreglos van en `ajustes.css`) |
| `frontend/tests/{solidario,clasificaciones}.test.tsx` | PROP `scripts/check-solidarity.tsx`, `scripts/check-classifications.tsx` | Portado a vitest (partes de cliente) |
| `frontend/src/seo/rutas.ts` (títulos de `/`, `/recorridos`, `/galeria`, `/clasificaciones`, `/reglamento`, `/contacto`) | PROD `trailcorremosadriana_v2.py` | Títulos conservados; descripciones adaptadas |
| `backend/seed/contenido_inicial.json` | PROP `lib/data.ts` (`seed`) | Volcado a JSON (ver `backend/seed/README.md`) |
| `backend/seed/noticias/2026-07-13-gracias-trail-2026.json` | PROD `datos/noticias/2026-07-13-gracias-trail-2026.txt` | Campos adaptados al contrato (`subtitulo` → `excerpt`); texto íntegro |

## Fuentes tipográficas

| Archivo | Familia | Licencia |
|---|---|---|
| `frontend/public/fonts/barlow-{0,1,2}.woff2`, `barlow.css` | Barlow Condensed 600/700/800 | SIL Open Font License 1.1 (`fonts/licencias/Barlow_Condensed_OFL.txt`) |
| `frontend/public/fonts/manrope-{0..4}.woff2`, `manrope.css` | Manrope 400–800 | SIL Open Font License 1.1 (`fonts/licencias/Manrope_OFL.txt`) |

**Formato (feature 011, DISCREPANCIAS C4).** Los archivos de PROP tenían extensión `.woff2` pero
contenían TrueType.

- **Conversión**: a WOFF2 real con fontTools 4.55.0 (`fonttools ttLib.woff2 compress`), que no
  pierde información en los contornos. Se conservan los nombres de archivo y las licencias OFL;
  un cambio de formato no es una «Modified Version» según la FAQ de la OFL.
- **Peso**: 743.164 → 250.840 bytes (−66 %).
- **Aspecto**: capturas idénticas píxel a píxel a 360/768/1024/1440 px.

## Imágenes

Copiadas desde PROP `public/`. Las de `reused/` son byte a byte idénticas a las de PROD `assets/`
(comprobado con SHA-256 el 2026-11-19).

**Licencia**: fotografías, logotipos y silueta son materiales aportados por el propietario o
reutilizados de su web. La licencia MIT de PROD cubre el código, no estas imágenes, y no se
concede una licencia genérica a terceros. Su uso se limita a la web de la carrera. Antes de cada
lanzamiento hay que confirmar las autorizaciones de publicación e imagen
(`docs/referencia/11_RECURSOS_Y_LICENCIAS.md`).

| Archivo | Origen | Uso |
|---|---|---|
| `reused/fondos/fondo.webp` | PROD `assets/fondos/fondo.webp` | Fondo de la portada, del acceso y de reserva |
| `reused/logos/logo1.webp` | PROD `assets/logos/logo1.webp` | Favicon. La web y el panel usan el logotipo nuevo: el pie desde la decisión P8, y la barra lateral y el acceso del panel desde la decisión P11 |
| `reused/logos/nombre_desktop.webp`, `nombre_mobile.webp` | PROD `assets/logos/` | Reserva (sin uso actual) |
| `reused/logos/logo_cabecera-{480,720}.webp` | Aportado por el propietario el 2026-11-21 (`datos_iniciales/new_logo.png`, 2172 × 724, 393 KB; feature 012, decisión P7) | Logotipo de la cabecera pública. Recortado a su contenido transparente, redimensionado con Lanczos a 480 y 720 px de ancho y convertido a WebP con calidad 90 y alfa sin pérdidas (Pillow) |
| `reused/logos/logo_pie-{480,720}.webp` | Derivado del mismo `datos_iniciales/new_logo.png` el 2026-11-21 (feature 012, decisión P8) | Logotipo del pie y, desde P11, de la barra lateral y de la pantalla de acceso del panel, en negativo para los fondos oscuros. Mismo recorte que el de la cabecera. La tinta oscura (texto y montañas) se mezcla hacia el blanco según su canal rojo; el naranja y el alfa no cambian. Sin redibujar nada. Redimensionado con Lanczos a 480 y 720 px y convertido a WebP con calidad 90 (Pillow). Se sustituye si el propietario aporta una versión oficial para fondo oscuro |
| `reused/logos/corremos_por_adriana.webp` | PROD `assets/logos/` | Imagen para compartir (OG) |
| `reused/img/{trail,speed_trail,familiar_trail}_inscripciones.webp` | PROD `assets/img/` | Fotos reales de las carreras |
| `reused/img/dorsal_solidario.webp` | PROD `assets/img/` | Foto real de la causa |
| `reused/logos/patrocinadores/banner_*.png` (8) | PROD `assets/logos/patrocinadores/` | Logotipos de patrocinadores |
| `reused/noticias/gracias_2026.webp` | PROD `assets/noticias/img/gracias_2026.webp` (feature 007) | Imagen de la noticia «¡Gracias por un Trail 2026 inolvidable!» |
| `images/adriana-silueta.png` | PROP `public/images/`, aportada por el propietario | Silueta de Adriana (máscara CSS) |
| `templates/clasificacion.csv` | PROP `public/templates/` | Plantilla CSV con datos ficticios (nunca se importa como oficial) |

No se copian `favicon.svg` (icono genérico del starter), `contenido/media/*.png` (datos de prueba
D2/D3) ni el CSS de shadcn de `vendor/`.
