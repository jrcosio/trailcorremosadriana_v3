// Feature 008 · Galería: históricos, filtro, álbum nuevo con fotos, visor accesible y limpieza.
// Uso: ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-galeria.mjs [url-base]
import { fileURLToPath } from 'node:url';
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!usuario || !password) { console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD'); process.exit(2); }
const f = (n) => fileURLToPath(new URL(`../public/reused/img/${n}`, import.meta.url));
const browser = await navegador();
const contexto = await browser.newContext();
const page = await contexto.newPage();
const TITULO = 'Álbum de verificación 008';

// 1. Históricos y filtro.
await page.goto(base + '/galeria', { waitUntil: 'networkidle' });
const anios = await page.$$eval('.album-card .album-year', (e) => e.map((x) => x.textContent));
await page.click('.tabs button:has-text("2025")');
const filtrados = await page.$$eval('.album-card .album-year', (e) => e.map((x) => x.textContent));
if (anios.join() === '2026,2025,2024' && filtrados.join() === '2025') ok('galería: 3 históricos ordenados y filtro 2025'); else fallo(`galería ${anios} / ${filtrados}`);
await page.goto(base + '/galeria/edicion-2026', { waitUntil: 'networkidle' });
const enlace = await page.getAttribute('a:has-text("Abrir álbum en Google Fotos")', 'href');
if (enlace === 'https://photos.app.goo.gl/A5ksyLsC3cSc2HHWA') ok('enlace histórico de 2026 exacto'); else fallo(`enlace ${enlace}`);

// 2. Panel: álbum nuevo con portada y 2 fotos (borrador).
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
await page.fill('input[name="username"]', usuario);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-event h2');
const privado = async () => (await (await page.request.get(base + '/api/content?admin=1')).json()).data;
async function guardar() {
  await page.click('button[type="submit"]');
  await page.waitForFunction(() => document.body.innerText.includes('Cambios guardados') || document.querySelector('.admin-error[role="alert"]'), null, { timeout: 15000 });
  return (await page.$('.admin-error[role="alert"]')) ? (await page.textContent('.admin-error[role="alert"]'))?.trim() : 'ok';
}
await page.goto(base + '/admin/galeria/nuevo', { waitUntil: 'networkidle' });
await page.fill('input[name="title"]', TITULO);
await page.fill('input[name="year"]', '2027');
const entradas = page.locator('.upload-field input[type="file"]');
await entradas.nth(0).setInputFiles(f('trail_inscripciones.webp'));
await page.waitForSelector('img.upload-preview');
await entradas.nth(1).setInputFiles([f('speed_trail_inscripciones.webp'), f('familiar_trail_inscripciones.webp')]);
await page.waitForFunction(() => document.querySelectorAll('.admin-photo-grid img').length === 2, null, { timeout: 15000 });
let r = await guardar();
const album = (await privado()).albums.find((a) => a.title === TITULO);
await page.goto(base + '/galeria', { waitUntil: 'networkidle' });
const oculto = !(await page.evaluate(() => document.body.innerText)).includes(TITULO);
if (r === 'ok' && album && !album.published && album.photos.length === 2 && oculto) ok('álbum nuevo: borrador con 2 fotos, oculto'); else fallo(`nuevo: ${r} ${JSON.stringify(album)}`);

await page.goto(base + '/admin/galeria/' + album.id, { waitUntil: 'networkidle' });
await page.locator('.publish-card input[role="switch"]').check();
r = await guardar();
await page.goto(base + '/galeria/' + album.id, { waitUntil: 'networkidle' });
const alts = await page.$$eval('.photo-grid img', (imgs) => imgs.map((i) => i.alt));
if (r === 'ok' && alts.join('|') === `${TITULO} · fotografía 1|${TITULO} · fotografía 2`) ok('publicado: 2 fotos con texto alternativo'); else fallo(`publicado: ${r} ${alts}`);

// 3. Visor accesible.
const miniatura = page.locator('.photo-grid button').first();
await miniatura.click();
await page.waitForSelector('.lightbox');
const enfocadoAlAbrir = await page.evaluate(() => document.activeElement?.getAttribute('aria-label'));
let dentro = true;
for (let i = 0; i < 10; i++) {
  await page.keyboard.press(i % 3 === 2 ? 'Shift+Tab' : 'Tab');
  dentro &&= await page.evaluate(() => !!document.activeElement?.closest('.lightbox'));
}
const srcAntes = await page.getAttribute('.lightbox img', 'src');
await page.keyboard.press('ArrowRight');
const srcDespues = await page.getAttribute('.lightbox img', 'src');
await page.keyboard.press('Escape');
await page.waitForSelector('.lightbox', { state: 'detached' });
await page.waitForTimeout(100);
const vuelve = await page.evaluate(() => document.activeElement?.getAttribute('aria-label'));
if (enfocadoAlAbrir === 'Cerrar fotografía' && dentro && srcAntes !== srcDespues && vuelve === 'Ampliar fotografía 1') ok('visor: foco inicial, 10 Tab dentro, flechas, Escape y foco devuelto a la miniatura');
else fallo(`visor: ${enfocadoAlAbrir} ${dentro} ${srcAntes === srcDespues} ${vuelve}`);

// 4. Quitar una foto y borrar.
await page.goto(base + '/admin/galeria/' + album.id, { waitUntil: 'networkidle' });
await page.click('button[aria-label="Quitar fotografía 1"]');
r = await guardar();
await page.goto(base + '/galeria/' + album.id, { waitUntil: 'networkidle' });
const quedan = await page.$$eval('.photo-grid img', (i) => i.length);
await page.goto(base + '/admin/galeria', { waitUntil: 'networkidle' });
await page.locator('tr', { hasText: TITULO }).locator('button[aria-label^="Eliminar"]').click();
await page.click('text=Eliminar contenido');
await page.waitForSelector('.confirm-modal', { state: 'detached', timeout: 10000 });
const finales = (await privado()).albums.map((a) => a.id).join(',');
if (r === 'ok' && quedan === 1 && finales === 'edicion-2026,edicion-2025,edicion-2024') ok('quitar foto (queda 1) y borrar álbum; quedan los 3 históricos');
else fallo(`quitar/borrar: ${r} ${quedan} ${finales}`);
await browser.close();
