// Feature 002 · Acceso real al panel de extremo a extremo (a través de Caddy).
// Uso: ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-acceso.mjs [url-base] [--bloqueo] [--api-caida]
//   --bloqueo   comprueba el bloqueo tras 8 fallos (después hay que limpiar limites_login)
//   --api-caida comprueba el mensaje de servicio con la API detenida (solo ese paso)
import { fallo, navegador, ok } from './comun.mjs';

const args = process.argv.slice(2);
const base = args.find((a) => !a.startsWith('--')) ?? 'http://localhost:8080';
const usuario = process.env.ADMIN_USUARIO;
const password = process.env.ADMIN_PASSWORD;
const GENERICO = 'Usuario o contraseña incorrectos.';

const browser = await navegador();
const contexto = await browser.newContext();
const page = await contexto.newPage();

async function enviarAcceso(u, p) {
  await page.goto(base + '/admin', { waitUntil: 'networkidle' });
  await page.fill('input[name="username"]', u);
  await page.fill('input[name="password"]', p);
  await page.click('button[type="submit"]');
}

async function mensajeAcceso() {
  await page.waitForSelector('.error-message[role="alert"]', { timeout: 10000 });
  return (await page.textContent('.error-message[role="alert"]'))?.trim();
}

if (args.includes('--api-caida')) {
  await enviarAcceso('admin', 'cualquier-contraseña');
  const m = await mensajeAcceso();
  if (m !== 'El servicio no está disponible. Inténtalo más tarde.') fallo(`API caída: mensaje inesperado «${m}»`);
  else if (!(await page.isVisible('input[name="password"]'))) fallo('API caída: se concedió acceso');
  else ok('API caída: error de servicio y sin acceso');
  await browser.close();
  process.exit();
}

if (!usuario || !password) {
  console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD');
  process.exit(2);
}

// 1. Credenciales incorrectas → mensaje genérico (usuario inexistente y contraseña errónea).
for (const [u, p] of [['no-existe', 'cualquier-contraseña'], [usuario, 'contraseña-equivocada']]) {
  await enviarAcceso(u, p);
  const m = await mensajeAcceso();
  if (m !== GENERICO) fallo(`acceso erróneo (${u}): «${m}»`);
  else ok(`acceso erróneo (${u}): mensaje genérico`);
}

// 2. Acceso correcto → resumen en menos de 30 s (SC-001).
const t0 = Date.now();
await enviarAcceso(usuario, password);
await page.waitForSelector('.admin-event h2', { timeout: 30000 });
const segundos = (Date.now() - t0) / 1000;
const titulo = await page.textContent('.admin-event h2');
if (!titulo?.includes('Peñasagra 2027')) fallo(`resumen inesperado: «${titulo}»`);
else ok(`acceso correcto: resumen «${titulo}» en ${segundos.toFixed(1)} s`);
const cookies = await contexto.cookies();
const sesion = cookies.find((c) => c.name === 'penasagra_admin');
const csrf = cookies.find((c) => c.name === 'penasagra_csrf');
if (!sesion?.httpOnly || sesion.sameSite !== 'Strict' || !csrf || csrf.httpOnly) fallo('atributos de cookies inesperados');
else ok('cookies: sesión HttpOnly+Strict; CSRF legible');

// 3. Recarga → sigue dentro.
await page.reload({ waitUntil: 'networkidle' });
if (!(await page.isVisible('.admin-event h2'))) fallo('la sesión no sobrevive a la recarga');
else ok('recarga: sesión mantenida');

// 4. Un guardado que el servidor rechaza → aviso claro, sin simular éxito ni cambiar datos.
// Desde la feature 010 todas las secciones persisten: se usa un dato no válido en /admin/ajustes.
await page.goto(base + '/admin/ajustes', { waitUntil: 'networkidle' });
const instagramAntes = await page.getByLabel('Instagram').inputValue();
await page.getByLabel('Instagram').fill('http://www.instagram.com/no-valido/');
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-error[role="alert"]', { timeout: 10000 });
const aviso = (await page.textContent('.admin-error[role="alert"]'))?.trim();
const exito = await page.isVisible('text=Cambios guardados');
const guardado = (await (await page.request.get(base + '/api/content')).json()).data.settings.instagram;
if (aviso !== 'Revisa el campo «Instagram».' || exito || guardado !== instagramAntes) fallo(`error del servidor: «${aviso}» éxito=${exito}`);
else ok('error del servidor: aviso claro, sin éxito simulado ni cambios');

// 5. Cerrar sesión → formulario; la cookie anterior ya no sirve.
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.click('button[aria-label="Cerrar sesión"]');
await page.waitForSelector('input[name="password"]', { timeout: 10000 });
const anterior = await fetch(base + '/api/content?admin=1', { headers: { cookie: `penasagra_admin=${sesion.value}` } });
if (anterior.status !== 401) fallo(`tras cerrar sesión la cookie anterior devuelve ${anterior.status}`);
else ok('cierre de sesión: formulario y cookie anterior rechazada (401)');

// 6. Bloqueo tras 8 fallos (opcional).
if (args.includes('--bloqueo')) {
  for (let i = 0; i < 8; i++) {
    await enviarAcceso(usuario, 'contraseña-equivocada-' + i);
    await mensajeAcceso();
  }
  await enviarAcceso(usuario, password);
  const m = await mensajeAcceso();
  if (!m?.startsWith('Demasiados intentos')) fallo(`bloqueo: «${m}»`);
  else ok('bloqueo: 9.º intento (correcto) rechazado con «Demasiados intentos…»');
}

await browser.close();
