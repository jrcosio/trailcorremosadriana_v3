# Recursos gráficos y licencias

Todos los recursos de presentación locales del commit se incluyen en `proyecto/public/`. El inventario completo, con dimensiones y tamaño, está en `INVENTARIO_RECURSOS.csv`.

## Recursos que conservar

| Recurso | Uso |
|---|---|
| `reused/fondos/fondo.webp` | Paisaje original de la Sierra de Peñasagra, portada y otras franjas |
| `reused/logos/logo1.webp` | Logo de la carrera, cabecera y pie |
| `reused/logos/nombre_desktop.webp`, `nombre_mobile.webp`, `corremos_por_adriana.webp` | Recursos de marca heredados disponibles para referencia |
| `images/adriana-silueta.png` | PNG transparente suministrado por el propietario; reemplaza el corazón de la frase en portada |
| `reused/img/trail_inscripciones.webp` | Imagen real de la prueba larga |
| `reused/img/speed_trail_inscripciones.webp` | Imagen real de Speed Trail |
| `reused/img/familiar_trail_inscripciones.webp` | Imagen real de la prueba familiar |
| `reused/img/dorsal_solidario.webp` | Imagen real asociada a la causa/dorsal solidario |
| `reused/logos/patrocinadores/` | Ocho logotipos reutilizados, mostrados a mayor tamaño |
| `fonts/` | Archivos locales de Manrope y Barlow Condensed y sus CSS |

El PNG de la silueta se utiliza mediante máscara alfa CSS para darle color naranja; el archivo original permanece intacto. Evitar eliminar su transparencia o sustituir la figura.

## Fuentes y código

Se han incorporado los textos OFL recuperados de los directorios oficiales de Barlow Condensed y Manrope en el repositorio Google Fonts, dentro de `public/fonts/licencias/`. Conservarlos al redistribuir las fuentes. Algunas extensiones heredadas de fuentes son `.woff2` aunque sus CSS declaran formato truetype; comprobar formato antes de reconvertir u optimizar, conservando la apariencia.

La copia conserva los avisos de licencia de los componentes vendorizados: `scripts/vite/sites-vite-plugin.LICENSE` y `vendor/shadcn-tailwind-4.13.0.LICENSE.md`, además de las dependencias de `package-lock.json`.

Las fotografías y logos se incluyen como materiales aportados/reutilizados del proyecto del propietario; no se otorga mediante este paquete una licencia genérica a terceros. Confirmar autorizaciones de publicación e imagen de la edición correspondiente antes de un nuevo lanzamiento. No inventar una autorización de reutilización comercial fuera de la web de la carrera.

Los álbumes de Google Fotos se conservan como enlaces. No se han descargado todas las fotografías de esos servicios. `contenido/estado-exportacion.json` indica cuántos archivos `/media/` publicados se pudieron incorporar.
