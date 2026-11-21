# Quickstart / validación: Ajustes de la revisión (012)

```bash
cd frontend && node scripts/verificar-fotos.mjs --referencia capturas/marcos-antes-012.json   # antes del cambio
docker compose build web && docker compose up -d web
cd frontend && npx vitest run && npm run typecheck && npm run build
ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-fotos.mjs --comparar capturas/marcos-antes-012.json
node scripts/verificar-accesibilidad.mjs
node scripts/capturas.mjs http://localhost:8080 capturas/despues-012
```

Resultados esperados:

- 0 fotos recortadas y 0 marcos con un tamaño distinto.
- Relleno presente donde las proporciones difieren.
- 0 incumplimientos AA y 0 desbordamientos.
- La foto de Adriana se ve completa en `/` y en `/solidaridad` (revisión visual de las capturas).

## US3: logotipo nuevo en la cabecera

```bash
cd frontend && node scripts/verificar-logo.mjs --referencia capturas/cabecera-antes-012.json   # antes del cambio
docker compose build web && docker compose up -d web
node scripts/verificar-logo.mjs --comparar capturas/cabecera-antes-012.json
node scripts/verificar-accesibilidad.mjs
node scripts/capturas.mjs http://localhost:8080 capturas/despues-logo-012
```

Resultados esperados:

- El logotipo se ve completo en todas las páginas y anchos, sin la silueta ni el texto en dos
  filas.
- Cabecera, navegación, «INSCRIPCIONES» y menú con 0 px de diferencia.
- 0 desbordamientos y 0 incumplimientos AA.
- Variantes de 50 KB como máximo; en densidad 2 se descarga la de 720.

## US4: logotipo también en el pie

```bash
PANTALLAS=si docker compose up -d web       # para medir también la barra lateral del panel
cd frontend && node scripts/verificar-logo.mjs --referencia capturas/pie-antes-012.json   # antes del cambio
docker compose build web && PANTALLAS=si docker compose up -d web
node scripts/verificar-logo.mjs --comparar capturas/pie-antes-012.json
docker compose up -d web                    # vuelve a PANTALLAS=no
node scripts/verificar-accesibilidad.mjs
node scripts/capturas.mjs http://localhost:8080 capturas/despues-pie-012
```

Resultados esperados:

- El pie muestra el logotipo en negativo, completo, sin la silueta ni el texto en dos filas.
- La cabecera, con 0 px de diferencia.
- Las columnas 2.ª a 4.ª del pie, con la misma posición horizontal y el mismo ancho.
- Lo que baja en el pie, no más que lo que crece el logotipo.
- Naranja con al menos 3:1 y blanco con al menos 4,5:1 sobre el verde del pie.
- 0 desbordamientos y 0 incumplimientos AA.
- Variantes de 50 KB como máximo y nítidas en densidad 2.

## US5: frase de autoría del pie

```bash
cd frontend && npx vitest run tests/pie.test.tsx          # antes del cambio: falla
docker compose build web && PANTALLAS=si docker compose up -d web
node scripts/verificar-logo.mjs --comparar capturas/pie-antes-012.json
docker compose up -d web                    # vuelve a PANTALLAS=no
node scripts/verificar-accesibilidad.mjs
node scripts/capturas.mjs http://localhost:8080 capturas/despues-pie-texto-012
```

Resultados esperados:

- Línea inferior del pie: «© año Asociación Peñasagra» y «Hecho por la Escuela Hacker Cosío».
- Sin enlaces en esa línea y sin restos de «Hecho con pasión», «JR BLANCO» ni «Hackers Cosío».
- La frase, con el color y el tamaño de la línea.
- Cabecera y resto del pie como en la US4.
- 0 desbordamientos y 0 incumplimientos AA.

## US6: podio de las clasificaciones

```bash
cd frontend && node scripts/verificar-podio.mjs --referencia capturas/podio-antes-012.json   # antes del cambio
npx vitest run tests/podio.test.tsx                        # antes del cambio: falla
docker compose build web && docker compose up -d web
node scripts/verificar-podio.mjs --comparar capturas/podio-antes-012.json
node scripts/verificar-accesibilidad.mjs
node scripts/capturas.mjs http://localhost:8080 capturas/despues-podio-012
```

Resultados esperados:

- 1.º, 2.º y 3.º de cada clasificación con fondo de oro, plata y bronce, franja a la izquierda y
  medalla con el número en negrita.
- Las demás filas, igual que antes.
- Filas y tablas con 0 px de diferencia.
- Texto y medallas con un contraste de al menos 4,5:1; 0 incumplimientos AA y 0 desbordamientos.
- El ganador conserva su color al buscarlo; con el filtro «Femenino», las primeras filas no se
  colorean.

## US7 y US8: panel (barra lateral con desplazamiento y logotipo oficial)

```bash
export ADMIN_USUARIO=admin ADMIN_PASSWORD=…
cd frontend && node scripts/verificar-panel.mjs --referencia capturas/panel-antes-012.json   # antes del cambio
docker compose build web && docker compose up -d web
node scripts/verificar-panel.mjs --comparar capturas/panel-antes-012.json
node scripts/verificar-acceso.mjs && node scripts/verificar-admin.mjs
node scripts/verificar-accesibilidad.mjs
```

Resultados esperados:

- En ventanas bajas, de escritorio y de móvil, la barra lateral se desplaza. Todas las opciones y
  «Cerrar sesión» se alcanzan con el teclado y con la rueda, y la página no se mueve.
- La opción de la sección abierta se ve al cargar.
- Sin desplazamiento horizontal. Con altura suficiente, la barra lateral se ve igual que antes.
- Logotipo oficial en la barra lateral, con «ADMINISTRACIÓN», y en el acceso. No es más ancho que
  la marca anterior y es nítido en densidad 2. Barra, contenido y formulario en su sitio.
- axe da 0 incumplimientos en la barra lateral y en el acceso.

## US9: contraste AA en todo el panel

```bash
export ADMIN_USUARIO=admin ADMIN_PASSWORD=…
cd frontend && node scripts/verificar-panel-aa.mjs     # antes del cambio: 222 incumplimientos (2 defectos)
docker compose build web && docker compose up -d web
node scripts/verificar-panel-aa.mjs
curl -s http://localhost:8080/api/content | jq '.data.settings.email'   # sin cambios
```

Resultados esperados:

- 0 incumplimientos en 69 vistas: 22 rutas × 3 anchos y 3 estados de guardado.
- Escrituras interceptadas; ningún dato cambia.
- En las capturas solo cambia el color de las cabeceras de tabla y del pie del panel.
