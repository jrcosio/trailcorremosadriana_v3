# Plan propuesto de continuación

Prioridad aprobada: implementar el backend FastAPI y la base de datos PostgreSQL conforme a [14_BACKEND_FASTAPI_POSTGRESQL.md](14_BACKEND_FASTAPI_POSTGRESQL.md), conservando el frontend y las decisiones visuales. Las fases siguientes se ejecutan dentro de esa migración; no implican mantener D1 como arquitectura final.

## Fase 1 · Arranque y comprobación

Instalar con el lockfile, generar acceso local, aplicar la migración en una base vacía e importar el contenido público. Recorrer el mapa de pantallas. Ejecutar tipos, compilación y pruebas relevantes. Registrar incidencias reproducibles.

**Salida:** proyecto ejecutable y lista contrastada de diferencias, sin rediseñar.

## Fase 2 · Estructura mantenible

Separar pantallas públicas en componentes por área, y login/resumen/listados/editores/ajustes del panel. Extraer tipos de dominio, validaciones y formularios compartidos. Sustituir tipos amplios de forma gradual. Mantener rutas, datos, apariencia y compatibilidad con registros ya existentes.

**Salida:** estructura clara que permita cambiar una pantalla sin editar un archivo monolítico.

## Fase 3 · Cierre funcional del CMS

Verificar cada operación de gestión, publicación, orden y archivos. Tratar conflictos y fallos sin perder datos introducidos. Revisar validaciones de números, años, enlaces y documentos. Definir exportación/copia de seguridad y mantenimiento de archivos retirados.

**Salida:** CMS coherente y verificable con persistencia real.

## Fase 4 · Edición y experiencia pública

Completar los datos que entregue la organización. Probar apertura/cierre, fecha/contador y todos los destinos. Mantener la causa y los recursos reales. Revisar 404, metadatos, accesibilidad, móvil, carga de imágenes y enlaces externos.

**Salida:** web lista para revisión editorial y de participación.

## Fase 5 · Preparación del despliegue

Elegir infraestructura, configurar nuevos recursos y secretos, aplicar migraciones, probar restauración y generar instrucciones. Si se publica en otro proveedor, adaptar los servicios sin rebajar la protección del administrador. Preparar el cambio de dominio como acción posterior y explícita.

**Salida:** versión revisable y proceso de publicación reproducible.

## Ampliaciones fuera del comportamiento actual

Correo entregado por backend, alta/cobro propio de participantes, sincronización automática con el proveedor de cronometraje y múltiples cuentas administradoras requieren definición adicional. No convertirlas silenciosamente en dependencias del lanzamiento básico.
