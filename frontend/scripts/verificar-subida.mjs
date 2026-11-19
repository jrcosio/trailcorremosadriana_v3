// Feature 003 · Subida real desde el panel y vista previa servida desde /media (a través de Caddy).
// Uso: ADMIN_USUARIO=admin ADMIN_PASSWORD=… node scripts/verificar-subida.mjs [url-base]
import { fileURLToPath } from 'node:url';
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!usuario || !password) {
  console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD');
  process.exit(2);
}
const imagen = fileURLToPath(new URL('../public/reused/img/dorsal_solidario.webp', import.meta.url));

const browser = await navegador();
const page = await browser.newPage();
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.fill('input[name="username"]', usuario);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-event h2');

await page.goto(base + '/admin/noticias/nuevo', { waitUntil: 'networkidle' });
const entrada = page.locator('.upload-field input[type="file"]').first();
await entrada.setInputFiles(imagen);
await page.waitForSelector('img.upload-preview', { timeout: 15000 });
const src = await page.getAttribute('img.upload-preview', 'src');
const cargada = await page.evaluate(() => {
  const img = document.querySelector('img.upload-preview');
  return img instanceof HTMLImageElement && img.complete && img.naturalWidth > 0;
});
if (!/^\/media\/[0-9a-f]{32}\.webp$/.test(src ?? '')) fallo(`referencia inesperada «${src}»`);
else if (!cargada) fallo('la vista previa no carga desde /media');
else ok(`subida desde el panel: vista previa ${src}`);

// Un tipo no admitido muestra el error del servidor sin vista previa nueva.
await page.goto(base + '/admin/noticias/nuevo', { waitUntil: 'networkidle' });
await page.locator('.upload-field input[type="file"]').first().setInputFiles({
  name: 'icono.svg',
  mimeType: 'image/svg+xml',
  buffer: Buffer.from('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'),
});
await page.waitForSelector('.admin-card .error-message[role="alert"]', { timeout: 10000 });
const aviso = (await page.textContent('.admin-card .error-message[role="alert"]'))?.trim();
if (!aviso?.includes('Sube imágenes JPG, PNG o WebP')) fallo(`rechazo de SVG: «${aviso}»`);
else ok('SVG rechazado con mensaje claro');
await browser.close();
