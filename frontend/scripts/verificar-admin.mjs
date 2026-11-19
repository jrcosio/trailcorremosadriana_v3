// /admin rechaza credenciales incorrectas con mensaje genérico (002) y las vistas de diseño no escriben.
// Uso: node scripts/verificar-admin.mjs [url-base]
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const browser = await navegador();
const page = await browser.newPage();
const escrituras = [];
page.on('request', (r) => {
  if (r.url().includes('/api/') && !['GET', 'HEAD'].includes(r.method())) escrituras.push(`${r.method()} ${r.url()}`);
});

// 1. Acceso con credenciales incorrectas: mensaje genérico y sin acceso.
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.fill('input[name="username"]', 'usuario-inexistente');
await page.fill('input[name="password"]', 'cualquier-cosa');
await page.click('button[type="submit"]');
await page.waitForSelector('.error-message[role="alert"]');
const error = await page.textContent('.error-message[role="alert"]');
const sigueEnLogin = await page.isVisible('input[name="password"]');
const cookies = await page.context().cookies();
if (error?.trim() !== 'Usuario o contraseña incorrectos.') fallo(`/admin: mensaje inesperado «${error}»`);
else if (!sigueEnLogin) fallo('/admin: el formulario desapareció (¿acceso concedido?)');
else if (cookies.length) fallo('/admin: se emitieron cookies');
else ok('/admin: mensaje genérico, sin acceso y sin cookies');

// 2. Vista de diseño: guardar no envía escrituras.
escrituras.length = 0;
await page.goto(base + '/pantallas/admin/noticias/nuevo', { waitUntil: 'networkidle' });
await page.fill('input[name="title"]', 'Noticia de prueba de diseño').catch(() => {});
await page.fill('textarea[name="body"]', 'Texto de prueba.').catch(() => {});
await page.click('button[type="submit"]');
await page.waitForTimeout(500);
const texto = await page.evaluate(() => document.body.innerText);
if (!texto.includes('Esta es una vista de diseño. Entra en /admin para guardar cambios reales.')) fallo('vista de diseño: falta el aviso');
else if (escrituras.length) fallo('vista de diseño: se enviaron escrituras: ' + escrituras.join(', '));
else ok('vista de diseño: aviso mostrado y ninguna escritura enviada');
await browser.close();
