// Feature 006 · Clasificaciones: consulta pública (2026 reales) y flujo del panel con una prueba
// temporal (alta, sustitución y borrado). Restaura los datos al terminar.
// Uso: ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-clasificaciones.mjs [url-base]
import { writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!usuario || !password) { console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD'); process.exit(2); }
const browser = await navegador();
const contexto = await browser.newContext();
const page = await contexto.newPage();
const texto = () => page.evaluate(() => document.body.innerText);

// --- Público: /clasificaciones/2026 ---
await page.goto(base + '/clasificaciones/2026', { waitUntil: 'networkidle' });
const tarjetas = await page.$$eval('.classification-card header', (hs) => hs.map((h) => h.innerText));
const recuentos = tarjetas.map((t) => (t.match(/(\d+) participantes/) ?? [])[1]).sort();
if (tarjetas.length === 3 && JSON.stringify(recuentos) === JSON.stringify(['205', '224', '63'])) ok('/clasificaciones/2026: 3 clasificaciones (63, 205 y 224)');
else fallo(`/clasificaciones/2026: ${JSON.stringify(tarjetas)}`);
const trail = page.locator('.classification-card', { hasText: 'Trail Peñasagra 2026' }).first();
await trail.locator('input[type="search"]').fill('gonzalez');
await page.waitForFunction(() => [...document.querySelectorAll('.classification-card')].some((c) => /7 participantes · /.test(c.querySelector('caption')?.textContent ?? '')), null, { timeout: 10000 });
const nombres = await trail.locator('tbody tr td strong').allInnerTexts();
if (nombres.length === 7 && nombres.every((n) => /gonz[aá]lez/i.test(n))) ok('búsqueda «gonzalez» sin tilde: 7 participantes');
else fallo(`búsqueda: ${nombres.join(' | ')}`);
const speed = page.locator('.classification-card', { hasText: 'Speed Trail' }).first();
const pag = speed.locator('.classification-pagination span');
const p1 = await pag.innerText();
await speed.locator('button:has-text("Siguiente")').click();
await page.waitForFunction((el) => el.textContent?.startsWith('Página 2'), await pag.elementHandle(), { timeout: 10000 });
const primeraPos2 = await speed.locator('tbody tr td').first().innerText();
if (p1 === 'Página 1 de 5' && primeraPos2 === '51') ok('paginación: «Página 1 de 5» → página 2 empieza en la posición 51');
else fallo(`paginación: ${p1} / ${primeraPos2}`);
await speed.locator('.classification-filters select').first().selectOption('Vet A M');
await page.waitForTimeout(600);
const categorias = await speed.locator('tbody tr td:nth-child(5)').allInnerTexts();
if (categorias.length > 0 && categorias.every((c) => c === 'Vet A M')) ok(`filtro de categoría «Vet A M»: ${categorias.length} filas`);
else fallo(`filtro de categoría: ${categorias.slice(0, 5)}`);

// --- Panel ---
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.fill('input[name="username"]', usuario);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-event h2');
const csrf = async () => (await contexto.cookies()).find((c) => c.name === 'penasagra_csrf')?.value ?? '';
const api = async (metodo, ruta, data) => page.request.fetch(base + ruta, { method: metodo, headers: { 'X-CSRF-Token': await csrf(), Origin: base }, data });
const privado = async () => (await (await page.request.get(base + '/api/content?admin=1')).json()).data;

const plantilla = (await privado()).races.find((r) => r.id === 'familiar-7k');
const tmp = await api('PUT', '/api/admin/carreras/verificacion-006', { ...plantilla, title: 'Prueba verificación 006', edition: '2026', published: false, version: 0 });
if (!tmp.ok()) throw new Error('No se pudo crear la prueba temporal: ' + (await tmp.text()));

const csv = (nombre, contenido) => { const ruta = join(tmpdir(), nombre); writeFileSync(ruta, contenido); return ruta; };
const DUP = csv('dup.csv', 'pos;dorsal;nombre;tiempo\n1;5;Ana;1:00\n2;5;Luis;1:05\n');
const TRES = csv('tres.csv', 'posicion;dorsal;nombre;apellidos;tiempo;categoria;club;sexo;estado\n1;101;Prueba;Uno;01:42:10;Senior;;F;\n2;102;Prueba;Dos;01:47:32;Senior;;M;\nDNF;103;Prueba;Tres;;Senior;;M;Retirado\n');
const UNA = csv('una.csv', 'pos;dorsal;nombre;tiempo\n1;201;Sustituto Único;00:59:00\n');

async function subirCsv(ruta) {
  await page.locator('input[aria-label="Subir CSV de clasificación"]').setInputFiles(ruta);
  await page.waitForTimeout(300);
}
async function guardar() {
  await page.click('.publish-card button[type="submit"]');
  await page.waitForFunction(() => document.body.innerText.includes('Guardado correctamente') || document.querySelector('[role="alert"]'), null, { timeout: 15000 });
}

await page.goto(base + '/admin/clasificaciones/nuevo', { waitUntil: 'networkidle' });
await page.fill('label:has-text("Nombre de la clasificación") input', 'Clasificación verificación 006');
await page.fill('label:has-text("Edición") input', '2026');
await page.selectOption('label:has-text("Carrera") select', 'verificacion-006');
await subirCsv(DUP);
const errorDup = (await page.textContent('.csv-pending [role="alert"]'))?.trim();
if (errorDup?.includes('repetido')) ok(`CSV con dorsal repetido: «${errorDup}»`); else fallo(`dorsal repetido: ${errorDup}`);
await subirCsv(TRES);
await page.click('button:has-text("Usar estos resultados")');
await page.waitForSelector('.csv-current');
await page.locator('.publish-card input[role="switch"]').check();
await guardar();
let lista = (await privado()).results.find((r) => r.id && r.title === 'Clasificación verificación 006');
if (lista?.participants === 3 && lista.published && (await texto()).includes('Guardado correctamente')) ok('alta desde el panel: 3 participantes, publicada');
else fallo(`alta: ${JSON.stringify(lista && { ...lista, rows: lista.rows.length })}`);
await page.goto(base + '/clasificaciones', { waitUntil: 'networkidle' });
if ((await texto()).includes('Clasificación verificación 006')) ok('visible en /clasificaciones'); else fallo('no visible en /clasificaciones');

await page.goto(base + '/admin/clasificaciones/' + lista.id, { waitUntil: 'networkidle' });
await subirCsv(UNA);
await page.click('button:has-text("Usar estos resultados")');
await page.waitForSelector('.csv-current');
await guardar();
lista = (await privado()).results.find((r) => r.id === lista.id);
if (lista.participants === 1 && lista.rows.map((r) => r.bib).join() === '201') ok('sustitución: queda 1 participante, sin mezclar');
else fallo(`sustitución: ${lista.participants} ${lista.rows.map((r) => r.bib)}`);

const borrarTrail = await api('DELETE', '/api/admin/carreras/trail-27k?version=' + (await privado()).races.find((r) => r.id === 'trail-27k').version);
if (borrarTrail.status() === 409) ok('borrar una prueba con clasificación → 409'); else fallo(`borrar trail-27k: ${borrarTrail.status()}`);

await page.goto(base + '/admin/clasificaciones', { waitUntil: 'networkidle' });
await page.locator('tr', { hasText: 'Clasificación verificación 006' }).locator('button[aria-label^="Eliminar"]').click();
await page.click('text=Eliminar clasificación');
await page.waitForSelector('.confirm-modal', { state: 'detached', timeout: 10000 });
const quedan = (await privado()).results.filter((r) => r.title === 'Clasificación verificación 006').length;
const limpieza = await api('DELETE', '/api/admin/carreras/verificacion-006?version=' + (await privado()).races.find((r) => r.id === 'verificacion-006').version);
if (quedan === 0 && limpieza.ok()) ok('borrado de la clasificación y de la prueba temporal'); else fallo(`limpieza: ${quedan} / ${limpieza.status()}`);
const finales = (await privado()).results.map((r) => `${r.id}:${r.participants}`).sort().join(' ');
if (finales === 'familiar-7k-2026:224 speed-14k-2026:205 trail-27k-2026:63') ok('estado final: solo las 3 clasificaciones reales');
else fallo(`estado final: ${finales}`);
await browser.close();
