// Con la API detenida, la web debe mostrar el contenido de referencia y el aviso (FR-007).
// Uso: node scripts/verificar-respaldo.mjs [url-base]
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const AVISO = 'No se han podido comprobar las últimas novedades';
const browser = await navegador();
const page = await browser.newPage();
for (const [ruta, esperado] of [['/', 'PEÑASAGRA'], ['/carreras', 'Speed Trail'], ['/patrocinadores', 'Patrocinadores']]) {
  // Site.tsx no consume el cuerpo de una respuesta de error: Chromium deja esa petición abierta y
  // `networkidle` nunca llega. Se espera a la carga y al aviso de respaldo.
  await page.goto(base + ruta, { waitUntil: 'load' });
  await page.waitForSelector('.load-error', { timeout: 10000 }).catch(() => {});
  const texto = await page.evaluate(() => document.body.innerText);
  if (!texto.includes(AVISO)) fallo(`${ruta}: falta el aviso de respaldo`);
  else if (!texto.includes(esperado)) fallo(`${ruta}: falta el contenido de referencia «${esperado}»`);
  else ok(`${ruta}: contenido de referencia + aviso`);
}
await browser.close();
