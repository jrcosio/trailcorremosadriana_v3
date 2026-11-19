// Feature 004 · Evento y pruebas desde el panel hasta la web pública (a través de Caddy).
// Restaura los datos al terminar. Uso: ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-evento-carreras.mjs
import { writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!usuario || !password) { console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD'); process.exit(2); }
const foto = fileURLToPath(new URL('../public/reused/img/familiar_trail_inscripciones.webp', import.meta.url));
const TOAST = 'Cambios guardados';

const browser = await navegador();
async function sesion() {
  const contexto = await browser.newContext();
  const page = await contexto.newPage();
  await page.goto(base + '/admin', { waitUntil: 'networkidle' });
  await page.fill('input[name="username"]', usuario);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForSelector('.admin-event h2');
  return page;
}
const texto = (page) => page.evaluate(() => document.body.innerText);
async function guardarYEsperar(page) {
  await page.click('button[type="submit"]');
  await page.waitForFunction((t) => document.body.innerText.includes(t) || document.querySelector('[role="alert"]'), TOAST, { timeout: 15000 });
  const alerta = await page.$('.admin-error[role="alert"]');
  return alerta ? (await alerta.textContent())?.trim() : 'ok';
}
async function privado(page) {
  return (await (await page.request.get(base + '/api/content?admin=1')).json()).data;
}

const page = await sesion();

// 1. Fecha de verano y contador en la portada.
async function fecha(valor) {
  await page.goto(base + '/admin/evento', { waitUntil: 'networkidle' });
  await page.fill('input[type="datetime-local"]', valor);
  return guardarYEsperar(page);
}
let r = await fecha('2027-07-10T09:00');
await page.goto(base + '/', { waitUntil: 'networkidle' });
const portada = await texto(page);
if (r !== 'ok' || !portada.includes('10 de julio de 2027') || portada.includes('está por confirmar')) fallo(`fecha de verano en portada (${r})`);
else ok('fecha 10/07/2027 09:00 guardada y visible en la portada con contador');
await page.goto(base + '/admin/evento', { waitUntil: 'networkidle' });
if ((await page.inputValue('input[type="datetime-local"]')) !== '2027-07-10T09:00') fallo('la hora de verano no se reabre igual');
else ok('reabrir: 09:00 (verano)');

// 2. Fecha de invierno (SC-002).
r = await fecha('2027-01-15T09:00');
await page.goto(base + '/admin/evento', { waitUntil: 'networkidle' });
if (r !== 'ok' || (await page.inputValue('input[type="datetime-local"]')) !== '2027-01-15T09:00') fallo('la hora de invierno no se reabre igual');
else ok('reabrir: 09:00 (invierno)');

// 3. Restaurar sin fecha.
r = await fecha('');
await page.goto(base + '/', { waitUntil: 'networkidle' });
if (r !== 'ok' || !(await texto(page)).includes('La fecha de 2027 está por confirmar')) fallo('restaurar sin fecha');
else ok('sin fecha: «La fecha de 2027 está por confirmar»');

// 4. Editar la distancia de la Trail y restaurar.
async function editarKm(valor) {
  await page.goto(base + '/admin/recorridos/trail-27k', { waitUntil: 'networkidle' });
  await page.fill('input[name="km"]', valor);
  return guardarYEsperar(page);
}
r = await editarKm('28');
await page.goto(base + '/carreras/trail-27k', { waitUntil: 'networkidle' });
const detalle = await texto(page);
if (r !== 'ok' || !/28\s*K/.test(detalle)) fallo(`editar km (${r})`);
else ok('km 28 visible en /carreras/trail-27k');
r = await editarKm('27');
if (r !== 'ok') fallo('restaurar km'); else ok('km restaurado a 27');

// 5. Nueva prueba: borrador → publicada → retirada → borrada.
const TITULO = 'Prueba de verificación 004';
await page.goto(base + '/admin/recorridos/nuevo', { waitUntil: 'networkidle' });
await page.fill('input[name="title"]', TITULO);
await page.fill('input[name="km"]', '3');
await page.fill('input[name="elevation"]', '100');
await page.fill('input[name="price"]', '5 €');
await page.locator('.upload-field input[type="file"]').first().setInputFiles(foto);
await page.waitForSelector('img.upload-preview');
r = await guardarYEsperar(page);
const nueva = (await privado(page)).races.find((x) => x.title === TITULO);
await page.goto(base + '/carreras', { waitUntil: 'networkidle' });
if (r !== 'ok' || !nueva || nueva.published || (await texto(page)).includes(TITULO)) fallo(`nueva prueba como borrador (${r})`);
else ok(`nueva prueba ${nueva.id} creada como borrador y oculta en /carreras`);

async function publicar(valor) {
  await page.goto(base + '/admin/recorridos/' + nueva.id, { waitUntil: 'networkidle' });
  const sw = page.locator('.publish-card input[role="switch"]');
  if ((await sw.isChecked()) !== valor) await sw.click();
  return guardarYEsperar(page);
}
r = await publicar(true);
await page.goto(base + '/carreras', { waitUntil: 'networkidle' });
if (r !== 'ok' || !(await texto(page)).includes(TITULO)) fallo('publicar'); else ok('publicada: visible en /carreras');
r = await publicar(false);
await page.goto(base + '/carreras/' + nueva.id, { waitUntil: 'networkidle' });
if (r !== 'ok' || !(await texto(page)).includes('Este sendero no está en el mapa.')) fallo('retirar'); else ok('retirada: su detalle muestra «Este sendero no está en el mapa.»');

await page.goto(base + '/admin/recorridos', { waitUntil: 'networkidle' });
await page.locator('tr', { hasText: TITULO }).locator('button[aria-label^="Eliminar"]').click();
await page.click('text=Eliminar contenido');
await page.waitForSelector('.confirm-modal', { state: 'detached', timeout: 10000 });
if ((await privado(page)).races.some((x) => x.title === TITULO)) fallo('borrar'); else ok('borrada del panel y de la web');

// 6. Conflicto entre dos sesiones (FR-007).
const otra = await sesion();
await page.goto(base + '/admin/recorridos/speed-14k', { waitUntil: 'networkidle' });
await otra.goto(base + '/admin/recorridos/speed-14k', { waitUntil: 'networkidle' });
await otra.fill('input[name="price"]', '19 €');
const r1 = await guardarYEsperar(otra);
await page.fill('input[name="price"]', '17 €');
const r2 = await guardarYEsperar(page);
if (r1 !== 'ok' || !r2?.startsWith('Otra persona ha modificado')) fallo(`conflicto: ${r1} / ${r2}`);
else ok('conflicto: la segunda sesión recibe el aviso y no sobrescribe');
await otra.goto(base + '/admin/recorridos/speed-14k', { waitUntil: 'networkidle' });
await otra.fill('input[name="price"]', '18 €');
if ((await guardarYEsperar(otra)) !== 'ok') fallo('restaurar precio'); else ok('precio restaurado a 18 €');

// 7. GPX en el detalle (US4/AC2): sin GPX no hay descarga; con GPX subido sí; restaurar.
await page.goto(base + '/carreras/trail-27k', { waitUntil: 'networkidle' });
const sinGpx = !(await texto(page)).includes('Descargar GPX');
const gpx = join(tmpdir(), 'trail-27k-verificacion.gpx');
writeFileSync(gpx, '<?xml version="1.0" encoding="UTF-8"?><gpx version="1.1" creator="verificacion"><trk><name>Trail</name><trkseg><trkpt lat="43.2" lon="-4.5"/></trkseg></trk></gpx>');
await page.goto(base + '/admin/recorridos/trail-27k', { waitUntil: 'networkidle' });
await page.locator('input[type="file"][aria-label="Subir Track GPX"]').setInputFiles(gpx);
await page.waitForFunction(() => !document.body.innerText.includes('Subiendo…'), null, { timeout: 15000 });
r = await guardarYEsperar(page);
await page.goto(base + '/carreras/trail-27k', { waitUntil: 'networkidle' });
const enlace = await page.getAttribute('a:has-text("Descargar GPX")', 'href').catch(() => null);
const descarga = enlace ? await page.request.get(base + enlace) : null;
const disposicion = descarga?.headers()['content-disposition'] ?? '';
if (!sinGpx || r !== 'ok' || !/^\/media\/[0-9a-f]{32}\.gpx$/.test(enlace ?? '') || !disposicion.startsWith('attachment')) {
  fallo(`GPX en el detalle (sin GPX: ${sinGpx}, guardado: ${r}, enlace: ${enlace}, disposición: ${disposicion})`);
} else ok(`GPX: sin archivo no hay descarga; subido → «Descargar GPX» ${enlace} (attachment)`);
const csrf = (await page.context().cookies()).find((c) => c.name === 'penasagra_csrf')?.value ?? '';
const actual = (await privado(page)).races.find((x) => x.id === 'trail-27k');
const restaurar = await page.request.put(base + '/api/admin/carreras/trail-27k', {
  headers: { 'X-CSRF-Token': csrf, Origin: base }, data: { ...actual, gpx: '' },
});
await page.goto(base + '/carreras/trail-27k', { waitUntil: 'networkidle' });
if (!restaurar.ok() || (await texto(page)).includes('Descargar GPX')) fallo('restaurar sin GPX'); else ok('GPX retirado: sin descarga');

// 8. Fecha pasada (casos límite): contador a cero, sin negativos; restaurar sin fecha.
r = await fecha('2020-01-01T09:00');
await page.goto(base + '/', { waitUntil: 'networkidle' });
await page.waitForTimeout(1200);
const numeros = await page.$$eval('.countdown-numbers strong', (els) => els.map((e) => e.textContent));
const cabecera = await page.textContent('.countdown-heading');
if (r !== 'ok' || !cabecera?.includes('Nos vemos en la montaña') || numeros.some((n) => n !== '00')) fallo(`fecha pasada: ${cabecera} ${numeros}`);
else ok('fecha pasada: «Nos vemos en la montaña» y contador 00:00:00:00');
r = await fecha('');
if (r !== 'ok') fallo('restaurar sin fecha'); else ok('restaurado sin fecha');

await browser.close();
