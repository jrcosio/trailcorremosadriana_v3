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
