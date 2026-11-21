// Feature 012 · US9 (decisión P4 aplicada al panel): revisión WCAG 2.1 A/AA (axe) del panel con la
// sesión iniciada. Cubre todas las secciones, un elemento existente y el alta de cada colección.
// Cubre también los estados de guardado (aviso de éxito y mensaje de error) y las dos variantes de
// la etiqueta de estado. Las escrituras se interceptan: la revisión no cambia ningún dato.
// Uso (desde frontend/, con Docker Compose en marcha):
//   ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-panel-aa.mjs [url-base]
import AxeBuilder from '@axe-core/playwright';
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!usuario || !password) { console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD'); process.exit(2); }
const ETIQUETAS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'];
const ANCHOS = [360, 1024, 1440];

const browser = await navegador();
const contexto = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await contexto.newPage();
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.fill('input[name="username"]', usuario);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-sidebar nav a');

// Ninguna escritura llega al servidor. El modo decide la respuesta: éxito, error o petición abortada.
let modoEscritura = 'abortar';
let escriturasInterceptadas = 0;
await page.route('**/api/**', (ruta) => {
  const r = ruta.request();
  if (r.method() === 'GET' || /\/api\/(login|logout)$/.test(new URL(r.url()).pathname)) return ruta.continue();
  escriturasInterceptadas++;
  if (modoEscritura === 'exito') return ruta.fulfill({ status: 200, contentType: 'application/json', body: '{}' });
  if (modoEscritura === 'error') return ruta.fulfill({ status: 422, contentType: 'application/json', body: JSON.stringify({ detail: 'El título es obligatorio.' }) });
  return ruta.abort();
});

// Rutas: las secciones de la barra lateral y, en las colecciones, un elemento existente y el alta.
const secciones = await page.$$eval('.admin-sidebar nav a', (as) => as.map((a) => a.getAttribute('href')));
const rutas = [...secciones];
for (const s of secciones.filter((h) => h !== '/admin')) {
  await page.goto(base + s, { waitUntil: 'networkidle' });
  const enlaces = await page.$$eval(`a[href^="${s}/"]`, (as) => [...new Set(as.map((a) => a.getAttribute('href')))]);
  const existente = enlaces.find((h) => !h.endsWith('/nuevo'));
  if (existente) rutas.push(existente);
  if (enlaces.some((h) => h.endsWith('/nuevo'))) rutas.push(`${s}/nuevo`);
}

const fallos = [];
const vistas = [];
async function revisar(etiqueta) {
  const { violations } = await new AxeBuilder({ page }).withTags(ETIQUETAS).analyze();
  vistas.push(etiqueta);
  for (const v of violations) for (const n of v.nodes) {
    // Agrupa por regla, elemento (sin su posición) y mensaje: el mismo defecto se repite en muchas vistas.
    const elemento = n.target.join(' ').replace(/:nth-child\(\d+\)/g, '');
    fallos.push({ vista: etiqueta, clave: `${v.id} ${elemento} — ${(n.any[0]?.message ?? n.failureSummary ?? '').split('. Expected')[0]}` });
  }
}

for (const ancho of ANCHOS) {
  await page.setViewportSize({ width: ancho, height: 900 });
  for (const ruta of rutas) {
    await page.goto(base + ruta, { waitUntil: 'networkidle' });
    // Variante «borrador» de la etiqueta de estado, si la página solo muestra la otra: se clona la real.
    await page.evaluate(() => {
      const pill = document.querySelector('.status-pill.published');
      if (pill && !document.querySelector('.status-pill.draft')) {
        const copia = pill.cloneNode(true);
        copia.className = 'status-pill draft';
        copia.textContent = 'Borrador';
        pill.after(copia);
      }
    });
    await revisar(`${ancho}px ${ruta}`);
  }
}

// Estados de guardado (1440 px), con las escrituras interceptadas.
await page.setViewportSize({ width: 1440, height: 900 });
const guardar = async () => { await page.click('form button[type="submit"], .form-save-bar button[type="submit"]'); };
// Aviso de éxito en «Ajustes» y mensaje «Guardado correctamente» en un elemento existente.
modoEscritura = 'exito';
await page.goto(base + '/admin/ajustes', { waitUntil: 'networkidle' });
await page.fill('input[type="email"]', 'aa-prueba@example.com').catch(() => {});
await guardar();
await page.waitForSelector('.toast', { timeout: 10000 }).then(() => revisar('estado: aviso de guardado (Ajustes)')).catch(() => fallos.push({ vista: 'estado', clave: 'no aparece el aviso de guardado' }));
const existente = rutas.find((r) => /^\/admin\/noticias\/(?!nuevo)/.test(r));
if (existente) {
  await page.goto(base + existente, { waitUntil: 'networkidle' });
  await page.fill('input[name="title"]', 'Título de prueba de contraste').catch(() => {});
  await guardar();
  await page.waitForSelector('.success-message', { timeout: 10000 }).then(() => revisar('estado: «Guardado correctamente» (noticia)')).catch(() => fallos.push({ vista: 'estado', clave: 'no aparece «Guardado correctamente»' }));
}
// Mensaje de error del servidor.
modoEscritura = 'error';
await page.goto(base + '/admin/ajustes', { waitUntil: 'networkidle' });
await page.fill('input[type="email"]', 'aa-prueba@example.com').catch(() => {});
await guardar();
await page.waitForSelector('.error-message', { timeout: 10000 }).then(() => revisar('estado: mensaje de error (Ajustes)')).catch(() => fallos.push({ vista: 'estado', clave: 'no aparece el mensaje de error' }));
await browser.close();

if (!fallos.length) ok(`axe WCAG 2.1 A/AA en el panel con la sesión iniciada: 0 incumplimientos en ${vistas.length} vistas (${rutas.length} rutas × ${ANCHOS.length} anchos y 3 estados de guardado); ${escriturasInterceptadas} escrituras interceptadas, ninguna llegó al servidor`);
else {
  const grupos = new Map();
  for (const f of fallos) grupos.set(f.clave, [...(grupos.get(f.clave) ?? []), f.vista]);
  fallo(`${fallos.length} incumplimientos en ${new Set(fallos.map((f) => f.vista)).size} de ${vistas.length} vistas, ${grupos.size} distintos:\n  ${[...grupos].map(([c, v]) => `${c} — ${v.length} vistas (${[...new Set(v)].slice(0, 4).join('; ')}${v.length > 4 ? '…' : ''})`).join('\n  ')}`);
}
console.log(`Rutas revisadas: ${rutas.join(', ')}`);
