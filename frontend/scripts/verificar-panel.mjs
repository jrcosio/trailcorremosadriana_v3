// Feature 012 · US7: la barra lateral del panel se desplaza en pantallas bajas. US8 (decisión P11):
// logotipo oficial en la barra lateral y en la pantalla de acceso, sin mover el resto.
// Uso (desde frontend/, con Docker Compose en marcha):
//   ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-panel.mjs --referencia capturas/panel-antes-012.json   # antes del cambio
//   ADMIN_USUARIO=… ADMIN_PASSWORD=… node scripts/verificar-panel.mjs --comparar capturas/panel-antes-012.json
import { readFileSync, writeFileSync } from 'node:fs';
import AxeBuilder from '@axe-core/playwright';
import { fallo, navegador, ok } from './comun.mjs';

const [modo, archivo] = process.argv.slice(2);
const { ADMIN_USUARIO: usuario, ADMIN_PASSWORD: password } = process.env;
if (!['--referencia', '--comparar'].includes(modo) || !archivo || !usuario || !password) {
  console.error('Uso: ADMIN_USUARIO=… ADMIN_PASSWORD=… verificar-panel.mjs --referencia|--comparar <archivo.json> [url-base]');
  process.exit(2);
}
const base = process.argv[4] ?? 'http://localhost:8080';
// Ventanas de escritorio y de móvil (≤ 700 px: menú desplegable), altas y bajas, en cada tramo de la barra lateral.
const VISTAS = [[1440, 900], [1440, 640], [1200, 560], [1024, 500], [701, 480], [700, 640], [360, 640], [360, 480]];
const ACCESO = [1440, 1200, 1024, 900, 768, 701, 360];
const PIE = ['logo_pie-480.webp', 'logo_pie-720.webp'];

// --- Funciones que se ejecutan en el navegador ---
const rect = (e) => { if (!e || getComputedStyle(e).display === 'none') return null; const r = e.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; };
async function datosImg(img) {
  if (!img) return null;
  const [w, h] = await new Promise((res) => { const x = new Image(); x.onload = () => res([x.naturalWidth, x.naturalHeight]); x.onerror = () => res([0, 0]); x.src = img.currentSrc; });
  const r = img.getBoundingClientRect();
  return { x: r.left, y: r.top, w: r.width, h: r.height, src: img.currentSrc, completa: img.complete && img.naturalWidth > 0, natural: w / h, pixeles: w, alt: img.alt };
}
/** Unión de los hijos de una marca: silueta y texto antes; logotipo (y rótulo) ahora. */
const huella = (a) => {
  const rs = [...a.children].map((e) => e.getBoundingClientRect());
  const l = Math.min(...rs.map((r) => r.left)), t = Math.min(...rs.map((r) => r.top));
  return { x: l, y: t, w: Math.max(...rs.map((r) => r.right)) - l, h: Math.max(...rs.map((r) => r.bottom)) - t };
};

async function medirAcceso() {
  const foto = document.querySelector('.login-photo');
  const marca = foto?.querySelector('.brand');
  return {
    formulario: rect(document.querySelector('.login-content')),
    marca: marca && getComputedStyle(foto).display !== 'none' ? {
      ...rect(marca), huella: huella(marca), href: marca.getAttribute('href'),
      texto: marca.innerText.replace(/\s+/g, ' ').trim(), img: await datosImg(marca.querySelector('img')),
    } : null,
    resto: marca && getComputedStyle(foto).display !== 'none' ? ['h1', 'p', ':scope > span'].map((s) => rect(foto.querySelector(s))) : null,
    desborda: document.documentElement.scrollWidth > innerWidth,
  };
}

async function medirLateral() {
  const s = document.querySelector('.admin-sidebar');
  s.scrollTop = 0;
  const marca = s.querySelector('.brand');
  const rotulo = marca.querySelector('small');
  const cs = rotulo && getComputedStyle(rotulo);
  return {
    lateral: rect(s), cuerpo: rect(document.querySelector('.admin-body')),
    marca: {
      ...rect(marca), huella: huella(marca), href: marca.getAttribute('href'),
      texto: marca.innerText.replace(/\s+/g, ' ').trim(), img: await datosImg(marca.querySelector('img')),
      rotulo: rotulo && { texto: rotulo.textContent.trim(), fuente: cs.fontSize, espaciado: cs.letterSpacing, color: cs.color, peso: cs.fontWeight, familia: cs.fontFamily },
    },
    enlaces: [...s.querySelectorAll('nav a')].map((a) => ({ texto: a.textContent.trim(), ...rect(a) })),
    abajo: rect(s.querySelector('.sidebar-bottom')),
    alto: { cliente: s.clientHeight, contenido: s.scrollHeight }, anchoContenido: s.scrollWidth - s.clientWidth,
    desplazable: ['auto', 'scroll'].includes(getComputedStyle(s).overflowY),
    desborda: document.documentElement.scrollWidth > innerWidth,
  };
}

/** Cada opción y «Cerrar sesión», al recibir el foco (teclado), quedan a la vista y se pueden pulsar. */
function alcanzables() {
  const s = document.querySelector('.admin-sidebar');
  const destinos = [...s.querySelectorAll('nav a'), s.querySelector('.sidebar-bottom button')];
  return destinos.map((el) => {
    s.scrollTop = 0;
    el.focus();
    const r = el.getBoundingClientRect(), l = s.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const tocado = document.elementFromPoint(cx, cy);
    const ok = r.top >= Math.max(0, l.top) - 0.5 && r.bottom <= Math.min(innerHeight, l.bottom) + 0.5 && Boolean(tocado && el.contains(tocado));
    el.blur();
    return { nombre: el.textContent.trim() || el.getAttribute('aria-label'), ok };
  });
}

// --- Recorrido ---
const browser = await navegador();
const contexto = await browser.newContext();
const page = await contexto.newPage();
/** Ejecuta en la página una de las funciones de medida con sus utilidades. */
const enPagina = (fn) => page.evaluate(`(() => { const rect = ${rect.toString()}; const huella = ${huella.toString()}; const datosImg = ${datosImg.toString()}; return (${fn.toString()})(); })()`);

const acceso = {};
await page.goto(base + '/admin', { waitUntil: 'networkidle' });
for (const ancho of ACCESO) {
  await page.setViewportSize({ width: ancho, height: 900 });
  await page.waitForFunction(() => [...document.querySelectorAll('.login-photo img')].every((i) => i.complete));
  acceso[ancho] = await enPagina(medirAcceso);
}

await page.setViewportSize({ width: 1440, height: 900 });
await page.fill('input[name="username"]', usuario);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
await page.waitForSelector('.admin-sidebar nav a');
async function abrir(ruta, ancho, alto) {
  await page.setViewportSize({ width: ancho, height: alto });
  await page.goto(base + ruta, { waitUntil: 'networkidle' });
  await page.waitForSelector('.admin-sidebar nav a');
  await page.waitForFunction(() => [...document.querySelectorAll('.admin-sidebar img')].every((i) => i.complete));
  if (ancho <= 700) {
    await page.click('.mobile-admin-menu');
    await page.waitForFunction(() => Math.abs(document.querySelector('.admin-sidebar').getBoundingClientRect().left) < 0.5);
  }
}

const lateral = {};
const ajustes = {};
for (const [ancho, alto] of VISTAS) {
  const clave = `${ancho}x${alto}`;
  await abrir('/admin', ancho, alto);
  const m = await enPagina(medirLateral);
  m.alcanzables = await page.evaluate(alcanzables);
  // Ratón: rueda sobre la barra lateral hasta el final; «Cerrar sesión» queda a la vista y la página de detrás no se mueve.
  const l = m.lateral;
  await page.mouse.move(l.x + l.w / 2, Math.min(alto, l.y + l.h) / 2);
  for (let i = 0; i < 6; i++) await page.mouse.wheel(0, 400);
  await page.waitForTimeout(250);
  m.rueda = await page.evaluate(() => {
    const b = document.querySelector('.admin-sidebar .sidebar-bottom button').getBoundingClientRect();
    return { boton: b.bottom <= innerHeight + 0.5 && b.top >= 0, pagina: scrollY };
  });
  lateral[clave] = m;
  // La opción de la sección abierta (la última, «Ajustes») se ve al cargar.
  await abrir('/admin/ajustes', ancho, alto);
  ajustes[clave] = await page.evaluate(() => {
    const s = document.querySelector('.admin-sidebar'), a = s.querySelector('nav a.selected');
    const r = a?.getBoundingClientRect(), l = s.getBoundingClientRect();
    return Boolean(r) && r.top >= Math.max(0, l.top) - 0.5 && r.bottom <= Math.min(innerHeight, l.bottom) + 0.5;
  });
}

// AA en la barra lateral con la sesión iniciada: escritorio bajo y menú de móvil abierto. La pantalla de acceso ya la revisa verificar-accesibilidad.mjs.
const axe = {};
if (modo === '--comparar') {
  for (const [ancho, alto] of [[1440, 560], [360, 640]]) {
    await abrir('/admin', ancho, alto);
    axe[`${ancho}x${alto}`] = (await new AxeBuilder({ page }).include('.admin-sidebar').withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze()).violations.map((v) => `${v.id} (${v.nodes.length})`);
  }
}

// Nitidez en densidad 2 (barra lateral y acceso a 1440 px).
const densidad = {};
if (modo === '--comparar') {
  const c2 = await browser.newContext({ deviceScaleFactor: 2, viewport: { width: 1440, height: 900 } });
  const p2 = await c2.newPage();
  const leer = (sel) => p2.evaluate(`(() => { const datosImg = ${datosImg.toString()}; return datosImg(document.querySelector(${JSON.stringify(sel)})); })()`);
  await p2.goto(base + '/admin', { waitUntil: 'networkidle' });
  densidad.acceso = await leer('.login-photo .brand img');
  await p2.fill('input[name="username"]', usuario);
  await p2.fill('input[name="password"]', password);
  await p2.click('button[type="submit"]');
  await p2.waitForSelector('.admin-sidebar nav a');
  densidad.lateral = await leer('.admin-sidebar .brand img');
}
await browser.close();

if (modo === '--referencia') {
  writeFileSync(archivo, JSON.stringify({ acceso, lateral, ajustes }, null, 1));
  console.log(`Referencia guardada: acceso a ${ACCESO.length} anchos y barra lateral en ${VISTAS.length} ventanas.`);
  process.exit(0);
}

// --- Comparación ---
const ref = JSON.parse(readFileSync(archivo, 'utf8'));
const cerca = (a, b) => Math.abs(a - b) <= 0.5;
const problemas = [];
let maxBajada = 0;
function comprobarLogotipo(i, p, donde, maxAncho) {
  if (!i || !PIE.some((v) => i.src.endsWith('/reused/logos/' + v))) { p(`${donde}: no muestra el logotipo oficial (${i?.src})`); return; }
  if (!i.completa) p(`${donde}: el logotipo no ha cargado`);
  if (Math.abs(i.w / i.h - i.natural) / i.natural > 0.01) p(`${donde}: logotipo deformado`);
  if (!i.alt) p(`${donde}: el logotipo no tiene alt`);
  if (i.w > maxAncho + 0.5) p(`${donde}: más ancho que la marca anterior (${i.w.toFixed(1)} > ${maxAncho.toFixed(1)})`);
}
function baja(a, b, crece, p, que) {
  if (!a || !b) { if (a || b) p(`${que}: aparece o desaparece`); return; }
  if (!cerca(a.x, b.x) || !cerca(a.w, b.w)) p(`${que}: cambia en horizontal (${JSON.stringify(b)} → ${JSON.stringify(a)})`);
  const dy = a.y - b.y;
  maxBajada = Math.max(maxBajada, dy);
  if (dy < -0.5 || dy > crece + 0.5) p(`${que}: baja ${dy.toFixed(1)} px y el logotipo crece ${crece.toFixed(1)} px`);
}

// Pantalla de acceso (US8).
for (const ancho of ACCESO) {
  const m = acceso[ancho], a = ref.acceso[ancho];
  const p = (t) => problemas.push(`acceso ${ancho} px: ${t}`);
  if (m.desborda) p('desbordamiento horizontal');
  if (JSON.stringify(m.formulario) !== JSON.stringify(a.formulario)) p(`el formulario cambia (${JSON.stringify(a.formulario)} → ${JSON.stringify(m.formulario)})`);
  if (!a.marca) { if (m.marca) p('aparece la foto donde antes no estaba'); continue; }
  if (!m.marca) { p('sin marca'); continue; }
  comprobarLogotipo(m.marca.img, p, 'logotipo', a.marca.huella.w);
  if (m.marca.texto) p(`queda texto de marca («${m.marca.texto}»)`);
  if (m.marca.href !== '/') p(`el logotipo no lleva a la portada (${m.marca.href})`);
  const crece = Math.max(0, m.marca.h - a.marca.h);
  m.resto.forEach((r, k) => baja(r, a.resto[k], crece, p, ['título', 'párrafo', 'pie de la foto'][k]));
}

// Barra lateral (US7 y US8).
let conDesplazamiento = 0, sinDesplazamiento = 0;
for (const [ancho, alto] of VISTAS) {
  const clave = `${ancho}x${alto}`, m = lateral[clave], a = ref.lateral[clave];
  const p = (t) => problemas.push(`panel ${clave}: ${t}`);
  if (m.desborda) p('desbordamiento horizontal de la página');
  if (m.anchoContenido > 0) p(`desplazamiento horizontal en la barra lateral (${m.anchoContenido} px)`);
  // US7
  if (m.alto.contenido > m.alto.cliente + 0.5) {
    conDesplazamiento++;
    if (!m.desplazable) p('la barra lateral no se desplaza');
    const fuera = m.alcanzables.filter((x) => !x.ok).map((x) => x.nombre);
    if (fuera.length) p(`no se alcanzan con el teclado: ${fuera.join(', ')}`);
    if (!m.rueda.boton) p('con la rueda no se llega a «Cerrar sesión»');
    // Al llegar al final, la rueda no arrastra la página de detrás. Si la barra cabe entera, la rueda mueve la página como antes.
    if (m.rueda.pagina !== 0) p(`la rueda sobre la barra lateral mueve la página de detrás (${m.rueda.pagina} px)`);
  } else {
    sinDesplazamiento++;
    if (!cerca(m.abajo.y + m.abajo.h, alto)) p(`el usuario no queda abajo del todo (${(m.abajo.y + m.abajo.h).toFixed(1)} de ${alto})`);
  }
  if (!ajustes[clave]) p('al abrir «Ajustes», su opción no se ve en la barra lateral');
  // US8
  if (!cerca(m.lateral.x, a.lateral.x) || !cerca(m.lateral.w, a.lateral.w)) p(`la barra lateral cambia de ancho o de sitio (${JSON.stringify(a.lateral)} → ${JSON.stringify(m.lateral)})`);
  if (JSON.stringify(m.cuerpo) !== JSON.stringify(a.cuerpo)) p(`el contenido del panel cambia (${JSON.stringify(a.cuerpo)} → ${JSON.stringify(m.cuerpo)})`);
  comprobarLogotipo(m.marca.img, p, 'logotipo', a.marca.huella.w);
  if (m.marca.img && m.marca.img.x + m.marca.img.w > m.lateral.x + m.lateral.w + 0.5) p('el logotipo se sale de la barra lateral');
  if (m.marca.texto !== 'ADMINISTRACIÓN') p(`texto de la marca: «${m.marca.texto}»`);
  const ra = { ...a.marca.rotulo }, rm = { ...m.marca.rotulo };
  if (JSON.stringify(rm) !== JSON.stringify(ra)) p(`el rótulo cambia de estilo (${JSON.stringify(ra)} → ${JSON.stringify(rm)})`);
  if (m.marca.href !== '/admin') p(`el logotipo no lleva al panel (${m.marca.href})`);
  if (m.enlaces.length !== a.enlaces.length) { p('cambia el número de opciones'); continue; }
  const crece = Math.max(0, m.marca.h - a.marca.h);
  m.enlaces.forEach((e, k) => { if (e.texto !== a.enlaces[k].texto) p(`opción ${k + 1}: «${e.texto}»`); baja(e, a.enlaces[k], crece, p, `opción «${e.texto}»`); });
}
if (!problemas.length) ok(`panel: barra lateral en ${VISTAS.length} ventanas (${conDesplazamiento} con desplazamiento: todas las opciones y «Cerrar sesión» se alcanzan con el teclado y con la rueda, sin mover la página; ${sinDesplazamiento} sin él, como antes); «Ajustes» a la vista al abrirla; sin desplazamiento horizontal. Logotipo oficial en la barra lateral (con «ADMINISTRACIÓN» y el mismo estilo) y en el acceso (${ACCESO.length} anchos), no más ancho que la marca anterior; barra, contenido y formulario en su sitio; lo de debajo baja como mucho ${maxBajada.toFixed(1)} px (≤ lo que crece el logotipo)`);
else fallo(`${problemas.length} problemas:\n  ${problemas.slice(0, 30).join('\n  ')}`);

const lineas = Object.entries(densidad);
if (lineas.every(([, v]) => v && v.pixeles >= 2 * v.w)) ok(`densidad 2: ${lineas.map(([k, v]) => `${k} → ${v.src.split('/').pop()} (${v.pixeles} ≥ 2×${v.w.toFixed(0)})`).join('; ')}`);
else fallo(`densidad 2 sin resolución suficiente: ${JSON.stringify(densidad)}`);

const axeFallos = Object.entries(axe).filter(([, v]) => v.length);
if (!axeFallos.length) ok(`axe WCAG 2.1 A/AA en la barra lateral con la sesión iniciada (${Object.keys(axe).join(', ')}): 0 incumplimientos`);
else fallo(`axe en la barra lateral: ${JSON.stringify(axeFallos)}`);
