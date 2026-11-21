// Feature 012 · US6 (decisión P10) y US10 (decisión P12): podio de las clasificaciones.
// - Sin filtros: los 3 primeros hombres y las 3 primeras mujeres de cada prueba.
// - Con el filtro de sexo, el podio de ese sexo; con el de categoría, el de esa categoría.
// Las filas del podio llevan fondo y franja de oro, plata o bronce y una etiqueta junto al nombre
// («1.ª mujer»); la columna «Pos.» conserva la posición general. El podio esperado se calcula
// aparte, con todas las páginas de la API: así el script no depende del código que verifica.
// Uso (desde frontend/, con Docker Compose en marcha y las clasificaciones de 2026 importadas):
//   node scripts/verificar-podio.mjs --referencia capturas/podio-sexo-antes-012.json   # antes del cambio
//   node scripts/verificar-podio.mjs --comparar capturas/podio-sexo-antes-012.json
import { readFileSync, writeFileSync } from 'node:fs';
import { fallo, navegador, ok } from './comun.mjs';

const [modo, archivo] = process.argv.slice(2);
if (!['--referencia', '--comparar'].includes(modo) || !archivo) {
  console.error('Uso: verificar-podio.mjs --referencia|--comparar <archivo.json> [url-base]');
  process.exit(2);
}
const base = process.argv[4] ?? 'http://localhost:8080';
const ANCHOS = [320, 360, 768, 1024, 1440];

// --- Podio esperado (oráculo independiente) ---
const contenido = (await (await fetch(base + '/api/content')).json()).data;
const clasificaciones = contenido.results.filter((r) => r.year === '2026');
const todas = {};
for (const c of clasificaciones) {
  const filas = [];
  for (let pagina = 1; ; pagina++) {
    const p = await (await fetch(`${base}/api/clasificaciones/${c.id}/participantes?pagina=${pagina}`)).json();
    filas.push(...p.rows);
    if (pagina >= p.pages) break;
  }
  todas[c.title] = filas;
}
const FEMENINO = /^(femenino|f|mujer)$/i, MASCULINO = /^(masculino|m|hombre)$/i;
/** Dorsal → puesto en el podio (1–3), con la regla de la spec (FR-028). */
function podioEsperado(filas, { categoria = '', sexo = '' } = {}) {
  const conSexo = filas.some((f) => f.gender);
  const grupo = filas.filter((f) => f.position != null && (!categoria || f.category === categoria) && (!sexo || f.gender === sexo) && (!conSexo || f.gender));
  const puestos = new Map();
  for (const f of grupo) {
    const puesto = 1 + grupo.filter((o) => o.gender === f.gender && o.position < f.position).length;
    if (puesto <= 3) puestos.set(f.bib, puesto);
  }
  return puestos;
}
function etiquetaEsperada(puesto, fila, categoria) {
  const ordinal = `${puesto}.${FEMENINO.test(fila.gender) ? 'ª' : 'º'}`;
  const grupo = categoria || (FEMENINO.test(fila.gender) ? 'mujer' : MASCULINO.test(fila.gender) ? 'hombre' : fila.gender || 'general');
  return `${ordinal} ${grupo}`;
}

// --- Medidas en el navegador ---
function medir() {
  return {
    desborda: document.documentElement.scrollWidth > innerWidth,
    tablas: [...document.querySelectorAll('.classification-card')].map((card) => ({
      nombre: card.querySelector('h2')?.textContent.trim(),
      filas: [...card.querySelectorAll('.classification-table tbody tr')].map((tr) => {
        const c = [...tr.children];
        const etiqueta = tr.querySelector('.podium-label');
        const e = etiqueta && getComputedStyle(etiqueta);
        return {
          puesto: c[0].textContent.trim(), dorsal: c[1].textContent.trim(), clase: tr.className,
          fondo: getComputedStyle(tr).backgroundColor, h: tr.getBoundingClientRect().height,
          franja: getComputedStyle(c[0]).boxShadow, medalla: Boolean(tr.querySelector('.podium-medal')),
          colores: [...new Set([...c, ...tr.querySelectorAll('strong')].map((x) => getComputedStyle(x).color))],
          etiqueta: etiqueta && { texto: etiqueta.textContent.trim(), fondo: e.backgroundColor, color: e.color, peso: Number(e.fontWeight) },
        };
      }),
    })),
  };
}

const browser = await navegador();
const page = await (await browser.newContext()).newPage();
const abrir = async (ancho) => {
  await page.setViewportSize({ width: ancho, height: 900 });
  await page.goto(base + '/clasificaciones/2026', { waitUntil: 'networkidle' });
  await page.waitForFunction(() => document.querySelectorAll('.classification-table tbody tr').length >= 3);
};
const medidas = {};
for (const ancho of ANCHOS) { await abrir(ancho); medidas[ancho] = await page.evaluate(medir); }

// Filtros y búsqueda (1440 y 360 px): sexo en cada prueba, una categoría y la campeona buscada por dorsal.
const filtradas = [];
if (modo === '--comparar') {
  for (const ancho of [1440, 360]) {
    for (const [k, c] of clasificaciones.entries()) {
      const casos = [{ sexo: 'Femenino' }, { sexo: 'Masculino' }];
      const categorias = [...new Set(todas[c.title].map((f) => f.category).filter(Boolean))];
      if (categorias.includes('Senior F')) casos.push({ categoria: 'Senior F' });
      const primera = [...podioEsperado(todas[c.title], { sexo: 'Femenino' })].find(([, p]) => p === 1);
      if (primera) casos.push({ q: primera[0] });
      for (const caso of casos) {
        await abrir(ancho);
        const tarjeta = page.locator('.classification-card').nth(k);
        const antes = await tarjeta.locator('caption').textContent();
        if (caso.sexo) await tarjeta.locator('select').nth(1).selectOption({ label: caso.sexo });
        if (caso.categoria) await tarjeta.locator('select').nth(0).selectOption({ label: caso.categoria });
        if (caso.q) await tarjeta.locator('input[type="search"]').fill(caso.q);
        await page.waitForFunction(([n, a]) => document.querySelectorAll('.classification-card')[n].querySelector('caption').textContent !== a, [k, antes], { timeout: 10000 });
        const m = await page.evaluate(medir);
        filtradas.push({ ancho, nombre: c.title, caso, filas: m.tablas[k].filas, desborda: m.desborda });
      }
    }
  }
}
await browser.close();

if (modo === '--referencia') {
  writeFileSync(archivo, JSON.stringify(medidas, null, 1));
  console.log(`Referencia guardada: ${ANCHOS.length} anchos, ${Object.values(medidas)[0].tablas.map((t) => `${t.nombre} (${t.filas.length} filas)`).join(', ')}.`);
  process.exit(0);
}

// --- Comparación ---
const ref = JSON.parse(readFileSync(archivo, 'utf8'));
const rgb = (c) => (c.match(/[\d.]+/g) ?? []).map(Number);
const efectivo = (c) => (c === 'rgba(0, 0, 0, 0)' || c === 'transparent' ? 'rgb(255, 255, 255)' : c);
const lum = (c) => rgb(c).slice(0, 3).map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }).reduce((s, v, k) => s + v * [0.2126, 0.7152, 0.0722][k], 0);
const contraste = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
const problemas = [];
const colores = new Map(); // puesto → fondos y etiquetas vistos
let filasPodio = 0, filasResto = 0, minTexto = Infinity, minEtiqueta = Infinity;
// La etiqueta ensancha la columna del nombre y la tabla reparte de nuevo los anchos. Algún texto
// largo (club) puede cambiar de salto de línea: se informa, pero no es un fallo (spec FR-031).
const reajustes = [];
const normales = new Set(['rgb(255, 255, 255)', 'rgb(248, 250, 249)']);

/** Comprueba las filas de una tabla contra el podio esperado. `ref` (opcional) da fondo y alto previos por dorsal. */
function comprobar(filas, todasLasFilas, filtro, p, refPorDorsal) {
  const esperado = podioEsperado(todasLasFilas, filtro);
  const porDorsal = new Map(todasLasFilas.map((f) => [f.bib, f]));
  for (const f of filas) {
    const datos = porDorsal.get(f.dorsal);
    const puesto = f.dorsal ? esperado.get(f.dorsal) : undefined;
    const fondo = efectivo(f.fondo);
    for (const c of f.colores) { const x = contraste(c, fondo); minTexto = Math.min(minTexto, x); if (x < 4.5) p(`dorsal ${f.dorsal}: texto ${c} sobre ${fondo} a ${x.toFixed(2)}:1`); }
    if (f.medalla) p(`dorsal ${f.dorsal}: queda la medalla redonda`);
    if (datos && f.puesto !== String(datos.position ?? '—')) p(`dorsal ${f.dorsal}: «Pos.» muestra ${f.puesto} y su posición general es ${datos.position}`);
    if (puesto) {
      filasPodio++;
      const texto = etiquetaEsperada(puesto, datos, filtro.categoria);
      if (f.clase !== `podium podium-${puesto}`) p(`dorsal ${f.dorsal} (${texto}): clase «${f.clase}»`);
      if (!f.etiqueta || f.etiqueta.texto !== texto) { p(`dorsal ${f.dorsal}: etiqueta «${f.etiqueta?.texto}» y debería ser «${texto}»`); continue; }
      if (normales.has(fondo)) p(`dorsal ${f.dorsal} (${texto}): fondo de fila normal`);
      if (f.etiqueta.peso < 700) p(`dorsal ${f.dorsal}: la etiqueta no va en negrita`);
      const x = contraste(f.etiqueta.color, f.etiqueta.fondo);
      minEtiqueta = Math.min(minEtiqueta, x);
      if (x < 4.5) p(`dorsal ${f.dorsal}: etiqueta a ${x.toFixed(2)}:1`);
      if (!f.franja.includes(f.etiqueta.fondo)) p(`dorsal ${f.dorsal}: la franja no es del color de la etiqueta`);
      if (!colores.has(puesto)) colores.set(puesto, new Set());
      colores.get(puesto).add(`${fondo} | ${f.etiqueta.fondo}`);
    } else {
      filasResto++;
      if (f.clase || f.etiqueta) p(`dorsal ${f.dorsal}: marcada como podio sin serlo (${f.etiqueta?.texto ?? f.clase})`);
      if (!normales.has(fondo)) p(`dorsal ${f.dorsal}: fondo ${fondo} en una fila normal`);
      const a = refPorDorsal?.get(f.dorsal);
      if (a && a.fondo !== f.fondo) p(`dorsal ${f.dorsal}: cambia el fondo (${a.fondo} → ${f.fondo})`);
      if (a && Math.abs(a.h - f.h) > 0.5) reajustes.push(`${f.dorsal} (${a.h.toFixed(0)} → ${f.h.toFixed(0)} px)`);
    }
  }
  // Todo el podio esperado que está en la página aparece marcado.
  const enPagina = new Set(filas.map((f) => f.dorsal));
  const faltan = [...esperado.keys()].filter((d) => enPagina.has(d) && !filas.find((f) => f.dorsal === d)?.etiqueta);
  if (faltan.length) p(`podio sin marcar: dorsales ${faltan.join(', ')}`);
  return [...esperado.keys()].filter((d) => enPagina.has(d)).length;
}

let sinFiltros = 0;
for (const ancho of ANCHOS) {
  const m = medidas[ancho];
  if (m.desborda) problemas.push(`${ancho} px: desbordamiento horizontal`);
  for (const t of m.tablas) {
    const a = ref[ancho].tablas.find((x) => x.nombre === t.nombre);
    const p = (txt) => problemas.push(`${ancho} px ${t.nombre}: ${txt}`);
    const enPagina = comprobar(t.filas, todas[t.nombre], {}, p, new Map(a.filas.map((f) => [f.dorsal, f])));
    if (ancho === 1440) sinFiltros += enPagina;
  }
}
const casosFiltrados = new Set();
for (const v of filtradas) {
  const p = (txt) => problemas.push(`${v.ancho} px ${v.nombre} ${JSON.stringify(v.caso)}: ${txt}`);
  if (v.desborda) p('desbordamiento horizontal');
  const marcadas = comprobar(v.filas, todas[v.nombre], { categoria: v.caso.categoria, sexo: v.caso.sexo }, p);
  if (!marcadas) p('ninguna fila del podio en la vista');
  casosFiltrados.add(`${v.nombre.replace(/^Clasificación /, '').replace(/ \d{4}$/, '')}: ${v.caso.sexo ?? v.caso.categoria ?? `dorsal ${v.caso.q}`}`);
}
const vistos = [...colores.entries()].map(([k, v]) => [k, [...v]]);
for (const [k, v] of vistos) if (v.length !== 1) problemas.push(`puesto ${k}: colores distintos según la tabla (${v.join(' / ')})`);
if (new Set(vistos.map(([, v]) => v[0].split(' | ')[0])).size !== 3) problemas.push(`no hay tres fondos de podio distintos: ${JSON.stringify(vistos)}`);

if (!problemas.length) ok(`podio: ${sinFiltros} filas sin filtros a 1440 px (3 hombres y 3 mujeres por prueba) y ${casosFiltrados.size} casos con filtro o búsqueda (${[...casosFiltrados].join('; ')}); ${filasPodio} filas del podio con su fondo, su franja y su etiqueta, y «Pos.» con la posición general; ${filasResto} filas restantes sin marcar y con el mismo fondo; contraste mínimo del texto ${minTexto.toFixed(2)}:1 y de la etiqueta ${minEtiqueta.toFixed(2)}:1; sin desbordamientos`);
else fallo(`${problemas.length} problemas:\n  ${[...new Set(problemas)].slice(0, 30).join('\n  ')}`);

console.log(`INFO  reajuste de columnas: ${reajustes.length} filas que no son del podio cambian de salto de línea${reajustes.length ? ` (${reajustes.join(', ')})` : ''}`);
