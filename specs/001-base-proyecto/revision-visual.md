# Revisión visual — feature 001

Fecha: 2026-11-19 · Herramienta: `frontend/scripts/capturas.mjs` (Playwright/Chromium)

- **Local**: `http://localhost:8080` (Compose: Caddy + API + PostgreSQL)
- **Referencia**: `https://trail-penasagra-nueva-web.jrblanco.chatgpt.site` (propuesta publicada)
- **Rutas**: `/`, `/carreras`, `/carreras/trail-27k`, `/inscripciones`, `/solidaridad`,
  `/patrocinadores`, `/contacto`, `/noticias`, `/galeria`, `/clasificaciones`, `/reglamento`
- **Anchos**: 360, 768, 1024 y 1440 px (44 capturas por sitio, página completa)

## Desbordamiento horizontal

| Sitio | Antes del ajuste | Después del ajuste A-001 |
|---|---|---|
| Referencia publicada | 11/44 (todas las rutas a 360 px, `scrollWidth` 369) | — |
| Local | 11/44 (mismo defecto heredado) | **0/44** |

Causa: a 360 px el botón de menú de la cabecera (`.menu-toggle`) sobresalía 9 px. Corrección
mínima en `frontend/src/styles/ajustes.css` (A-001): menos espaciado entre elementos de la
cabecera por debajo de 400 px. `globals.css` sigue idéntica a la propuesta. A 360 px el icono de
menú ahora se ve completo (en la referencia aparecía cortado).

Comprobación adicional de anchos: 360, 375, 390, 414 y 480 px sin desbordamiento. A 320 y 340 px
todavía desborda (357 px), pero esos anchos están por debajo del mínimo de aceptación (360 px).
Queda anotado para la feature 011.

## Comparación de textos (1440 px, cifras del contador normalizadas)

| Ruta | Resultado | Diferencia |
|---|---|---|
| `/clasificaciones`, `/contacto`, `/galeria`, `/noticias`, `/solidaridad` | Igual | — |
| `/` | Esperada | Contador «—» y «La fecha de 2027 está por confirmar» frente a la fecha de prueba (D1) |
| `/carreras` | Esperada | «edición 2027» frente a «edición 2028» (D1) |
| `/carreras/trail-27k` | Esperada | «Fecha por confirmar» frente a la fecha de prueba (D1) |
| `/inscripciones` | Esperada | «Trail Peñasagra 2027 · Fecha por confirmar» (D1) |
| `/patrocinadores` | Esperada | Sin colaborador de prueba «boc»; se muestra el estado vacío aprobado (D3) |
| `/reglamento` | Esperada | Sin el párrafo «PRUEBA» (D4) |

## Inspección de imágenes

- Inicio a 1440 px: composición, tipografías, colores, título «TRAIL PENASAGRA», silueta,
  bloque del Dorsal Solidario, noticia, galería, patrocinadores grandes y pie: idénticos. Única
  diferencia: la tarjeta 27K muestra la foto real (`trail_inscripciones.webp`) en lugar de la
  silueta subida por error (D2).
- Inicio a 360 px (parte superior): idéntico salvo el contador sin fecha (D1) y el icono de menú
  completo (A-001).

Resultado: **sin diferencias** de textos, imágenes ni composición, salvo las derivadas de excluir
los datos de prueba D1–D4 y de la corrección A-001 (SC-002 cumplido).
