// Feature 011 · Accesibilidad y móvil: revisión automática WCAG 2.1 A/AA (axe) a 360 y 1440 px y
// desbordamiento horizontal a 320, 340, 360, 768, 1024 y 1440 px.
// Uso: node scripts/verificar-accesibilidad.mjs [url-base]
import AxeBuilder from '@axe-core/playwright';
import { cargarTodo, fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const ETIQUETAS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'];
const RUTAS = [
  '/', '/carreras', '/recorridos', '/inscripciones', '/solidaridad', '/patrocinadores', '/contacto', '/noticias',
  '/galeria', '/clasificaciones', '/reglamento', '/noticias/gracias-trail-2026', '/galeria/edicion-2026',
  '/carreras/trail-27k', '/clasificaciones/2026', '/no-existe', '/admin',
];
const browser = await navegador();

// 1. Revisión automática a 360 y 1440 px.
let incumplimientos = 0;
for (const ancho of [360, 1440]) {
  const contexto = await browser.newContext({ viewport: { width: ancho, height: 900 } });
  const page = await contexto.newPage();
  for (const ruta of RUTAS) {
    await page.goto(base + ruta, { waitUntil: 'networkidle' });
    await cargarTodo(page);
    const { violations } = await new AxeBuilder({ page }).withTags(ETIQUETAS).analyze();
    for (const v of violations) {
      incumplimientos += v.nodes.length;
      fallo(`${ancho}px ${ruta}: ${v.id} [${v.impact}] ${v.nodes.slice(0, 3).map((n) => n.target.join(' ')).join(' · ')}`);
    }
  }
  await contexto.close();
}
if (!incumplimientos) ok(`axe WCAG 2.1 A/AA: 0 incumplimientos en ${RUTAS.length} rutas a 360 y 1440 px`);

// 2. Desbordamiento horizontal a 6 anchos.
const ANCHOS = [320, 340, 360, 768, 1024, 1440];
const desbordes = [];
for (const ancho of ANCHOS) {
  const contexto = await browser.newContext({ viewport: { width: ancho, height: 900 } });
  const page = await contexto.newPage();
  for (const ruta of RUTAS) {
    await page.goto(base + ruta, { waitUntil: 'networkidle' });
    await cargarTodo(page);
    const ancho_doc = await page.evaluate(() => document.documentElement.scrollWidth);
    if (ancho_doc > ancho) desbordes.push(`${ruta}@${ancho} (${ancho_doc} px)`);
  }
  await contexto.close();
}
if (!desbordes.length) ok(`sin desbordamiento horizontal en ${RUTAS.length} rutas a ${ANCHOS.join('/')} px`);
else fallo(`desbordamiento: ${desbordes.join(', ')}`);
await browser.close();
