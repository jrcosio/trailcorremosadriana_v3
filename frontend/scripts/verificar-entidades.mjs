// Feature 009 · Patrocinadores y colaboradores: logos grandes, secciones independientes, orden,
// enlace en pestaña nueva, retirada y borrado (deja los datos como estaban).
// Uso: ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-entidades.mjs [url-base]
import { fileURLToPath } from 'node:url';
import { ANCHOS, cargarTodo, fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!usuario || !password) { console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD'); process.exit(2); }
const logo = (n) => fileURLToPath(new URL(`../public/reused/logos/patrocinadores/${n}`, import.meta.url));
const PATROCINADORES = ['Carandía', 'JV Cosío', 'Andros', 'Aljomar', 'Artipublic', 'Grupo Choví', 'Natuber', 'Ayuntamiento de Rionansa'];
const A = 'Colaborador de verificación A';
const B = 'Colaborador de verificación B';
const WEB_A = 'https://example.com/verificacion-009';
const browser = await navegador();
const page = await (await browser.newContext()).newPage();

const rejilla = (n) => page.$$eval('.partners .logo-grid', (grids, n) => [...(grids[n]?.children ?? [])].map((c) => ({
  tag: c.tagName,
  alt: c.querySelector('img')?.alt,
  href: c.getAttribute('href'),
  target: c.getAttribute('target'),
  rel: c.getAttribute('rel'),
  alto: c.getBoundingClientRect().height,
  ajuste: getComputedStyle(c.querySelector('img')).objectFit,
})), n);
const patrocinadoresPublicos = () => rejilla(0);
async function colaboradoresPublicos() {
  await page.goto(base + '/patrocinadores', { waitUntil: 'networkidle' });
  return rejilla(1);
}

// 1. Público: los 8 patrocinadores aprobados, grandes, sin enlaces y en orden; colaboradores vacíos.
for (const ancho of ANCHOS) {
  await page.setViewportSize({ width: ancho, height: 900 });
  await page.goto(base + '/patrocinadores', { waitUntil: 'networkidle' });
  await cargarTodo(page);
  const celdas = await patrocinadoresPublicos();
  const desborde = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  const vacio = (await page.textContent('.partners')).includes('Próximamente anunciaremos los colaboradores');
  const bien = celdas.map((c) => c.alt).join('|') === PATROCINADORES.join('|')
    && celdas.every((c) => c.tag === 'DIV' && c.ajuste === 'contain' && c.alto >= 150);
  if (bien && !desborde && vacio) ok(`${ancho}px: 8 patrocinadores en orden, sin enlace, logos ≥150 px con object-fit contain; colaboradores vacíos`);
  else fallo(`${ancho}px: ${JSON.stringify(celdas.map((c) => [c.alt, c.tag, c.ajuste, Math.round(c.alto)]))} desborde=${desborde} vacío=${vacio}`);
}
await page.setViewportSize({ width: 1440, height: 900 });
await page.goto(base + '/', { waitUntil: 'networkidle' });
const enInicio = await page.$$eval('.partners .logo-grid img', (i) => i.map((x) => x.alt));
if (enInicio.join('|') === PATROCINADORES.join('|')) ok('inicio: los 8 patrocinadores'); else fallo(`inicio: ${enInicio}`);

// 2. Panel.
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.fill('input[name="username"]', usuario);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-event h2');
const privado = async () => (await (await page.request.get(base + '/api/content?admin=1')).json()).data;
const antes = (await privado()).sponsors;
async function guardar() {
  await page.click('button[type="submit"]');
  await page.waitForFunction(() => document.body.innerText.includes('Cambios guardados') || document.querySelector('.admin-error[role="alert"]'), null, { timeout: 15000 });
  return (await page.$('.admin-error[role="alert"]')) ? (await page.textContent('.admin-error[role="alert"]'))?.trim() : 'ok';
}
async function nuevo(nombre, archivo, web, orden) {
  await page.goto(base + '/admin/colaboradores/nuevo', { waitUntil: 'networkidle' });
  await page.fill('input[name="name"]', nombre);
  await page.locator('.upload-field input[type="file"]').first().setInputFiles(logo(archivo));
  await page.waitForSelector('img.upload-preview');
  if (web) await page.fill('input[name="url"]', web);
  await page.fill('input[name="order"]', String(orden));
  await page.locator('.publish-card input[role="switch"]').check();
  return guardar();
}
const idDe = async (nombre) => (await privado()).collaborators.find((c) => c.name === nombre)?.id;

const r1 = await nuevo(A, 'banner_andros.png', WEB_A, 2);
const r2 = await nuevo(B, 'banner_natuber.png', '', 1);
let col = await colaboradoresPublicos();
const celdaA = col.find((c) => c.alt === A);
if (r1 === 'ok' && r2 === 'ok' && col.map((c) => c.alt).join('|') === `${B}|${A}` && celdaA?.tag === 'A'
  && celdaA.href === WEB_A && celdaA.target === '_blank' && celdaA.rel === 'noreferrer' && col.every((c) => c.ajuste === 'contain')) {
  ok('2 colaboradores publicados en orden (B=1, A=2); A abre su web en pestaña nueva y B no tiene enlace');
} else fallo(`alta: ${r1} ${r2} ${JSON.stringify(col)}`);

// 3. Cambiar el orden y retirar.
const idA = await idDe(A);
const idB = await idDe(B);
await page.goto(base + '/admin/colaboradores/' + idA, { waitUntil: 'networkidle' });
await page.fill('input[name="order"]', '0');
let r = await guardar();
col = await colaboradoresPublicos();
if (r === 'ok' && col.map((c) => c.alt).join('|') === `${A}|${B}`) ok('cambio de orden: A pasa delante'); else fallo(`orden: ${r} ${col.map((c) => c.alt)}`);
await page.goto(base + '/admin/colaboradores/' + idA, { waitUntil: 'networkidle' });
await page.locator('.publish-card input[role="switch"]').uncheck();
r = await guardar();
col = await colaboradoresPublicos();
if (r === 'ok' && col.map((c) => c.alt).join('|') === B) ok('retirada: A deja de mostrarse'); else fallo(`retirada: ${r} ${col.map((c) => c.alt)}`);

// 4. Independencia: los patrocinadores no han cambiado (ni versión).
const despues = (await privado()).sponsors;
if (JSON.stringify(despues) === JSON.stringify(antes)) ok('patrocinadores intactos tras editar colaboradores'); else fallo('los patrocinadores han cambiado');

// 5. Borrado y restauración.
for (const nombre of [A, B]) {
  await page.goto(base + '/admin/colaboradores', { waitUntil: 'networkidle' });
  await page.locator('tr', { hasText: nombre }).locator('button[aria-label^="Eliminar"]').click();
  await page.click('text=Eliminar contenido');
  await page.waitForSelector('.confirm-modal', { state: 'detached', timeout: 10000 });
}
const finales = await privado();
col = await colaboradoresPublicos();
const vacioFinal = (await page.textContent('.partners')).includes('Próximamente anunciaremos los colaboradores');
if (finales.collaborators.length === 0 && col.length === 0 && vacioFinal && !(await idDe(A)) && idB) ok('borrado: colaboradores vacíos de nuevo');
else fallo(`borrado: ${JSON.stringify(finales.collaborators)}`);
await browser.close();
