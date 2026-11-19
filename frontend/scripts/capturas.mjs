// Capturas de revisión visual a 360/768/1024/1440 px y detección de desbordamiento horizontal.
// Uso: node scripts/capturas.mjs <url-base> <carpeta-salida>
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { ANCHOS, cargarTodo, navegador } from './comun.mjs';

const [base = 'http://localhost:8080', salida = 'capturas/local'] = process.argv.slice(2);
const RUTAS = ['/', '/carreras', '/carreras/trail-27k', '/inscripciones', '/solidaridad', '/patrocinadores', '/contacto', '/noticias', '/galeria', '/clasificaciones', '/reglamento'];

mkdirSync(salida, { recursive: true });
const browser = await navegador();
const informe = [];
for (const ancho of ANCHOS) {
  const page = await browser.newPage({ viewport: { width: ancho, height: 900 } });
  for (const ruta of RUTAS) {
    await page.goto(base + ruta, { waitUntil: 'networkidle' });
    await cargarTodo(page);
    const datos = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      innerWidth: window.innerWidth,
      texto: document.body.innerText,
      aviso: document.body.innerText.includes('No se han podido comprobar las últimas novedades'),
    }));
    const nombre = (ruta === '/' ? 'inicio' : ruta.slice(1).replaceAll('/', '_')) + '-' + ancho;
    await page.screenshot({ path: join(salida, nombre + '.png'), fullPage: true });
    writeFileSync(join(salida, nombre + '.txt'), datos.texto);
    const desborda = datos.scrollWidth > datos.innerWidth;
    informe.push({ ruta, ancho, desborda, scrollWidth: datos.scrollWidth, avisoRespaldo: datos.aviso });
    console.log(`${desborda ? 'DESBORDA' : 'ok      '} ${String(ancho).padStart(4)} ${ruta}${datos.aviso ? '  (aviso de respaldo)' : ''}`);
  }
  await page.close();
}
await browser.close();
writeFileSync(join(salida, 'informe.json'), JSON.stringify(informe, null, 2));
const desbordes = informe.filter((i) => i.desborda);
console.log(`\n${informe.length} capturas · ${desbordes.length} con desbordamiento horizontal`);
if (desbordes.length) process.exitCode = 1;
