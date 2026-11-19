# Instrucciones para continuar Trail Peñasagra

Este es un paquete de continuidad, no una petición de rediseño libre.

1. Lee `LEEME.md`, `docs/01_PRODUCTO_Y_ALCANCE.md`, `docs/02_ESTILO_VISUAL.md`, `docs/03_MAPA_PANTALLAS.md`, `docs/08_ESTADO_Y_PENDIENTES.md` y `docs/10_PLAN_DESARROLLO.md` antes de cambiar comportamiento.
2. El código ejecutable está en `proyecto/`. Las fichas por pantalla están en `docs/screens/`.
3. Conserva fotografías, logotipos, silueta, tono deportivo y decisiones aprobadas. No sustituyas a las personas reales por imágenes generadas.
4. Mantén literalmente «TRAIL PENASAGRA» en el título principal salvo instrucción nueva del propietario. En el resto del sitio, el nombre habitual es «Trail Peñasagra».
5. El botón superior debe decir «INSCRIPCIONES». No vuelvas a introducir el rótulo «TRAIL PEÑASAGRA 2027» sobre el contador.
6. El dorsal solidario usa el enlace específico configurado en administración. Solo es clicable si las inscripciones están abiertas y existe una URL HTTPS válida. No lo redirijas a Contacto ni inventes un enlace de pago.
7. Los datos de 2026 son referencia histórica. No anuncies fecha, precio, recorrido ni inscripción de 2027 sin confirmación.
8. Protege las operaciones de escritura en el servidor. No reemplaces D1/R2 por localStorage ni implementes una autenticación únicamente visual.
9. Las vistas `/pantallas/admin` son demostraciones sin escritura. El panel real `/admin` requiere sesión propia.
10. Los archivos `contenido/` contienen solo datos publicados. No asumas que son una copia de borradores, usuarios o archivos privados.
11. Trabaja sobre una rama local. No publiques, cambies DNS ni sobrescribas la propuesta existente por el mero hecho de disponer de sus URLs.
12. No solicites credenciales de producción para empezar: genera un acceso local y usa datos de prueba.
13. Verifica lo afectado, documenta limitaciones y actualiza las fichas correspondientes. No afirmes que una función está terminada si sigue siendo un enlace, un estado de ejemplo o un envío por mailto.

14. Clasificaciones: importar un CSV por carrera y edición y dibujar la tabla desde sus filas. Conservar el mapeo de columnas, vista previa, sustitución íntegra y validación de servidor. El Dorsal Solidario no tiene clasificación ni puede seleccionarse en esta sección. Lee `docs/13_CLASIFICACIONES_CSV.md`.

La implementación actual concentra pantallas en `components/Site.tsx` y `components/admin/Admin.tsx`. Se puede modularizar conservando URLs y apariencia. Mantén las licencias incluidas.

15. El backend de destino aprobado es FastAPI con PostgreSQL, SQLAlchemy/Alembic, almacenamiento R2/S3 y Docker Compose. Lee `docs/14_BACKEND_FASTAPI_POSTGRESQL.md` antes de implementarlo. Distingue el código actual de la arquitectura prevista; esta entrega solo documenta esa migración.
