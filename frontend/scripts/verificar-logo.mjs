// Feature 012 · US3 (decisión P7): logotipo nuevo en la cabecera, sin mover el resto.
// Uso (desde frontend/, con Docker Compose en marcha):
//   node scripts/verificar-logo.mjs --referencia capturas/cabecera-antes-012.json   # antes del cambio
//   node scripts/verificar-logo.mjs --comparar capturas/cabecera-antes-012.json
import { readFileSync, statSync, writeFileSync } from 'node:fs';
import { fallo, navegador, ok } from './comun.mjs';

const [modo, archivo] = process.argv.slice(2);
if (!['--referencia', '--comparar'].includes(modo) || !archivo) {
  console.error('Uso: verificar-logo.mjs --referencia|--comparar <archivo.json> [url-base]');
  process.exit(2);
}
const base = process.argv[4] ?? 'http://localhost:8080';
// Anchos aprobados y los dos lados de cada cambio de diseño de la cabecera (359/360, 700/701, 1000/1001, 1200/1201).
const ANCHOS = [320, 340, 359, 360, 390, 414, 700, 701, 768, 1000, 1001, 1024, 1200, 1201, 1440];
const RUTAS = ['/', '/carreras', '/solidaridad', '/noticias', '/clasificaciones', '/contacto'];
const VARIANTES = ['logo_cabecera-480.webp', 'logo_cabecera-720.webp'];

async function medir() {
  const rect = (el) => {
    if (!el || getComputedStyle(el).display === 'none') return null;
    const r = el.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height };
  };
  const header = document.querySelector('.header');
  const marca = header.querySelector('.brand');
  const img = marca?.querySelector('img');
  const pie = document.querySelector('footer .brand');
  // Con srcset, naturalWidth/Height vienen en píxeles CSS redondeados: se miden los píxeles reales del archivo descargado.
  const real = img && await new Promise((res) => { const x = new Image(); x.onload = () => res([x.naturalWidth, x.naturalHeight]); x.onerror = () => res([0, 0]); x.src = img.currentSrc; });
  return {
    header: rect(header),
    nav: rect(header.querySelector('nav')),
    cta: rect(header.querySelector('.nav-cta')),
    menu: rect(header.querySelector('.menu-toggle')),
    marca: rect(marca),
    texto: marca?.innerText.trim() ?? null,
    enlace: { href: marca?.getAttribute('href'), etiqueta: marca?.getAttribute('aria-label') },
    img: img && {
      ...rect(img), src: img.currentSrc, completa: img.complete && img.naturalWidth > 0,
      natural: real[0] / real[1], pixeles: real[0], ajuste: getComputedStyle(img).objectFit,
      filtro: getComputedStyle(img).filter, alt: img.alt,
    },
    pie: pie && { ...rect(pie), texto: pie.innerText, src: pie.querySelector('img')?.getAttribute('src') },
    desborda: document.documentElement.scrollWidth > innerWidth,
  };
}

const browser = await navegador();
const medidas = {};
const page = await (await browser.newContext()).newPage();
for (const ancho of ANCHOS) {
  await page.setViewportSize({ width: ancho, height: 900 });
  for (const ruta of RUTAS) {
    await page.goto(base + ruta, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => [...document.querySelectorAll('.header img')].every((i) => i.complete), null, { timeout: 10000 }).catch(() => {});
    medidas[`${ruta}@${ancho}`] = await page.evaluate(medir);
  }
}

// Barra lateral del panel (vista de demostración, solo si /pantallas está disponible en local).
let panel = null;
const r = await page.goto(base + '/pantallas/admin', { waitUntil: 'networkidle' });
if (r?.status() === 200 && (await page.$('.admin-sidebar .brand'))) {
  panel = await page.$eval('.admin-sidebar .brand', (a) => ({ texto: a.innerText, src: a.querySelector('img')?.getAttribute('src') }));
}

// Nitidez: en densidad 2 la variante descargada mide al menos el doble del tamaño en pantalla.
const densidad = {};
for (const ancho of [360, 768, 1440]) {
  const p = await (await browser.newContext({ deviceScaleFactor: 2, viewport: { width: ancho, height: 900 } })).newPage();
  await p.goto(base + '/', { waitUntil: 'networkidle' });
  await p.waitForFunction(() => document.querySelector('.header .brand img')?.complete);
  densidad[ancho] = await p.evaluate(medir).then((m) => ({ natural: m.img.pixeles, pantalla: m.img.w, src: m.img.src }));
}
await browser.close();

if (modo === '--referencia') {
  writeFileSync(archivo, JSON.stringify({ medidas, panel }, null, 1));
  console.log(`Referencia guardada: ${Object.keys(medidas).length} vistas de la cabecera; panel: ${panel ? 'medido' : 'no disponible'}.`);
  process.exit(0);
}

const ref = JSON.parse(readFileSync(archivo, 'utf8'));
const igual = (a, b) => (a === null && b === null) || (a && b && ['x', 'y', 'w', 'h'].every((k) => Math.abs(a[k] - b[k]) <= 0.5));
const problemas = [];
for (const [clave, m] of Object.entries(medidas)) {
  const antes = ref.medidas[clave];
  const p = (t) => problemas.push(`${clave}: ${t}`);
  if (!antes) { p('sin referencia'); continue; }
  for (const k of ['header', 'nav', 'cta', 'menu']) if (!igual(m[k], antes[k])) p(`${k} se ha movido (${JSON.stringify(antes[k])} → ${JSON.stringify(m[k])})`);
  const i = m.img;
  if (!i || !VARIANTES.some((v) => i.src.endsWith('/reused/logos/' + v))) { p(`no muestra el logotipo nuevo (${i?.src})`); continue; }
  if (!i.completa) p('el logotipo no ha cargado');
  if (Math.abs(i.w / i.h - i.natural) / i.natural > 0.01) p(`logotipo deformado (${(i.w / i.h).toFixed(3)} frente a ${i.natural.toFixed(3)})`);
  if (i.ajuste === 'cover') p('logotipo recortado (cover)');
  if (i.filtro !== 'none') p(`el logotipo lleva filtro (${i.filtro})`);
  if (i.w > antes.marca.w + 0.5) p(`más ancho que la marca anterior (${i.w.toFixed(1)} > ${antes.marca.w.toFixed(1)})`);
  if (i.y < m.header.y + 4 || i.y + i.h > m.header.y + m.header.h - 4) p('el logotipo no cabe en la cabecera con 4 px de margen');
  if (m.texto) p(`queda texto de marca en la cabecera («${m.texto}»)`);
  if (m.enlace.href !== '/' || !m.enlace.etiqueta) p(`enlace a la portada incorrecto (${JSON.stringify(m.enlace)})`);
  if (!i.alt) p('el logotipo no tiene alt');
  if (JSON.stringify({ ...m.pie }) !== JSON.stringify({ ...antes.pie })) p('el pie ha cambiado');
  if (m.desborda) p('desbordamiento horizontal');
}
const total = Object.keys(medidas).length;
if (!problemas.length) ok(`${total} vistas (${RUTAS.length} rutas × ${ANCHOS.length} anchos): logotipo nuevo completo y sin deformar, sin texto de marca, cabecera/navegación/INSCRIPCIONES/menú con 0 px de diferencia, logotipo no más ancho que la marca anterior, pie igual y sin desbordamientos`);
else fallo(`${problemas.length} problemas:\n  ${problemas.slice(0, 20).join('\n  ')}`);

const tamanos = VARIANTES.map((v) => statSync(new URL(`../public/reused/logos/${v}`, import.meta.url)).size);
if (tamanos.every((t) => t <= 50 * 1024)) ok(`variantes de ${tamanos.map((t) => `${(t / 1024).toFixed(1)} KB`).join(' y ')} (máximo 50 KB)`);
else fallo(`variantes demasiado pesadas: ${tamanos.join(', ')} bytes`);
const nitidas = Object.entries(densidad).filter(([, d]) => d.natural >= 2 * d.pantalla);
if (nitidas.length === Object.keys(densidad).length) ok(`densidad 2: ${Object.entries(densidad).map(([a, d]) => `${a} px → ${d.src.split('/').pop()} (${d.natural} ≥ 2×${d.pantalla.toFixed(0)})`).join('; ')}`);
else fallo(`densidad 2 sin resolución suficiente: ${JSON.stringify(densidad)}`);
if (ref.panel && JSON.stringify(panel) !== JSON.stringify(ref.panel)) fallo(`la barra lateral del panel ha cambiado: ${JSON.stringify(panel)}`);
else if (ref.panel) ok('barra lateral del panel sin cambios');
else console.log('AVISO /pantallas no disponible: barra lateral del panel no comprobada');
