# Criterios de aceptación

## Presentación

- El título de portada conserva «TRAIL PENASAGRA», mayor que en la primera propuesta.
- La frase «Corremos por Adriana.» tiene la silueta enviada, está ampliada y no muestra el corazón anterior.
- El botón de cabecera dice «INSCRIPCIONES» y abre esa página.
- No aparece el rótulo retirado sobre el contador.
- Los patrocinadores son legibles y grandes; las imágenes se contienen sin recortar ni deformar.
- No hay desbordamiento horizontal general a 360, 768, 1024 y 1440 px.

## Navegación y contenido

- Cada pantalla del mapa puede abrirse por su URL, incluso tras recargar.
- Un registro inexistente o no publicado no revela un borrador. La evolución del router debe ofrecer estado 404 apropiado.
- Los enlaces históricos y las rutas reales se conservan.
- La fecha no confirmada y los datos históricos no se presentan como información oficial nueva.

## Administración y persistencia

- Sin sesión, las lecturas privadas y escrituras se rechazan.
- Login correcto, error, bloqueo por intentos, caducidad y logout tienen estados verificables.
- Crear, editar y publicar sobreviven a recarga y otra sesión.
- Un borrador no aparece en la API pública.
- Una revisión obsoleta produce conflicto y no sobrescribe datos.
- Las vistas de diseño del panel no guardan contenido real.

## Dorsal e inscripciones

| Apertura global | URL solidaria | Resultado |
|---|---|---|
| Cerrada | Vacía | Aviso de próxima disponibilidad sin enlace |
| Cerrada | Válida | Mismo aviso, conservando URL en administración |
| Abierta | Vacía | Aviso de enlace pendiente, sin navegación alternativa |
| Abierta | HTTPS válida | «Pagar dorsal solidario» apunta exactamente al destino configurado |

No se aceptan URLs peligrosas. El mismo comportamiento debe observarse en portada, causa e inscripciones. Abrir solo el dorsal solidario debe ser posible.

## Clasificaciones CSV

- Un CSV por carrera y edición; la segunda importación sustituye el contenido del registro existente.
- El Dorsal Solidario no aparece como carrera clasificable ni como resultado público; el servidor rechaza nuevas clasificaciones de esa modalidad.
- Se asignan columnas obligatorias de posición, dorsal, nombre y tiempo; apellidos, categoría, club, sexo y estado son opcionales.
- Se muestra una vista previa antes de confirmar la importación. Los errores no sobrescriben los datos guardados.
- Las filas de no clasificados no reciben posición inventada; requieren un estado y admiten tiempo vacío.
- La tabla conserva tiempos y dorsales como texto, se ordena por la posición aportada, permite buscar participantes y filtrar por categoría/sexo.
- Los borradores siguen privados. La API valida filas, duplicados, sesión y revisión.

## Archivos y contacto

- Subidas válidas pueden recuperarse después; se rechazan formatos no admitidos y archivos que superen el límite.
- Se preserva la transparencia de los recursos que la tienen.
- Los GPX son descargables o consultables cuando existen. Las clasificaciones se importan desde CSV y se dibujan como tabla de participantes.
- El formulario no afirma un envío por servidor si sigue usando mailto.
- El visor de fotos admite cierre, teclado y foco accesible; revisar confinamiento del foco antes de darlo por cerrado.

## Entrega final de desarrollo

Comandos reproducibles, migraciones, variables documentadas sin secretos, capturas de revisión cuando se hayan producido, lista de cambios y limitaciones concretas. El despliegue y el dominio deben quedar separados de las credenciales de prueba.
