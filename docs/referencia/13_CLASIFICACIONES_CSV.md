# Clasificaciones desde CSV

Decisión del propietario: cada carrera tiene su propio CSV, del que se extraen los datos para representar la clasificación. El Dorsal Solidario no tiene clasificación y no aparece como opción ni como resultado.

## Flujo de la organización

1. Entrar en `/admin/clasificaciones` y añadir una clasificación.
2. Completar título, edición y carrera deportiva.
3. Seleccionar el CSV de esa carrera. Puede descargarse una plantilla desde el formulario.
4. Revisar las columnas detectadas y corregir su asignación si el proveedor utiliza otros nombres.
5. Comprobar los participantes de la vista previa y pulsar **Usar estos resultados**.
6. Activar **Visible en la web** cuando corresponda y pulsar **Guardar cambios**.
7. Consultar `/clasificaciones`. Para sustituir resultados, editar el mismo registro e importar el nuevo CSV.

La selección de archivo y la confirmación de la vista previa aún no publican nada. El guardado final usa la sesión, la validación del servidor y el control de revisión existente. La vista `/pantallas/admin/clasificaciones/nuevo` permite probar la importación visual sin persistir cambios.

## Archivo y columnas

- Extensión `.csv`; límite de 1 MB y 5.000 participantes por archivo.
- Cabecera obligatoria y datos separados por coma, punto y coma o tabulador.
- UTF-8, con o sin BOM; si no es UTF-8 válido se intenta Windows-1252.
- Admite campos entre comillas, separadores dentro de comillas, comillas duplicadas y saltos de línea Windows.
- Se ignoran filas completamente vacías; se rechaza un número desigual de columnas.
- Una columna solo se puede asignar a un campo. Las columnas no seleccionadas no se importan.

| Campo | Obligatorio | Tratamiento |
|---|---|---|
| Posición | Columna obligatoria | Entero positivo aportado por el cronometraje; admite NC, DNF, DNS, DSQ y otros estados previstos para no clasificados |
| Dorsal | Sí | Texto de hasta 30 caracteres; conserva ceros iniciales; único dentro de esa carrera |
| Nombre | Sí | Texto de hasta 200 caracteres después de combinar apellidos |
| Apellidos | No | Se concatena al nombre si se asigna |
| Tiempo | Columna obligatoria | Texto de hasta 60 caracteres, conservando el formato del proveedor; no se calculan tiempos nuevos |
| Categoría | No | Texto de hasta 150 caracteres |
| Club | No | Texto de hasta 150 caracteres |
| Sexo | No | Texto de hasta 60 caracteres, sin convertir etiquetas del proveedor |
| Estado | No | Texto de hasta 60 caracteres; necesario para filas sin posición |

Un clasificado con posición numérica necesita tiempo. Un participante sin posición necesita estado y puede tener el tiempo vacío. Se ordena por la posición general aportada; los no clasificados van al final y no reciben una posición inventada. Las posiciones y tiempos por categoría no se recalculan.

Plantilla incluida: `proyecto/public/templates/clasificacion.csv`. Sus tres filas son ejemplos ficticios para probar la importación; no son resultados oficiales ni se incluyen en el contenido publicado.

## Persistencia y compatibilidad

El CSV se lee en el navegador. Se envían y guardan únicamente las filas normalizadas y los metadatos del archivo (`sourceFile`, `importedAt`), no el texto original ni las columnas descartadas. No se almacena el CSV bruto en R2 ni se publica una descarga de ese archivo. `PUT /api/content` valida las filas en el servidor antes de persistirlas en D1.

La clave funcional es carrera (`raceId`) + edición (`year`). Existe un único registro por esa combinación. Importar otro archivo desde su editor sustituye todas sus filas; no añade participantes al CSV anterior. Cancelar una importación conserva el contenido anterior.

Se conserva el límite global de 3 MB del documento de contenido. Si la suma de todas las ediciones lo alcanza, la API rechaza el guardado; antes de ampliar mucho el histórico conviene migrar las filas a tablas separadas. El límite de 5.000 participantes por archivo no garantiza que muchos archivos de ese tamaño quepan simultáneamente en el documento.

Los registros heredados con enlaces, sin filas CSV, quedan fuera de la API pública y de las tablas. Siguen accesibles en la gestión para reimportarlos desde CSV. No se ha inventado una conversión de documentos antiguos. Los registros de Dorsal Solidario quedan excluidos de la interfaz de clasificaciones y de las nuevas altas del servidor, sin borrar datos históricos silenciosamente.

## Vista pública

Filtros por edición y carrera. Cada tabla permite buscar por nombre, dorsal o club, filtrar por categoría y sexo, y navegar en páginas de 50 participantes. Se muestran posición, dorsal, nombre y tiempo; las columnas opcionales solo aparecen cuando tienen datos. Los filtros mantienen la posición general oficial. Los datos se representan como texto, sin ejecutar HTML o fórmulas del archivo. En móvil, el desplazamiento horizontal queda dentro de la tabla.

## Código y verificación

- `lib/classifications.ts`: parser, asignación de columnas, normalización y exclusión solidaria.
- `lib/classification-schema.ts`: validación independiente de filas en el servidor.
- `components/admin/ClassificationImport.tsx` y `ClassificationManager.tsx`: lectura, vista previa y gestión.
- `components/Results.tsx` y `ClassificationTable.tsx`: filtros y tabla pública.
- `npm run test:clasificaciones`: 32 comprobaciones de formatos, límites, representación, autenticación y persistencia.

No se ha recibido todavía el CSV real del proveedor. La plantilla y las variantes de las pruebas están comprobadas; conviene validar un archivo real de cronometraje antes de publicar resultados oficiales.
