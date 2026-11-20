// Feature 011 · Cierre: 404 reales y metadatos de detalle en el HTML inicial, respaldo con la API
// caída y /admin intacto. Ampliado en la US4 con la CSP y /pantallas.
// Uso (desde frontend/, con Docker Compose en marcha):
//   node scripts/verificar-cierre.mjs [url-base]
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const raiz = fileURLToPath(new URL('../..', import.meta.url));
const sh = (orden) => execSync(orden, { cwd: raiz, stdio: ['ignore', 'pipe', 'pipe'] }).toString().trim();
const NO_ENCONTRADA = 'Este sendero no está en el mapa.';
const meta = (html, prop) => html.match(new RegExp(`(?:property|name)="${prop}" content="([^"]*)"`))?.[1];
const titulo = (html) => html.match(/<title>([^<]*)<\/title>/)?.[1];
async function pedir(ruta) {
  const r = await fetch(base + ruta, { redirect: 'manual' });
  return { estado: r.status, html: await r.text(), cabeceras: r.headers };
}
async function esperarApi() {
  for (let i = 0; i < 60; i++) {
    const r = await fetch(base + '/api/ready').catch(() => null);
    if (r?.ok) return;
    await new Promise((res) => setTimeout(res, 500));
  }
  throw new Error('La API no vuelve a estar disponible');
}

// 1. Estados HTTP reales.
const casos = [
  ['/no-existe', 404], ['/noticias/inventada', 404], ['/galeria/inventado', 404], ['/carreras/inventada', 404],
  ['/recorridos/inventada', 404], ['/clasificaciones/2019', 404], ['/noticias/gracias-trail-2026/extra', 404],
  ['/assets/inexistente.js', 404], ['/noticias/gracias-trail-2026', 200], ['/galeria/edicion-2026', 200],
  ['/carreras/trail-27k', 200], ['/recorridos/speed-14k', 200], ['/', 200], ['/carreras', 200], ['/noticias', 200],
];
const clasificaciones2026 = (await (await fetch(base + '/api/content')).json()).data.results.some((r) => r.year === '2026');
if (clasificaciones2026) casos.push(['/clasificaciones/2026', 200]);
const malos = [];
for (const [ruta, esperado] of casos) {
  const { estado, html } = await pedir(ruta);
  if (estado !== esperado) malos.push(`${ruta}: ${estado} (esperado ${esperado})`);
  if (estado === 404 && (!html.includes('noindex') || titulo(html) !== 'Página no encontrada | Trail Peñasagra')) malos.push(`${ruta}: 404 sin noindex`);
}
if (!malos.length) ok(`estados HTTP: ${casos.length} rutas (${casos.filter((c) => c[1] === 404).length} con 404 real y noindex)`);
else fallo(`estados: ${malos.join('; ')}`);

// 2. Metadatos propios en el HTML inicial (sin ejecutar JavaScript).
const noticia = (await pedir('/noticias/gracias-trail-2026')).html;
const album = (await pedir('/galeria/edicion-2026')).html;
const prueba = (await pedir('/recorridos/speed-14k')).html;
const datos = (await (await fetch(base + '/api/content')).json()).data;
const n = datos.news.find((x) => x.id === 'gracias-trail-2026');
// Un solo título, sin restos de la plantilla y con el bloque que inserta la API.
const unicos = [noticia, album, prueba].every((h) => (h.match(/<title>/g) ?? []).length === 1 && !h.includes('{{') && h.includes('<!-- meta -->'));
if (titulo(noticia) === `${n.title} | Trail Peñasagra` && meta(noticia, 'og:type') === 'article'
  && meta(noticia, 'og:image') === new URL(n.image, base).href && meta(noticia, 'og:url') === `${base}/noticias/gracias-trail-2026`
  && noticia.includes(`<link rel="canonical" href="${base}/noticias/gracias-trail-2026" />`)
  && meta(album, 'og:title') === `${datos.albums.find((a) => a.id === 'edicion-2026').title} | Trail Peñasagra`
  && meta(prueba, 'og:url') === `${base}/recorridos/speed-14k` && unicos)
  ok('metadatos propios en el HTML inicial: noticia (article), álbum y prueba por /recorridos, con canónica e imagen absoluta');
else fallo(`metadatos: ${titulo(noticia)} / ${meta(album, 'og:title')} / ${meta(prueba, 'og:url')} únicos=${unicos}`);

// 3. El SPA muestra la página «no encontrada» en las 404 y el contenido en los detalles.
const browser = await navegador();
const page = await browser.newPage();
let spa = true;
for (const ruta of ['/no-existe', '/noticias/inventada', '/carreras/inventada']) {
  const r = await page.goto(base + ruta, { waitUntil: 'networkidle' });
  spa &&= r.status() === 404 && (await page.textContent('main')).includes(NO_ENCONTRADA);
}
await page.goto(base + '/noticias/gracias-trail-2026', { waitUntil: 'networkidle' });
spa &&= (await page.textContent('main')).includes(n.title);
if (spa) ok(`SPA: «${NO_ENCONTRADA}» con estado 404; el detalle publicado se muestra`);
else fallo('SPA en 404 o detalle');

// 4. /admin y sus subrutas no cambian.
const admin = await Promise.all(['/admin', '/admin/noticias', '/admin/noticias/nuevo'].map(pedir));
if (admin.every((a) => a.estado === 200 && a.html.includes('noindex'))) ok('/admin y subrutas: 200 con noindex');
else fallo(`admin: ${admin.map((a) => a.estado)}`);

// 5. API detenida: el detalle se sirve con los metadatos genéricos y el aviso de respaldo.
sh('docker compose stop api');
try {
  const caida = await pedir('/noticias/gracias-trail-2026');
  const r = await page.goto(base + '/noticias/gracias-trail-2026', { waitUntil: 'load' });
  await page.waitForSelector('.load-error', { timeout: 15000 });
  if (caida.estado === 200 && titulo(caida.html) === 'Trail Peñasagra · Corremos por Adriana' && r.status() === 200 && !caida.html.includes('{{'))
    ok('API detenida: detalle con 200, metadatos genéricos y aviso de respaldo');
  else fallo(`API caída: ${caida.estado} ${titulo(caida.html)}`);
} finally {
  sh('docker compose start api');
  await esperarApi();
}
await browser.close();
