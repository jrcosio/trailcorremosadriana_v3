# Documentación de referencia

Copia mantenible de la documentación funcional aprobada, para que las decisiones
del proyecto no dependan de la carpeta `datos_iniciales/` (ignorada por Git y por
Docker, y tratada como fuente de solo lectura).

## Procedencia

| Origen | Ubicación local de consulta | Identificación |
|---|---|---|
| Propuesta aprobada y documentación funcional | `datos_iniciales/Trail_Penasagra_Desarrollo/` | Exportación 2026-11-19, commit fuente `9e0768887bcdfac5c361a4c4256ff59d76b5c296` (ver `PROCEDENCIA_PAQUETE.json`) |
| Web en producción (Reflex) | `datos_iniciales/trailcorremosadriana_v2/` | Repositorio `jrcosio/trailcorremosadriana_v2`, commit `1799a73`, licencia MIT (© 2026 José Ramón Blanco) |

Copiado el 2026-11-19 sin modificaciones de contenido:

- `00_GUIA_LECTURA.md` … `14_BACKEND_FASTAPI_POSTGRESQL.md`
- `screens/publica/*.md` (16 fichas) y `screens/admin/*.md` (24 fichas)
- `pantallas.json`, `INVENTARIO_RECURSOS.csv`
- `LEEME_PAQUETE.md`, `AGENTS_PAQUETE.md`, `PROCEDENCIA_PAQUETE.json` (renombrados para no confundirlos con los del proyecto)

Los enlaces relativos de estos documentos que apuntan a `../proyecto/...` o
`../contenido/...` se refieren al paquete original; en este repositorio el
código vive en `frontend/`, `backend/` e `infra/`.

## Documentos propios del proyecto

- [DISCREPANCIAS.md](DISCREPANCIAS.md): diferencias detectadas entre fuentes y cómo se resuelven.
- [../ROADMAP.md](../ROADMAP.md) y [../ESTADO_PROYECTO.md](../ESTADO_PROYECTO.md): avance y punto de continuidad.
- [../arquitectura.md](../arquitectura.md): decisiones técnicas de la implementación (a partir de la feature 001).

## Orden de autoridad

1. Instrucciones del propietario (prompt de desarrollo y nuevas indicaciones).
2. Decisiones aprobadas y especificaciones de esta carpeta.
3. Código de la propuesta, para conservar apariencia y comportamiento.
4. Código de producción, para recuperar contenido, recursos y reglas útiles.
