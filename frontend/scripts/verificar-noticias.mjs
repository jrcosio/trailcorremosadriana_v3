// Feature 007 · Noticias: existentes, borrador → publicada (con imagen) → retirada → borrada,
// HTML como texto y conflicto. Restaura los datos al terminar.
// Uso: ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-noticias.mjs [url-base]
import { fileURLToPath } from 'node:url';
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!usuario || !password) { console.error('Define ADMIN_USUARIO y ADMIN_PASSWORD'); process.exit(2); }
const foto = fileURLToPath(new URL('../public/reused/img/dorsal_solidario.webp', import.meta.url));
const browser = await navegador();
const contexto = await browser.newContext();
const page = await contexto.newPage();
const texto = () => page.evaluate(() => document.body.innerText);
const TITULO = 'Noticia de verificación 007';

// 1. Noticias existentes.
await page.goto(base + '/noticias', { waitUntil: 'networkidle' });
let t = await texto();
if (t.includes('Peñasagra 2027 ya está en el horizonte') && t.includes('¡Gracias por un Trail 2026 inolvidable!')) ok('/noticias: las 2 noticias existentes');
else fallo('/noticias sin las noticias existentes');
await page.goto(base + '/noticias/gracias-trail-2026', { waitUntil: 'networkidle' });
const parrafos = await page.$$eval('.prose p', (ps) => ps.length);
const imagen = await page.getAttribute('.article-image', 'src');
if (parrafos === 4 && imagen === '/reused/noticias/gracias_2026.webp') ok('detalle de la noticia de producción: 4 párrafos e imagen original');
else fallo(`detalle: ${parrafos} párrafos, imagen ${imagen}`);
await page.goto(base + '/', { waitUntil: 'networkidle' });
if ((await texto()).includes('¡Gracias por un Trail 2026 inolvidable!')) ok('portada: muestra las noticias'); else fallo('portada sin noticias');

// 2. Panel: nueva → borrador.
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
await page.goto(base + '/admin/noticias/nuevo', { waitUntil: 'networkidle' });
await page.fill('input[name="title"]', TITULO);
await page.fill('input[name="category"]', 'Verificación');
await page.fill('textarea[name="excerpt"]', 'Resumen de prueba.');
await page.fill('textarea[name="body"]', 'Primer párrafo.\n\nSegundo <b>párrafo</b> con <script>alert(1)</script>.');
await page.locator('.upload-field input[type="file"]').first().setInputFiles(foto);
await page.waitForSelector('img.upload-preview');
let r = await guardar();
const nueva = (await privado()).news.find((n) => n.title === TITULO);
await page.goto(base + '/noticias', { waitUntil: 'networkidle' });
const oculta = !(await texto()).includes(TITULO);
await page.goto(base + '/noticias/' + nueva?.id, { waitUntil: 'networkidle' });
if (r === 'ok' && nueva && !nueva.published && oculta && (await texto()).includes('Este sendero no está en el mapa.')) ok('nueva noticia: borrador oculto y detalle no encontrado');
else fallo(`borrador: ${r} ${JSON.stringify(nueva)}`);

// 3. Publicar: visible, imagen subida y HTML como texto.
await page.goto(base + '/admin/noticias/' + nueva.id, { waitUntil: 'networkidle' });
await page.locator('.publish-card input[role="switch"]').check();
r = await guardar();
await page.goto(base + '/noticias/' + nueva.id, { waitUntil: 'networkidle' });
const prosa = await page.$$eval('.prose p', (ps) => ps.map((p) => ({ texto: p.textContent, html: p.innerHTML })));
const img = await page.getAttribute('.article-image', 'src');
const dialogos = [];
page.on('dialog', (d) => { dialogos.push(d.message()); d.dismiss(); });
if (r === 'ok' && prosa.length === 2 && prosa[1].texto.includes('<script>alert(1)</script>') && !prosa[1].html.includes('<b>') && /^\/media\/[0-9a-f]{32}\.webp$/.test(img ?? '') && dialogos.length === 0) {
  ok('publicada: 2 párrafos, HTML mostrado como texto, imagen subida desde /media');
} else fallo(`publicar: ${r} ${JSON.stringify(prosa)} ${img}`);

// 4. Conflicto: otra pestaña con versión anterior.
const otra = await contexto.newPage();
await otra.goto(base + '/admin/noticias/' + nueva.id, { waitUntil: 'networkidle' });
await page.goto(base + '/admin/noticias/' + nueva.id, { waitUntil: 'networkidle' });
await page.fill('input[name="category"]', 'Primera');
await guardar();
await otra.fill('input[name="category"]', 'Segunda');
await otra.click('button[type="submit"]');
await otra.waitForSelector('.admin-error[role="alert"]', { timeout: 15000 });
const conflicto = (await otra.textContent('.admin-error[role="alert"]'))?.trim();
if (conflicto?.startsWith('Otra persona ha modificado')) ok('conflicto 409 avisado sin sobrescribir'); else fallo(`conflicto: ${conflicto}`);
await otra.close();

// 5. Retirar y borrar.
await page.goto(base + '/admin/noticias/' + nueva.id, { waitUntil: 'networkidle' });
await page.locator('.publish-card input[role="switch"]').uncheck();
await guardar();
await page.goto(base + '/noticias', { waitUntil: 'networkidle' });
const retirada = !(await texto()).includes(TITULO);
await page.goto(base + '/admin/noticias', { waitUntil: 'networkidle' });
await page.locator('tr', { hasText: TITULO }).locator('button[aria-label^="Eliminar"]').click();
await page.click('text=Eliminar contenido');
await page.waitForSelector('.confirm-modal', { state: 'detached', timeout: 10000 });
const final = (await privado()).news.map((n) => n.id).join(',');
if (retirada && final === 'proxima-edicion,gracias-trail-2026') ok('retirada y borrada; quedan solo las 2 noticias existentes');
else fallo(`retirar/borrar: ${retirada} ${final}`);
// 6. Noticia sin imagen (casos límite): paisaje de reserva en la lista y en el detalle.
const csrf = (await contexto.cookies()).find((c) => c.name === 'penasagra_csrf')?.value ?? '';
const crear = await page.request.put(base + '/api/admin/noticias/verificacion-sin-imagen', {
  headers: { 'X-CSRF-Token': csrf, Origin: base },
  data: { title: 'Sin imagen 007', body: 'Texto.', image: '', published: true, version: 0 },
});
await page.goto(base + '/noticias', { waitUntil: 'networkidle' });
const enLista = await page.getAttribute('a.news-card[href="/noticias/verificacion-sin-imagen"] img', 'src');
await page.goto(base + '/noticias/verificacion-sin-imagen', { waitUntil: 'networkidle' });
const enDetalle = await page.getAttribute('.article-image', 'src');
const borrar = await page.request.delete(base + '/api/admin/noticias/verificacion-sin-imagen?version=1', { headers: { 'X-CSRF-Token': csrf, Origin: base } });
if (crear.ok() && enLista === '/reused/fondos/fondo.webp' && enDetalle === '/reused/fondos/fondo.webp' && borrar.ok()) ok('sin imagen: paisaje de reserva en la lista y en el detalle (restaurado)');
else fallo(`sin imagen: ${crear.status()} ${enLista} ${enDetalle} ${borrar.status()}`);

await browser.close();
