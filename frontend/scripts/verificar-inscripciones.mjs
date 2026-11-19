// Feature 005 · Matriz del Dorsal Solidario en Inicio, Solidaridad e Inscripciones, tarjetas de
// inscripción y guardado desde el panel. Usa URLs de ejemplo y lo restaura todo al terminar.
// Uso: ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-inscripciones.mjs [url-base]
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!usuario || !password) { console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD'); process.exit(2); }
const DORSAL = 'https://example.com/dorsal-solidario-prueba';
const INSC_TRAIL = 'https://example.com/inscripcion-trail-prueba';
const MENSAJES = {
  cerradas: 'Disponible cuando se abran las inscripciones.',
  pendiente: 'Pronto estará disponible el enlace para conseguir tu dorsal solidario.',
  disponible: 'Completa el pago en la web oficial de inscripciones.',
};

const browser = await navegador();
const contexto = await browser.newContext();
const page = await contexto.newPage();
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.fill('input[name="username"]', usuario);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-event h2');

const csrf = async () => (await contexto.cookies()).find((c) => c.name === 'penasagra_csrf')?.value ?? '';
const api = async (metodo, ruta, data) =>
  page.request.fetch(base + ruta, { method: metodo, headers: { 'X-CSRF-Token': await csrf(), Origin: base }, data });
const privado = async () => (await (await page.request.get(base + '/api/content?admin=1')).json()).data;

async function enlaceTrail(url) {
  const trail = (await privado()).races.find((r) => r.id === 'trail-27k');
  const r = await api('PUT', '/api/admin/carreras/trail-27k', { ...trail, registration: url });
  if (!r.ok()) throw new Error('No se pudo fijar el enlace de la Trail: ' + (await r.text()));
}
async function inscripciones(abiertas, url) {
  const actual = await (await page.request.get(base + '/api/admin/inscripciones')).json();
  const r = await api('PUT', '/api/admin/inscripciones', { ...actual, registrationsOpen: abiertas, solidarityRegistration: url });
  if (!r.ok()) throw new Error('No se pudo fijar el estado: ' + (await r.text()));
}

async function bloque(ruta, selector) {
  const p = await contexto.newPage();
  await p.goto(base + ruta, { waitUntil: 'networkidle' });
  const datos = await p.evaluate((sel) => {
    const b = document.querySelector(sel);
    if (!b) return { existe: false, texto: document.body.innerText, enlacesPagina: [...document.querySelectorAll('a')].map((a) => a.href) };
    const a = b.querySelector('a.donation-button');
    return {
      existe: true,
      enlace: a?.getAttribute('href') ?? null,
      destino: a?.getAttribute('target') ?? null,
      boton: (a ?? b.querySelector('button.donation-button'))?.textContent?.trim(),
      deshabilitado: !!b.querySelector('button.donation-button[disabled]'),
      nota: b.querySelector('.donation-note')?.textContent?.trim(),
      internos: [...b.querySelectorAll('a')].map((x) => x.getAttribute('href')).filter((h) => h?.startsWith('/')),
      texto: document.body.innerText,
    };
  }, selector);
  await p.close();
  return datos;
}

const PAGINAS = [['/', '.donation-banner'], ['/solidaridad', '.donation-card'], ['/inscripciones', '.donation-callout']];
const ESTADOS = [
  ['cerradas sin URL', false, ''],
  ['cerradas con URL', false, DORSAL],
  ['abiertas sin URL', true, ''],
  ['abiertas con URL', true, DORSAL],
];
let correctas = 0;
await enlaceTrail(INSC_TRAIL); // permite abrir sin URL del dorsal (FR-003)
for (const [nombre, abiertas, url] of ESTADOS) {
  await inscripciones(abiertas, url);
  for (const [ruta, selector] of PAGINAS) {
    const b = await bloque(ruta, selector);
    let correcto;
    if (ruta === '/inscripciones' && !abiertas) {
      correcto = !b.existe && b.texto.includes('Inscripciones aún cerradas') && !b.enlacesPagina.some((h) => h.startsWith(DORSAL));
    } else if (abiertas && url) {
      correcto = b.existe && b.enlace === DORSAL && b.destino === '_blank' && b.boton === 'Pagar dorsal solidario' && b.nota === MENSAJES.disponible && b.internos.length === 0;
    } else {
      correcto = b.existe && b.enlace === null && b.deshabilitado && b.boton === 'Próximamente disponible'
        && b.nota === (abiertas ? MENSAJES.pendiente : MENSAJES.cerradas) && b.internos.length === 0;
    }
    if (correcto) { correctas++; ok(`${nombre} · ${ruta}`); } else fallo(`${nombre} · ${ruta}: ${JSON.stringify({ ...b, texto: undefined, enlacesPagina: undefined })}`);
  }
  if (nombre === 'abiertas sin URL') {
    // Tarjetas de /inscripciones (US3): la Trail enlaza fuera; las demás, pendientes.
    const p = await contexto.newPage();
    await p.goto(base + '/inscripciones', { waitUntil: 'networkidle' });
    const enlaceTarjeta = await p.getAttribute('.signup-card a:has-text("Inscribirme")', 'href').catch(() => null);
    const pendientes = await p.locator('.signup-card', { hasText: 'Inscripción pendiente para esta prueba.' }).count();
    await p.close();
    if (enlaceTarjeta === INSC_TRAIL && pendientes === 2) ok('tarjetas: «Inscribirme» en la Trail y 2 pendientes');
    else fallo(`tarjetas: ${enlaceTarjeta} / ${pendientes}`);
  }
}
console.log(`matriz: ${correctas}/12`);

// Panel: abrir sin destinos se rechaza; con el dorsal se guarda; cerrar conserva la URL.
await enlaceTrail('');
await inscripciones(false, '');
await page.goto(base + '/admin/inscripciones', { waitUntil: 'networkidle' });
await page.locator('input[role="switch"]').first().check();
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-error[role="alert"]');
const aviso = (await page.textContent('.admin-error[role="alert"]'))?.trim();
if (aviso?.startsWith('No puedes abrir las inscripciones')) ok('panel: abrir sin destinos rechazado con aviso claro');
else fallo(`panel: aviso inesperado «${aviso}»`);
await page.goto(base + '/admin/inscripciones', { waitUntil: 'networkidle' });
await page.fill('input[placeholder^="https://web-de-inscripciones"]', DORSAL);
await page.locator('input[role="switch"]').first().check();
await page.click('button[type="submit"]');
await page.waitForFunction(() => document.body.innerText.includes('Cambios guardados'), null, { timeout: 15000 });
await page.goto(base + '/admin/inscripciones', { waitUntil: 'networkidle' });
await page.locator('input[role="switch"]').first().uncheck();
await page.click('button[type="submit"]');
await page.waitForFunction(() => document.body.innerText.includes('Cambios guardados'), null, { timeout: 15000 });
const tras = await (await page.request.get(base + '/api/admin/inscripciones')).json();
if (!tras.registrationsOpen && tras.solidarityRegistration === DORSAL) ok('panel: abrir con el dorsal y cerrar conservando la URL');
else fallo(`panel: estado tras cerrar ${JSON.stringify(tras)}`);

// Restaurar: cerradas y sin enlaces.
await inscripciones(false, '');
const final = await (await page.request.get(base + '/api/admin/inscripciones')).json();
if (!final.registrationsOpen && final.solidarityRegistration === '') ok('restaurado: cerradas y sin enlaces');
else fallo('restaurar');
await browser.close();
