// Feature 011 · Cierre: 404 reales y metadatos de detalle en el HTML inicial, respaldo con la API
// caída y /admin intacto. Ampliado en la US4 con la CSP, la CSP propia de /media y /pantallas
// (decisión P5).
// Uso (desde frontend/, con Docker Compose en marcha; el panel solo con credenciales):
//   [ADMIN_USUARIO=… ADMIN_PASSWORD=…] node scripts/verificar-cierre.mjs [url-base]
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

// 6. CSP: ninguna violación en el recorrido público (con el mapa de Wikiloc) ni en el panel.
const contexto = await browser.newContext();
await contexto.addInitScript(() => {
  window.__csp = [];
  document.addEventListener('securitypolicyviolation', (e) => window.__csp.push(`${e.violatedDirective} ${e.blockedURI}`));
});
const nav = await contexto.newPage();
const violaciones = [];
// Solo cuentan las violaciones de NUESTRA política. Wikiloc responde 403 (desafío anti-bots de
// Cloudflare, con X-Frame-Options propio) a navegadores automatizados: se anota aparte.
const terceros = new Set();
nav.on('console', (m) => {
  const t = m.text();
  if (/X-Frame-Options/.test(t)) terceros.add(t.match(/'(https:\/\/[^']+)'/)?.[1] ?? 'tercero');
  else if (/Content Security Policy/.test(t)) violaciones.push(t.slice(0, 160));
});
const recoger = async (ruta) => violaciones.push(...(await nav.evaluate(() => window.__csp)).map((v) => `${ruta}: ${v}`));
const recorrido = ['/', '/carreras', '/carreras/trail-27k', '/inscripciones', '/solidaridad', '/patrocinadores', '/contacto',
  '/noticias', '/noticias/gracias-trail-2026', '/galeria', '/galeria/edicion-2026', '/clasificaciones', '/clasificaciones/2026', '/reglamento', '/no-existe', '/admin'];
for (const ruta of recorrido) {
  await nav.goto(base + ruta, { waitUntil: 'networkidle' });
  await recoger(ruta);
}
const cabecera = (await pedir('/')).cabeceras.get('content-security-policy') ?? '';
// El mapa se carga a petición: se pulsa el botón y se comprueba que el iframe no se bloquea.
await nav.goto(base + '/carreras/trail-27k', { waitUntil: 'networkidle' });
await nav.click('text=Cargar mapa interactivo');
const iframe = await nav.waitForSelector('iframe[src*="wikiloc.com"]', { timeout: 10000 }).catch(() => null);
await nav.waitForTimeout(3000);
await recoger('/carreras/trail-27k (mapa)');
let panel = 'sin credenciales: panel no recorrido';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (usuario && password) {
  await nav.goto(base + '/admin', { waitUntil: 'networkidle' });
  await nav.fill('input[name="username"]', usuario);
  await nav.fill('input[name="password"]', password);
  await nav.click('button[type="submit"]');
  await nav.waitForSelector('.admin-event h2');
  for (const ruta of ['/admin/noticias', '/admin/galeria', '/admin/clasificaciones', '/admin/evento', '/admin/ajustes', '/admin/noticias/nuevo']) {
    await nav.goto(base + ruta, { waitUntil: 'networkidle' });
    await recoger(ruta);
  }
  await nav.locator('.upload-field input[type="file"]').first().setInputFiles(fileURLToPath(new URL('../public/reused/img/dorsal_solidario.webp', import.meta.url)));
  await nav.waitForSelector('img.upload-preview', { timeout: 15000 });
  const subida = await nav.getAttribute('img.upload-preview', 'src');
  const cargada = await nav.evaluate(() => document.querySelector('img.upload-preview')?.naturalWidth > 0);
  await recoger('/admin/noticias/nuevo (subida)');
  const mediaCsp = (await pedir(subida)).cabeceras.get('content-security-policy');
  panel = cargada && mediaCsp === "default-src 'none'; sandbox" ? 'panel (7 pantallas y subida) sin violaciones; /media con su CSP propia' : `panel: subida=${cargada} csp /media=${mediaCsp}`;
}
if (!violaciones.length && cabecera.includes('frame-src https://es.wikiloc.com') && iframe && !panel.startsWith('panel:'))
  ok(`CSP: 0 violaciones en ${recorrido.length} páginas (frame-src de Wikiloc permitido)${terceros.size ? ` [Wikiloc rechaza el navegador automatizado: ${[...terceros].join(', ')}]` : ''}; ${panel}`);
else fallo(`CSP: ${violaciones.slice(0, 5).join(' | ')} cabecera=${!!cabecera} iframe=${!!iframe} ${panel}`);
await contexto.close();

// 7. /pantallas: 404 por defecto (producción) y disponible con PANTALLAS=si; se deja como estaba.
const pantallas = ['/pantallas', '/pantallas/admin', '/pantallas/admin/noticias'];
const estadoPantallas = async () => Promise.all(pantallas.map(async (r) => (await pedir(r)).estado));
const cambiarPantallas = async (valor) => {
  sh(`PANTALLAS=${valor} docker compose up -d web`);
  for (let i = 0; i < 30 && !(await fetch(base + '/').catch(() => null))?.ok; i++) await new Promise((r) => setTimeout(r, 300));
};
const inicial = await estadoPantallas();
await cambiarPantallas('no');
const produccion = await estadoPantallas();
await page.goto(base + '/pantallas/admin/noticias/nuevo', { waitUntil: 'networkidle' });
const retiradaEnSpa = (await page.textContent('main')).includes(NO_ENCONTRADA) && !(await page.isVisible('text=vista de diseño'));
await cambiarPantallas('si');
const local = await estadoPantallas();
await cambiarPantallas(inicial[0] === 404 ? 'no' : 'si');
if (produccion.every((e) => e === 404) && retiradaEnSpa && local.every((e) => e === 200) && (await estadoPantallas()).join() === inicial.join())
  ok('/pantallas: 404 y página «no encontrada» con PANTALLAS=no (producción); 200 con PANTALLAS=si (revisión local); configuración restaurada');
else fallo(`/pantallas: producción=${produccion} spa=${retiradaEnSpa} local=${local}`);
await browser.close();
