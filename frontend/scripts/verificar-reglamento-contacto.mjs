// Feature 010 · Reglamento por edición y contacto: edición desde el panel, respaldo histórico,
// todas las ubicaciones públicas, mailto, validación sin éxito simulado, reinicio y restauración.
// Uso (desde frontend/, con Docker Compose en marcha):
//   ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-reglamento-contacto.mjs [url-base]
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!usuario || !password) { console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD'); process.exit(2); }
const raiz = fileURLToPath(new URL('../..', import.meta.url));
const sh = (orden) => execSync(orden, { cwd: raiz, stdio: ['ignore', 'pipe', 'pipe'] }).toString().trim();
// Consultas sin comillas simples (van dentro de sh -c '…').
const sql = (q) => sh(`docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "${q}"'`);
const TITULO = 'APARTADO DE VERIFICACIÓN 010';
const NUEVO = { email: 'verificacion@example.com', phone: '+34 600 11 22 33', instagram: 'https://www.instagram.com/cuenta_verificacion/' };

const browser = await navegador();
const page = await (await browser.newContext()).newPage();
const titulos = () => page.$$eval('.prose section h2', (h) => h.map((x) => x.textContent.trim()));
async function reglamentoPublico() {
  await page.goto(base + '/reglamento', { waitUntil: 'networkidle' });
  return { aviso: (await page.textContent('.prose .info-bar'))?.trim() ?? '', titulos: await titulos(), texto: await page.textContent('.prose') };
}
const privado = async () => (await (await page.request.get(base + '/api/content?admin=1')).json()).data;
async function guardar() {
  await page.click('button[type="submit"]');
  await page.waitForFunction(() => document.body.innerText.includes('Cambios guardados') || document.querySelector('.admin-error[role="alert"]'), null, { timeout: 15000 });
  return (await page.$('.admin-error[role="alert"]')) ? (await page.textContent('.admin-error[role="alert"]'))?.trim() : 'ok';
}
async function esperarApi() {
  for (let i = 0; i < 60; i++) {
    const r = await page.request.get(base + '/api/ready').catch(() => null);
    if (r?.ok()) return;
    await page.waitForTimeout(500);
  }
  throw new Error('La API no vuelve a estar disponible');
}

// 1. Reglamento importado: referencia 2026, sin el párrafo de prueba.
const original = await reglamentoPublico();
if (original.aviso.startsWith('Información de referencia: edición 2026') && original.titulos.length >= 5 && !original.texto.includes('PRUEBA'))
  ok(`reglamento de referencia 2026: aviso histórico y ${original.titulos.length} apartados, sin «PRUEBA»`);
else fallo(`reglamento importado: ${original.aviso} / ${original.titulos}`);

// 2. Panel: el editor parte del reglamento mostrado y guarda en la edición actual.
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.fill('input[name="username"]', usuario);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-event h2');
const datosIniciales = await privado();
const huella2026 = sql('SELECT md5(reglamento) FROM ediciones WHERE anio = 2026');
await page.goto(base + '/admin/reglamento', { waitUntil: 'networkidle' });
const editor = page.getByLabel('Texto completo');
const enEditor = await editor.inputValue();
await editor.fill(enEditor + `\n\n${TITULO}\nTexto añadido desde el panel.`);
let r = await guardar();
let publico = await reglamentoPublico();
const enActual = Number(sql('SELECT length(reglamento) FROM ediciones WHERE es_actual'));
if (enEditor === datosIniciales.regulation && r === 'ok' && publico.titulos.join('|') === [...original.titulos, TITULO].join('|')
  && enActual > 0 && sql('SELECT md5(reglamento) FROM ediciones WHERE anio = 2026') === huella2026)
  ok('reglamento: el editor parte del mostrado; el apartado nuevo se publica en la edición actual y 2026 no cambia');
else fallo(`reglamento editado: ${r} ${publico.titulos} actual=${enActual}`);

// 3. Contacto: un valor no válido se rechaza sin simular éxito.
await page.goto(base + '/admin/ajustes', { waitUntil: 'networkidle' });
await page.getByLabel('Instagram').fill('http://www.instagram.com/x/');
r = await guardar();
const exito = await page.isVisible('text=Cambios guardados');
if (r === 'Revisa el campo «Instagram».' && !exito && (await privado()).settings.instagram === datosIniciales.settings.instagram)
  ok('contacto: Instagram no válido → «Revisa el campo «Instagram».», sin guardar ni simular éxito');
else fallo(`validación: «${r}» éxito=${exito}`);

// 4. Contacto válido: todas las ubicaciones.
await page.goto(base + '/admin/ajustes', { waitUntil: 'networkidle' });
await page.getByLabel('Correo de la organización').fill(NUEVO.email);
await page.getByLabel('Teléfono de contacto').fill(NUEVO.phone);
await page.getByLabel('Instagram').fill(NUEVO.instagram);
r = await guardar();
async function ubicaciones() {
  const res = {};
  for (const ruta of ['/contacto', '/', '/inscripciones']) {
    await page.goto(base + ruta, { waitUntil: 'networkidle' });
    res[ruta] = {
      correos: await page.$$eval('a[href^="mailto:"]', (a) => a.map((x) => x.getAttribute('href'))),
      telefonos: await page.$$eval('a[href^="tel:"]', (a) => a.map((x) => [x.getAttribute('href'), x.innerText.replace(/\s+/g, ' ').trim()])),
      instagram: await page.$$eval('a[href*="instagram"]', (a) => a.map((x) => [x.getAttribute('href'), x.innerText.trim()])),
      texto: await page.evaluate(() => document.body.innerText),
    };
  }
  return res;
}
let u = await ubicaciones();
const viejos = [datosIniciales.settings.email, datosIniciales.settings.phone, 'asociacion_penasagra'];
const todasNuevas = Object.values(u).every((p) => p.correos.every((h) => h === 'mailto:' + NUEVO.email) && p.instagram.every(([h]) => h === NUEVO.instagram)
  && p.instagram.length > 0 && p.correos.length > 0 && viejos.every((v) => !p.texto.includes(v)));
const contacto = u['/contacto'];
if (r === 'ok' && todasNuevas && contacto.telefonos[0]?.[0] === 'tel:' + NUEVO.phone && contacto.telefonos[0]?.[1].includes(`${NUEVO.phone} · Imanol`)
  && contacto.instagram.some(([, t]) => t === '@cuenta_verificacion') && contacto.texto.includes('Plaza de Cosío · Rionansa'))
  ok('contacto: correo, teléfono e Instagram nuevos en /contacto, pie e inscripciones; 0 valores anteriores; «@cuenta_verificacion»');
else fallo(`ubicaciones: ${r} ${JSON.stringify({ ...u, '/contacto': { ...contacto, texto: undefined }, '/': undefined, '/inscripciones': undefined })}`);

// 5. Formulario: prepara un mailto al correo configurado y no afirma un envío.
await page.goto(base + '/contacto', { waitUntil: 'networkidle' });
const peticiones = [];
page.on('request', (q) => peticiones.push(q.url()));
await page.fill('form.contact-form input[name="name"]', 'Verificación');
await page.fill('form.contact-form input[name="email"]', 'visitante@example.com');
await page.fill('form.contact-form input[name="subject"]', 'Consulta de prueba');
await page.fill('form.contact-form textarea[name="message"]', 'Mensaje de verificación.');
await page.click('form.contact-form button[type="submit"]');
await page.waitForSelector('form.contact-form [role="status"]');
await page.waitForTimeout(300);
const aviso = await page.textContent('form.contact-form [role="status"]');
const mailto = peticiones.find((p) => p.startsWith('mailto:'));
if (mailto?.startsWith(`mailto:${NUEVO.email}?subject=Consulta%20de%20prueba&body=`) && peticiones.every((p) => p.startsWith('mailto:')) && aviso.includes('Revísalo y envíalo') && !/enviado/i.test(aviso))
  ok('formulario: mailto al correo configurado, sin peticiones al servidor ni «enviado»');
else fallo(`mailto: ${mailto} ${peticiones} «${aviso}»`);

// 6. Reinicio: reglamento y contacto persisten.
sh('docker compose restart api');
await esperarApi();
publico = await reglamentoPublico();
const tras = (await (await page.request.get(base + '/api/content')).json()).data.settings;
if (publico.titulos.includes(TITULO) && tras.email === NUEVO.email && tras.phone === NUEVO.phone && tras.instagram === NUEVO.instagram)
  ok('reinicio de la API: reglamento y contacto persisten');
else fallo(`reinicio: ${publico.titulos} ${JSON.stringify(tras)}`);

// 7. Restauración: contacto original desde el panel y reglamento propio de la edición actual vaciado.
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.goto(base + '/admin/ajustes', { waitUntil: 'networkidle' });
await page.getByLabel('Correo de la organización').fill(datosIniciales.settings.email);
await page.getByLabel('Teléfono de contacto').fill(datosIniciales.settings.phone);
await page.getByLabel('Instagram').fill(datosIniciales.settings.instagram);
r = await guardar();
sql('UPDATE ediciones SET reglamento = DEFAULT WHERE es_actual');
publico = await reglamentoPublico();
const final = (await privado()).settings;
u = await ubicaciones();
if (r === 'ok' && publico.titulos.join('|') === original.titulos.join('|') && publico.aviso === original.aviso
  && ['email', 'phone', 'instagram'].every((k) => final[k] === datosIniciales.settings[k]) && u['/contacto'].instagram.some(([, t]) => t === '@asociacion_penasagra'))
  ok('restaurado: reglamento de referencia 2026 y datos de contacto originales');
else fallo(`restauración: ${r} ${publico.titulos} ${JSON.stringify(final)}`);
await browser.close();
