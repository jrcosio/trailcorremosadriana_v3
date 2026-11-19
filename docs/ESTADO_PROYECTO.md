# Estado del proyecto

Última actualización: 2026-11-19

## Punto de continuidad

- **Feature activa**: 001-base-proyecto (pendiente de iniciar)
- **Fase SDD**: — (preparación terminada)
- **Feature activa en Spec Kit**: `.specify/feature.json` (aún no existe)
- **Siguiente acción concreta**: `git switch -c 001-base-proyecto main` y `/speckit-specify` de la base
  del proyecto.

## Features

| Estado | Features |
|---|---|
| Terminadas | 0 (preparación) |
| Activa | — |
| Pendientes | 001 a 011 (ver [ROADMAP.md](ROADMAP.md)) |

## Decisiones tomadas

| Fecha | Decisión | Origen |
|---|---|---|
| 2026-11-19 | Próxima edición: 2027 sin fecha | Propietario (P1 en DISCREPANCIAS) |
| 2026-11-19 | Importar CSV reales de 2026 como clasificaciones publicadas | Propietario (P2) |
| 2026-11-19 | Estructura `frontend/`, `backend/`, `infra/` en la raíz | Prompt de desarrollo |
| 2026-11-19 | Frontend Vite + React SPA reutilizando el router interno de la propuesta; sin Vinext/Workers | Análisis del código (solo config, `worker/` y 6 route handlers dependían de Workers) |
| 2026-11-19 | `GET /api/content` como adaptador de solo lectura; escrituras por recurso; sin `PUT /api/content` | DOC 14 + DISCREPANCIAS M1 |
| 2026-11-19 | Datos de prueba de la exportación no se importan | DISCREPANCIAS D1–D4 |

## Supuestos

- El estado del evento se deriva (apertura + fecha + contador); no se crea un enum (M3).
- Los datos de carreras son referencia 2026 y se presentan como tal.
- `/pantallas` se mantiene como vista de revisión sin escritura hasta la feature 011.

## Pruebas ejecutadas

| Fecha | Feature | Prueba | Resultado |
|---|---|---|---|
| 2026-11-19 | 0 | `git check-ignore` sobre `datos_iniciales/` | Ignorada (regla `/datos_iniciales/`) |

## Bloqueos

Ninguno. Datos de producción pendientes del propietario (no bloquean): fecha 2027, enlaces de
inscripción y de pago solidario, webs de patrocinadores, reglamento definitivo, GPX.
