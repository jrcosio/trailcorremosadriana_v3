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
