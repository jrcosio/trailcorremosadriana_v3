# Definición del estilo visual

## Dirección

Moderno, elegante y deportivo; montañero y cercano. Grandes titulares condensados, fotografía real, superficies limpias, contraste claro y acentos naranja. La causa solidaria debe tener protagonismo sin perder la identidad del trail.

No sustituir fotografías reales de la carrera por corredores genéricos o imágenes generadas. No introducir testimonios, cifras de participación o promesas no verificadas.

## Colores

| Token/uso | Valor actual | Aplicación |
|---|---|---|
| Verde principal | `#172e28` | Titulares, navegación, panel y superficies oscuras |
| Verde profundo | `#10241e` | Pie de página |
| Naranja principal | `#dc6537` | Botones y acentos |
| Naranja oscuro | `#b64b24` | Hover y acentos de texto |
| Naranja del título | `#ed834e` | «PENASAGRA» en la portada |
| Naranja de la silueta | `#f1a074` | Silueta de Adriana |
| Terracota solidaria | `#ba4b2e` | Bloque destacado del dorsal en portada |
| Texto secundario | `#66716b` | Explicaciones y metadatos |
| Fondo suave | `#f3f6f4` | Secciones alternas y panel |
| Borde | `#dde3df` | Divisores y tarjetas |
| Blanco | `#ffffff` | Fondo principal y texto sobre imágenes |

Los valores exactos están en `proyecto/app/globals.css`. Conservar contraste de botones, textos, campos y estados; los tamaños mínimos de las reglas iniciales fueron corregidos con reglas posteriores de legibilidad.

## Tipografía

- **Barlow Condensed**, pesos 600/700/800: titulares, distancias y marca.
- **Manrope**, pesos 400/500/600/700/800: cuerpo, navegación y formularios.
- Fuentes locales en `public/fonts/`; no dependen de una descarga de Google en tiempo de visita.
- Cuerpo principal próximo a 16 px; controles y textos de trabajo próximos a 14 px o mayores. Metadatos secundarios pueden ser algo menores.
- Evitar convertir todo el texto en mayúsculas: reservarlas para marca, navegación breve y etiquetas.

## Portada aprobada

- Cabecera blanca con logo y enlaces; botón fijo de texto **INSCRIPCIONES**.
- Título en dos líneas: **TRAIL** en blanco y **PENASAGRA** en naranja. Esta escritura literal fue solicitada por el propietario.
- Tamaño ampliado: regla principal `clamp(5.4rem, 9vw, 8.7rem)`, con ajustes específicos por anchura.
- Paisaje original con capas oscuras para asegurar lectura.
- «Corremos por Adriana.» ampliado, junto a la silueta aportada por el propietario; ya no lleva un corazón.
- La silueta usa el PNG original como máscara alfa CSS. No reemplazarlo por un icono de otra niña.
- El contador permanece a la derecha en escritorio y se apila en móvil.
- **No mostrar el rótulo «TRAIL PEÑASAGRA 2027» encima del contador.**

## Componentes

- Botones sólidos naranja, rectangulares con radio discreto, foco visible y texto inequívoco.
- Enlaces externos con icono de salida; no añadir flechas decorativas a los botones.
- Tarjetas de carreras fotográficas, degradado oscuro inferior, distancia grande y título legible.
- Dorsal solidario: bloque terracota grande en portada y tarjeta verde en la causa; mismo comportamiento de pago.
- Patrocinadores grandes: 3 columnas en escritorio, 2 en tablet y 1 por debajo de 480 px. Celdas de aproximadamente 200/190/175 px de alto y logotipos completos con `object-fit: contain`, sin límite de 175 px de ancho.
- Administración: barra lateral verde, fondo gris verdoso, formularios blancos y estado de publicación claro.
- Clasificaciones: tabla con cabecera verde, filas alternas suaves, posición destacada en naranja para los tres primeros, tiempos tabulares y desplazamiento horizontal limitado a la tabla. La importación CSV utiliza la misma paleta y muestra el mapeo y la vista previa antes de confirmar.

## Composición y adaptación

Contenedor principal de unos 1200 px, márgenes amplios y secciones de 80 px en escritorio; cerca de 48 px en móvil. Radios bajos, sombras suaves y bordes discretos. Puntos de adaptación presentes: 1200, 1000, 700 y 480 px, con ajustes para pantallas grandes.

La apariencia final debe comprobarse a 360, 768, 1024 y 1440 px. Evitar desbordamiento de «PENASAGRA», de la frase solidaria, de tablas y de URLs largas. En pantallas estrechas las tablas pueden tener desplazamiento horizontal local.

Respetar `prefers-reduced-motion`, foco visible, etiquetas de formularios y navegación por teclado. Evitar animaciones continuas decorativas.
