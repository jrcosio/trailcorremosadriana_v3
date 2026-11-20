// Feature 012 · Decisión P6: las fotos se ven siempre completas, en el mismo marco que antes.
// Uso (desde frontend/, con Docker Compose en marcha; el panel y el álbum temporal con credenciales):
//   [ADMIN_USUARIO=… ADMIN_PASSWORD=…] node scripts/verificar-fotos.mjs --referencia capturas/marcos-antes-012.json
//   [ADMIN_USUARIO=… ADMIN_PASSWORD=…] node scripts/verificar-fotos.mjs --comparar capturas/marcos-antes-012.json
import { readFileSync, writeFileSync } from 'node:fs';
import { fallo, navegador, ok } from './comun.mjs';

const [modo, archivo] = process.argv.slice(2);
if (!['--referencia', '--comparar'].includes(modo) || !archivo) {
  console.error('Uso: verificar-fotos.mjs --referencia|--comparar <archivo.json> [url-base]');
  process.exit(2);
}
const base = process.argv[4] ?? 'http://localhost:8080';
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
const FOTOS = ['.race-card>img', '.cause-photo>img', '.news-image img', '.race-detail-hero>img', '.article-image',
  '.album-card>img', '.album-archive>img', '.photo-grid img', '.admin-row-name img', '.admin-photo-grid img'];
const ANCHOS = [320, 360, 768, 1024, 1440];
const ALBUM = 'verificacion-fotos-012';
const PUBLICAS = ['/', '/carreras', '/carreras/trail-27k', '/recorridos/speed-14k', '/solidaridad', '/noticias',
  '/noticias/gracias-trail-2026', '/noticias/proxima-edicion', '/galeria', '/galeria/edicion-2026', `/galeria/${ALBUM}`];
const PANEL = ['/admin/noticias', '/admin/recorridos', '/admin/galeria', `/admin/galeria/${ALBUM}`];

/** Mide cada foto: marco, rectángulo pintado (según object-fit/position) y área visible de sus ancestros. */
function medir(selectores) {
  const res = [];
  for (const sel of selectores) {
    document.querySelectorAll(sel).forEach((img, i) => {
      const b = img.getBoundingClientRect();
      const cs = getComputedStyle(img);
      const marco = { x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height };
      let pintada = { ...marco };
      const nr = img.naturalWidth / img.naturalHeight;
      if (img.naturalWidth && cs.objectFit === 'contain') {
        const w = Math.min(b.width, b.height * nr);
        const h = w / nr;
        const [px, py] = cs.objectPosition.split(' ').map((v) => (v.endsWith('%') ? parseFloat(v) / 100 : 0.5));
        pintada = { x: marco.x + (b.width - w) * px, y: marco.y + (b.height - h) * py, w, h };
      } else if (img.naturalWidth && cs.objectFit === 'cover') {
        const w = Math.max(b.width, b.height * nr);
        const h = w / nr;
        pintada = { x: marco.x - (w - b.width) / 2, y: marco.y - (h - b.height) / 2, w, h };
      }
      // Área visible: intersección del marco del img y de los ancestros que recortan.
      let vis = { l: marco.x, t: marco.y, r: marco.x + marco.w, b: marco.y + marco.h };
      for (let el = img.parentElement; el && el !== document.body; el = el.parentElement) {
        const c = getComputedStyle(el);
        if (c.overflowX !== 'visible' || c.overflowY !== 'visible') {
          const a = el.getBoundingClientRect();
          vis = { l: Math.max(vis.l, a.left + scrollX), t: Math.max(vis.t, a.top + scrollY), r: Math.min(vis.r, a.right + scrollX), b: Math.min(vis.b, a.bottom + scrollY) };
        }
      }
      const tol = 1;
      const completa = img.naturalWidth > 0 && pintada.x >= vis.l - tol && pintada.y >= vis.t - tol
        && pintada.x + pintada.w <= vis.r + tol && pintada.y + pintada.h <= vis.b + tol;
      const difiere = Math.abs(nr - b.width / b.height) / (b.width / b.height) > 0.02;
      res.push({ id: `${sel}#${i}`, marco, ajuste: cs.objectFit, completa, difiere, relleno: cs.backgroundImage.includes('url('), perdida: Math.round((1 - (Math.min(pintada.w, vis.r - vis.l) * Math.min(pintada.h, vis.b - vis.t)) / (pintada.w * pintada.h)) * 100) });
    });
  }
  return res;
}

const browser = await navegador();
const contexto = await browser.newContext();
const page = await contexto.newPage();
const csrf = async () => (await contexto.cookies()).find((c) => c.name === 'penasagra_csrf')?.value;
let conPanel = false;
if (usuario && password) {
  await page.goto(base + '/admin', { waitUntil: 'networkidle' });
  await page.fill('input[name="username"]', usuario);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForSelector('.admin-event h2');
  // Álbum temporal (borrador) con fotos vertical y horizontal para la cuadrícula y sus miniaturas.
  const r = await page.request.put(`${base}/api/admin/albumes/${ALBUM}`, {
    headers: { 'X-CSRF-Token': await csrf(), Origin: base },
    data: { title: 'Verificación de fotos 012', year: '2027', image: '/reused/img/dorsal_solidario.webp', url: '',
      photos: ['/reused/img/dorsal_solidario.webp', '/reused/noticias/gracias_2026.webp', '/reused/fondos/fondo.webp'], published: true, version: 0 },
  });
  conPanel = r.ok();
  if (!conPanel) fallo(`no se pudo crear el álbum temporal: ${r.status()} ${await r.text()}`);
}

const medidas = {};
for (const ancho of ANCHOS) {
  await page.setViewportSize({ width: ancho, height: 900 });
  for (const ruta of [...PUBLICAS, ...(conPanel ? PANEL : [])]) {
    if (!conPanel && ruta.includes(ALBUM)) continue;
    await page.goto(base + ruta, { waitUntil: 'networkidle' });
    await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 40)); } scrollTo(0, 0); });
    await page.waitForFunction(() => [...document.images].every((i) => i.complete), null, { timeout: 15000 }).catch(() => {});
    medidas[`${ruta}@${ancho}`] = await page.evaluate(medir, FOTOS);
  }
}

// FR-005: logotipos, visor y vista previa de subida no cambian; foto que no carga → color de base.
await page.setViewportSize({ width: 1440, height: 900 });
await page.goto(base + '/patrocinadores', { waitUntil: 'networkidle' });
const otros = { logos: await page.$$eval('.logo-grid img', (l) => [...new Set(l.map((i) => `${getComputedStyle(i).objectFit}|${getComputedStyle(i).backgroundImage}`))]) };
if (conPanel) {
  await page.goto(`${base}/galeria/${ALBUM}`, { waitUntil: 'networkidle' });
  await page.click('.photo-grid button');
  await page.waitForSelector('.lightbox img');
  otros.visor = await page.$eval('.lightbox img', (i) => `${getComputedStyle(i).objectFit}|${getComputedStyle(i).backgroundImage}`);
  await page.goto(`${base}/admin/noticias/nuevo`, { waitUntil: 'networkidle' });
  otros.vistaPrevia = await page.evaluate(() => { const i = document.createElement('img'); i.className = 'upload-preview'; document.body.append(i); const c = getComputedStyle(i); return `${c.objectFit}|${c.backgroundColor}|${c.backgroundImage}`; });
}
await page.goto(base + '/noticias', { waitUntil: 'networkidle' });
otros.sinCarga = await page.evaluate(() => { const img = document.querySelector('.news-image img').cloneNode(); img.removeAttribute('style'); img.src = '/reused/no-existe.webp'; document.querySelector('.news-image').append(img); return getComputedStyle(img).backgroundColor; });

if (conPanel) {
  const v = (await (await page.request.get(base + '/api/content?admin=1')).json()).data.albums.find((a) => a.id === ALBUM)?.version;
  const r = await page.request.delete(`${base}/api/admin/albumes/${ALBUM}?version=${v}`, { headers: { 'X-CSRF-Token': await csrf(), Origin: base } });
  if (!r.ok()) fallo(`no se pudo borrar el álbum temporal (${r.status()})`);
}
await browser.close();

const total = Object.values(medidas).reduce((n, l) => n + l.length, 0);
if (modo === '--referencia') {
  writeFileSync(archivo, JSON.stringify({ medidas, otros }, null, 1));
  const recortadas = Object.entries(medidas).flatMap(([k, l]) => l.filter((f) => !f.completa).map((f) => `${k} ${f.id} −${f.perdida}%`));
  console.log(`Referencia guardada: ${total} fotos medidas; ${recortadas.length} recortadas antes del cambio.`);
  console.log(recortadas.slice(0, 12).join('\n'));
  process.exit(0);
}

const ref = JSON.parse(readFileSync(archivo, 'utf8'));
const problemas = [];
for (const [clave, lista] of Object.entries(medidas)) {
  for (const f of lista) {
    if (f.ajuste !== 'contain' || !f.completa) problemas.push(`${clave} ${f.id}: recortada (${f.ajuste}, −${f.perdida}%)`);
    if (f.difiere && !f.relleno) problemas.push(`${clave} ${f.id}: sin relleno`);
    const antes = ref.medidas[clave]?.find((x) => x.id === f.id);
    if (antes && ['x', 'y', 'w', 'h'].some((k) => Math.abs(antes.marco[k] - f.marco[k]) > 0.5)) problemas.push(`${clave} ${f.id}: el marco ha cambiado`);
  }
}
if (!problemas.length) ok(`${total} fotos completas a ${ANCHOS.join('/')} px${conPanel ? ' (con el panel y un álbum temporal)' : ''}; marcos idénticos a la referencia; relleno donde las proporciones difieren`);
else fallo(`${problemas.length} problemas:\n  ${problemas.slice(0, 15).join('\n  ')}`);
// El visor y la vista previa solo se miden con el panel (credenciales).
const igualesOtros = JSON.stringify(otros.logos) === JSON.stringify(ref.otros.logos) && (!conPanel || (otros.visor === ref.otros.visor && otros.vistaPrevia === ref.otros.vistaPrevia));
if (igualesOtros && otros.sinCarga === 'rgb(23, 46, 40)') ok(`logotipos${conPanel ? ', visor y vista previa' : ''} sin cambios; una foto que no carga deja el marco en #172e28`);
else fallo(`otros: ${JSON.stringify(otros)} (antes ${JSON.stringify(ref.otros)})`);
