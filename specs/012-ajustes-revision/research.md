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
