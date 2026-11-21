// Feature 012 · US3 y US4 (decisiones P7 y P8): logotipo nuevo en la cabecera y, en negativo, en el
// pie, sin mover el resto. US5 (decisión P9): frase de autoría de la línea inferior del pie.
// Uso (desde frontend/, con Docker Compose en marcha; con PANTALLAS=si se mide también el panel):
//   node scripts/verificar-logo.mjs --referencia capturas/pie-antes-012.json   # antes del cambio
//   node scripts/verificar-logo.mjs --comparar capturas/pie-antes-012.json
import { readFileSync, statSync, writeFileSync } from 'node:fs';
import { fallo, navegador, ok } from './comun.mjs';

const [modo, archivo] = process.argv.slice(2);
if (!['--referencia', '--comparar'].includes(modo) || !archivo) {
  console.error('Uso: verificar-logo.mjs --referencia|--comparar <archivo.json> [url-base]');
  process.exit(2);
}
const base = process.argv[4] ?? 'http://localhost:8080';
// Anchos aprobados y los dos lados de cada cambio de diseño de la cabecera y del pie (359/360, 700/701, 1000/1001, 1200/1201).
const ANCHOS = [320, 340, 359, 360, 390, 414, 700, 701, 768, 1000, 1001, 1024, 1200, 1201, 1440];
const RUTAS = ['/', '/carreras', '/solidaridad', '/noticias', '/clasificaciones', '/contacto'];
const CABECERA = ['logo_cabecera-480.webp', 'logo_cabecera-720.webp'];
const PIE = ['logo_pie-480.webp', 'logo_pie-720.webp'];
const FRASE = 'Hecho por la Escuela Hacker Cosío';

/**
 * Lleva el pie a la vista para que cargue su logotipo (carga diferida) y vuelve arriba. El
 * desplazamiento es instantáneo: con `scroll-behavior: smooth` se mediría a mitad de animación.
 */
async function prepararPagina(page) {
  await page.evaluate(() => document.querySelector('footer')?.scrollIntoView({ behavior: 'instant' }));
  await page.waitForFunction(() => [...document.querySelectorAll('.header img, footer .brand img')].every((i) => i.complete), null, { timeout: 10000 }).catch(() => {});
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.waitForFunction(() => window.scrollY === 0);
}

async function medir() {
  // Coordenadas de documento: no dependen de dónde haya quedado el desplazamiento.
  const rect = (el) => {
    if (!el || getComputedStyle(el).display === 'none') return null;
    const r = el.getBoundingClientRect();
    return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height };
  };
  // Con srcset, naturalWidth/Height vienen en píxeles CSS redondeados: se miden los píxeles reales del archivo descargado.
  const reales = (img) => new Promise((res) => { const x = new Image(); x.onload = () => res([x.naturalWidth, x.naturalHeight]); x.onerror = () => res([0, 0]); x.src = img.currentSrc; });
  const datosImg = async (img) => {
    if (!img) return null;
    const [w, h] = await reales(img);
    return {
      ...rect(img), src: img.currentSrc, completa: img.complete && img.naturalWidth > 0,
      natural: w / h, pixeles: w, ajuste: getComputedStyle(img).objectFit,
      filtro: getComputedStyle(img).filter, alt: img.alt,
    };
  };
  // Huella visible de una marca: unión de sus hijos (silueta y texto antes; logotipo ahora).
  const huella = (a) => {
    const rs = [...a.children].map((e) => e.getBoundingClientRect());
    const l = Math.min(...rs.map((r) => r.left)), t = Math.min(...rs.map((r) => r.top));
    return { x: l + scrollX, y: t + scrollY, w: Math.max(...rs.map((r) => r.right)) - l, h: Math.max(...rs.map((r) => r.bottom)) - t };
  };
  const header = document.querySelector('.header');
  const marca = header.querySelector('.brand');
  const pie = document.querySelector('footer .brand');
  const columnas = [...document.querySelectorAll('.footer-main > div')];
  return {
    header: rect(header),
    nav: rect(header.querySelector('nav')),
    cta: rect(header.querySelector('.nav-cta')),
    menu: rect(header.querySelector('.menu-toggle')),
    marca: rect(marca),
    texto: marca?.innerText.trim() ?? null,
    enlace: { href: marca?.getAttribute('href'), etiqueta: marca?.getAttribute('aria-label') },
    img: await datosImg(marca?.querySelector('img')),
    pie: pie && {
      ...rect(pie), texto: pie.innerText.trim(), huella: huella(pie),
      enlace: { href: pie.getAttribute('href'), etiqueta: pie.getAttribute('aria-label') },
      img: await datosImg(pie.querySelector('img')),
    },
    columnas: columnas.map(rect),
    primera: { p: rect(columnas[0]?.querySelector('p')), instagram: rect(columnas[0]?.querySelector('.instagram')) },
    bajo: rect(document.querySelector('.footer-bottom')),
    // textContent y no innerText: no depende de transformaciones de mayúsculas del CSS.
    credito: (() => {
      const lineas = [...(document.querySelector('.footer-bottom')?.children ?? [])];
      return {
        lineas: lineas.map((s) => s.textContent.trim()),
        enlaces: document.querySelectorAll('.footer-bottom a').length,
        estilos: lineas.map((s) => `${getComputedStyle(s).color} ${getComputedStyle(s).fontSize}`),
        restos: /Hecho con pasión|JR BLANCO|Hackers Cosío/i.test(document.querySelector('footer')?.textContent ?? ''),
      };
    })(),
    desborda: document.documentElement.scrollWidth > innerWidth,
  };
}

/** Color medio del blanco y del naranja del logotipo del pie y su contraste con el fondo del pie. */
async function contraste() {
  const img = document.querySelector('footer .brand img');
  const x = new Image();
  await new Promise((res) => { x.onload = res; x.onerror = res; x.src = img.currentSrc; });
  const c = Object.assign(document.createElement('canvas'), { width: x.naturalWidth, height: x.naturalHeight });
  const g = c.getContext('2d');
  g.drawImage(x, 0, 0);
  const d = g.getImageData(0, 0, c.width, c.height).data;
  const grupos = { naranja: [0, 0, 0, 0], blanco: [0, 0, 0, 0] };
  for (let i = 0; i < d.length; i += 4) {
    if (d[i + 3] < 250) continue;
    const grupo = d[i] > 150 && d[i] - d[i + 2] > 80 ? grupos.naranja : d[i] > 230 && d[i + 1] > 230 && d[i + 2] > 230 ? grupos.blanco : null;
    if (grupo) { grupo[0] += d[i]; grupo[1] += d[i + 1]; grupo[2] += d[i + 2]; grupo[3]++; }
  }
  const lum = ([r, gg, b]) => [r, gg, b].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }).reduce((s, v, k) => s + v * [0.2126, 0.7152, 0.0722][k], 0);
  const fondo = getComputedStyle(document.querySelector('footer')).backgroundColor.match(/\d+/g).slice(0, 3).map(Number);
  const ratio = (a, b) => { const [l1, l2] = [lum(a), lum(b)].sort((p, q) => q - p); return (l1 + 0.05) / (l2 + 0.05); };
  const medio = (s) => (s[3] ? s.slice(0, 3).map((v) => Math.round(v / s[3])) : null);
  const naranja = medio(grupos.naranja), blanco = medio(grupos.blanco);
  return { fondo, naranja, blanco, cNaranja: naranja && ratio(naranja, fondo), cBlanco: blanco && ratio(blanco, fondo), pixeles: [grupos.naranja[3], grupos.blanco[3]] };
}

const browser = await navegador();
const medidas = {};
const page = await (await browser.newContext()).newPage();
for (const ancho of ANCHOS) {
  await page.setViewportSize({ width: ancho, height: 900 });
  for (const ruta of RUTAS) {
    await page.goto(base + ruta, { waitUntil: 'networkidle' });
    await prepararPagina(page);
    medidas[`${ruta}@${ancho}`] = await page.evaluate(medir);
  }
}

// Contraste del logotipo del pie (solo al comparar: antes del cambio el pie no lo tiene).
let colores = null;
if (modo === '--comparar') {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(base + '/', { waitUntil: 'networkidle' });
  await prepararPagina(page);
  colores = await page.evaluate(contraste);
}

// Barra lateral del panel (vista de demostración, solo si /pantallas está disponible en local).
let panel = null;
const r = await page.goto(base + '/pantallas/admin', { waitUntil: 'networkidle' });
if (r?.status() === 200 && (await page.$('.admin-sidebar .brand'))) {
  panel = await page.$eval('.admin-sidebar .brand', (a) => ({ texto: a.innerText, src: a.querySelector('img')?.getAttribute('src') }));
}

// Nitidez: en densidad 2, la variante descargada mide al menos el doble del tamaño en pantalla.
const densidad = {};
for (const ancho of [360, 768, 1440]) {
  const p = await (await browser.newContext({ deviceScaleFactor: 2, viewport: { width: ancho, height: 900 } })).newPage();
  await p.goto(base + '/', { waitUntil: 'networkidle' });
  await prepararPagina(p);
  const m = await p.evaluate(medir);
  densidad[ancho] = Object.fromEntries([['cabecera', m.img], ['pie', m.pie?.img]].map(([k, i]) => [k, i && { natural: i.pixeles, pantalla: i.w, src: i.src }]));
}
await browser.close();

if (modo === '--referencia') {
  writeFileSync(archivo, JSON.stringify({ medidas, panel }, null, 1));
  console.log(`Referencia guardada: ${Object.keys(medidas).length} vistas de la cabecera y del pie; panel: ${panel ? 'medido' : 'no disponible'}.`);
  process.exit(0);
}

const ref = JSON.parse(readFileSync(archivo, 'utf8'));
const igual = (a, b) => (a === null && b === null) || (a && b && ['x', 'y', 'w', 'h'].every((k) => Math.abs(a[k] - b[k]) <= 0.5));
const problemas = [];
/** Comprobaciones comunes a los dos logotipos: cargado, completo, sin deformar y sin filtro. */
function comprobarImg(i, variantes, p, donde) {
  if (!i || !variantes.some((v) => i.src.endsWith('/reused/logos/' + v))) { p(`${donde}: no muestra el logotipo nuevo (${i?.src})`); return false; }
  if (!i.completa) p(`${donde}: el logotipo no ha cargado`);
  if (Math.abs(i.w / i.h - i.natural) / i.natural > 0.01) p(`${donde}: logotipo deformado (${(i.w / i.h).toFixed(3)} frente a ${i.natural.toFixed(3)})`);
  if (i.ajuste === 'cover') p(`${donde}: logotipo recortado (cover)`);
  if (i.filtro !== 'none') p(`${donde}: el logotipo lleva filtro (${i.filtro})`);
  if (!i.alt) p(`${donde}: el logotipo no tiene alt`);
  return true;
}
let maxBajada = 0;
for (const [clave, m] of Object.entries(medidas)) {
  const antes = ref.medidas[clave];
  const p = (t) => problemas.push(`${clave}: ${t}`);
  if (!antes) { p('sin referencia'); continue; }
  // Cabecera (US3): nada se mueve.
  for (const k of ['header', 'nav', 'cta', 'menu']) if (!igual(m[k], antes[k])) p(`${k} se ha movido (${JSON.stringify(antes[k])} → ${JSON.stringify(m[k])})`);
  const i = m.img;
  if (comprobarImg(i, CABECERA, p, 'cabecera')) {
    if (i.w > antes.marca.w + 0.5) p(`cabecera: más ancho que la marca anterior (${i.w.toFixed(1)} > ${antes.marca.w.toFixed(1)})`);
    if (i.y < m.header.y + 4 || i.y + i.h > m.header.y + m.header.h - 4) p('cabecera: el logotipo no cabe con 4 px de margen');
  }
  if (m.texto) p(`queda texto de marca en la cabecera («${m.texto}»)`);
  if (m.enlace.href !== '/' || !m.enlace.etiqueta) p(`cabecera: enlace a la portada incorrecto (${JSON.stringify(m.enlace)})`);
  if (m.desborda) p('desbordamiento horizontal');
  // Línea inferior del pie (US5): aviso de copyright intacto, frase nueva como texto y con el estilo de la línea.
  const c = m.credito;
  if (!/^© \d{4} Asociación Peñasagra$/.test(c.lineas[0] ?? '')) p(`aviso de copyright del pie: «${c.lineas[0]}»`);
  if (c.lineas[1] !== FRASE || c.lineas.length !== 2) p(`frase del pie: ${JSON.stringify(c.lineas)}`);
  if (c.enlaces) p(`la línea inferior del pie tiene ${c.enlaces} enlace(s)`);
  if (c.estilos[0] !== c.estilos[1]) p(`la frase no tiene el color y el tamaño de la línea (${c.estilos.join(' / ')})`);
  if (c.restos) p('quedan restos de la frase anterior en el pie');
  // Pie (US4): logotipo en negativo; las demás columnas no se mueven en horizontal y nada baja más de lo que crece la marca.
  const f = m.pie, fa = antes.pie;
  if (!fa?.huella) { p('la referencia no tiene la huella del pie (tomarla con esta versión del script)'); continue; }
  if (!f) { p('sin marca en el pie'); continue; }
  if (comprobarImg(f.img, PIE, p, 'pie')) {
    if (f.img.w > fa.huella.w + 0.5) p(`pie: más ancho que la marca anterior (${f.img.w.toFixed(1)} > ${fa.huella.w.toFixed(1)})`);
    if (f.img.w > m.columnas[0].w + 0.5) p(`pie: más ancho que su columna (${f.img.w.toFixed(1)} > ${m.columnas[0].w.toFixed(1)})`);
  }
  if (f.texto) p(`queda texto de marca en el pie («${f.texto}»)`);
  if (f.enlace.href !== '/' || !f.enlace.etiqueta) p(`pie: enlace a la portada incorrecto (${JSON.stringify(f.enlace)})`);
  const crece = Math.max(0, f.h - fa.h);
  const baja = (a, b, que) => {
    if (!a || !b) { if (a || b) p(`${que}: aparece o desaparece`); return; }
    if (Math.abs(a.x - b.x) > 0.5 || Math.abs(a.w - b.w) > 0.5) p(`${que}: cambia en horizontal (${JSON.stringify(b)} → ${JSON.stringify(a)})`);
    const dy = a.y - b.y;
    maxBajada = Math.max(maxBajada, dy);
    if (dy < -0.5 || dy > crece + 0.5) p(`${que}: baja ${dy.toFixed(1)} px y la marca crece ${crece.toFixed(1)} px`);
  };
  if (m.columnas.length !== antes.columnas.length) p('cambia el número de columnas del pie');
  m.columnas.slice(1).forEach((c, k) => baja(c, antes.columnas[k + 1], `columna ${k + 2} del pie`));
  baja(m.primera.p, antes.primera.p, 'párrafo del pie');
  baja(m.primera.instagram, antes.primera.instagram, 'enlace a Instagram');
  baja(m.bajo, antes.bajo, 'franja inferior del pie');
}
const total = Object.keys(medidas).length;
if (!problemas.length) ok(`${total} vistas (${RUTAS.length} rutas × ${ANCHOS.length} anchos): logotipos completos y sin deformar, sin texto de marca, cabecera/navegación/INSCRIPCIONES/menú con 0 px de diferencia; pie con el logotipo en negativo, no más ancho que la marca anterior ni que su columna, columnas 2.ª–4.ª en su sitio y bajada máxima de ${maxBajada.toFixed(1)} px (≤ lo que crece la marca); línea inferior con «© año Asociación Peñasagra» y «${FRASE}», sin enlaces, con el mismo estilo y sin restos de la frase anterior; sin desbordamientos`);
else fallo(`${problemas.length} problemas:\n  ${problemas.slice(0, 25).join('\n  ')}`);

const tamanos = [...CABECERA, ...PIE].map((v) => [v, statSync(new URL(`../public/reused/logos/${v}`, import.meta.url)).size]);
if (tamanos.every(([, t]) => t <= 50 * 1024)) ok(`variantes: ${tamanos.map(([v, t]) => `${v} ${(t / 1024).toFixed(1)} KB`).join(', ')} (máximo 50 KB)`);
else fallo(`variantes demasiado pesadas: ${JSON.stringify(tamanos)}`);

const lineas = Object.entries(densidad).flatMap(([a, d]) => Object.entries(d).map(([k, v]) => [a, k, v]));
if (lineas.every(([, , v]) => v && v.natural >= 2 * v.pantalla)) ok(`densidad 2: ${lineas.map(([a, k, v]) => `${k} ${a} px → ${v.src.split('/').pop()} (${v.natural} ≥ 2×${v.pantalla.toFixed(0)})`).join('; ')}`);
else fallo(`densidad 2 sin resolución suficiente: ${JSON.stringify(densidad)}`);

if (colores?.cNaranja >= 3 && colores?.cBlanco >= 4.5) ok(`contraste sobre el pie rgb(${colores.fondo}): naranja rgb(${colores.naranja}) ${colores.cNaranja.toFixed(2)}:1 (≥ 3) y blanco rgb(${colores.blanco}) ${colores.cBlanco.toFixed(2)}:1 (≥ 4,5); ${colores.pixeles.join(' y ')} píxeles`);
else fallo(`contraste insuficiente o no medible: ${JSON.stringify(colores)}`);

if (ref.panel && JSON.stringify(panel) !== JSON.stringify(ref.panel)) fallo(`la barra lateral del panel ha cambiado: ${JSON.stringify(panel)}`);
else if (ref.panel) ok('barra lateral del panel sin cambios');
else console.log('AVISO /pantallas no disponible: barra lateral del panel no comprobada');
