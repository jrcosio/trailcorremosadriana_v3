// Feature 012 · US6 (decisión P10): podio destacado en las clasificaciones (oro, plata y bronce),
// sin cambiar el resto de la tabla.
// Uso (desde frontend/, con Docker Compose en marcha y las clasificaciones de 2026 importadas):
//   node scripts/verificar-podio.mjs --referencia capturas/podio-antes-012.json   # antes del cambio
//   node scripts/verificar-podio.mjs --comparar capturas/podio-antes-012.json
import { readFileSync, writeFileSync } from 'node:fs';
import { fallo, navegador, ok } from './comun.mjs';

const [modo, archivo] = process.argv.slice(2);
if (!['--referencia', '--comparar'].includes(modo) || !archivo) {
  console.error('Uso: verificar-podio.mjs --referencia|--comparar <archivo.json> [url-base]');
  process.exit(2);
}
const base = process.argv[4] ?? 'http://localhost:8080';
const ANCHOS = [320, 360, 768, 1024, 1440];
const FILAS = 8; // los tres del podio y las siguientes, alternas

/** Medidas de las primeras filas de cada tabla de clasificación (en el navegador). */
function medir(filas) {
  return {
    desborda: document.documentElement.scrollWidth > innerWidth,
    tablas: [...document.querySelectorAll('.classification-card')].map((card) => {
      const tabla = card.querySelector('.classification-table');
      const t = tabla.getBoundingClientRect();
      return {
        nombre: card.querySelector('h2')?.textContent.trim(),
        tabla: { w: t.width, h: t.height },
        filas: [...tabla.querySelectorAll('tbody tr')].slice(0, filas).map((tr) => {
          const celdas = [...tr.children];
          const medalla = tr.querySelector('.podium-medal');
          const m = medalla && getComputedStyle(medalla);
          return {
            puesto: celdas[0].textContent.trim(),
            dorsal: celdas[1].textContent.trim(),
            clase: tr.className,
            fondo: getComputedStyle(tr).backgroundColor,
            h: tr.getBoundingClientRect().height,
            y: tr.getBoundingClientRect().top - t.top,
            franja: getComputedStyle(celdas[0]).boxShadow,
            colores: [...new Set([...celdas, ...tr.querySelectorAll('strong')].map((c) => getComputedStyle(c).color))],
            medalla: medalla && { texto: medalla.textContent.trim(), fondo: m.backgroundColor, color: m.color, peso: Number(m.fontWeight) },
          };
        }),
      };
    }),
  };
}

const browser = await navegador();
const page = await (await browser.newContext()).newPage();
const medidas = {};
for (const ancho of ANCHOS) {
  await page.setViewportSize({ width: ancho, height: 900 });
  await page.goto(base + '/clasificaciones/2026', { waitUntil: 'networkidle' });
  await page.waitForFunction(() => document.querySelectorAll('.classification-table tbody tr').length >= 3);
  medidas[ancho] = await page.evaluate(medir, FILAS);
}

// Búsqueda y filtro (1440 px): el ganador conserva su color al buscarlo por dorsal; con el filtro
// de sexo, las primeras filas de la lista filtrada no se colorean si no son del podio general.
let filtros = null;
if (modo === '--comparar') {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(base + '/clasificaciones/2026', { waitUntil: 'networkidle' });
  const tarjeta = page.locator('.classification-card').first();
  const caption = () => tarjeta.locator('caption').textContent();
  const esperarCambio = async (antes) => page.waitForFunction(([n, a]) => document.querySelectorAll('.classification-card')[n].querySelector('caption').textContent !== a, [0, antes], { timeout: 10000 });
  const primera = await tarjeta.locator('tbody tr').first().evaluate((tr) => ({ dorsal: tr.children[1].textContent.trim(), fondo: getComputedStyle(tr).backgroundColor }));
  let antes = await caption();
  await tarjeta.locator('input[type="search"]').fill(primera.dorsal);
  await esperarCambio(antes);
  const buscado = await tarjeta.locator('tbody tr').evaluateAll((trs, d) => trs.filter((tr) => tr.children[1].textContent.trim() === d).map((tr) => ({ puesto: tr.children[0].textContent.trim(), fondo: getComputedStyle(tr).backgroundColor })), primera.dorsal);
  antes = await caption();
  await tarjeta.locator('input[type="search"]').fill('');
  await esperarCambio(antes);
  antes = await caption();
  await tarjeta.locator('select').nth(1).selectOption({ label: 'Femenino' });
  await esperarCambio(antes);
  const femenino = await tarjeta.locator('tbody tr').evaluateAll((trs) => trs.slice(0, 5).map((tr) => ({ puesto: tr.children[0].textContent.trim(), clase: tr.className, medalla: Boolean(tr.querySelector('.podium-medal')) })));
  filtros = { primera, buscado, femenino };
}
await browser.close();

if (modo === '--referencia') {
  writeFileSync(archivo, JSON.stringify(medidas, null, 1));
  const n = Object.values(medidas).reduce((s, m) => s + m.tablas.length, 0);
  console.log(`Referencia guardada: ${n} tablas (${ANCHOS.length} anchos), ${FILAS} primeras filas de cada una.`);
  process.exit(0);
}

const ref = JSON.parse(readFileSync(archivo, 'utf8'));
const rgb = (c) => (c.match(/[\d.]+/g) ?? []).map(Number);
const transparente = (c) => c === 'rgba(0, 0, 0, 0)' || c === 'transparent';
const efectivo = (c) => (transparente(c) ? 'rgb(255, 255, 255)' : c); // la tabla está sobre blanco
const lum = (c) => rgb(c).slice(0, 3).map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }).reduce((s, v, k) => s + v * [0.2126, 0.7152, 0.0722][k], 0);
const contraste = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
const problemas = [];
const podio = new Map(); // puesto → colores vistos
let minTexto = Infinity, minMedalla = Infinity, filasPodio = 0, filasResto = 0;
for (const ancho of ANCHOS) {
  const m = medidas[ancho], r = ref[ancho];
  const p = (t) => problemas.push(`${ancho} px: ${t}`);
  if (m.desborda) p('desbordamiento horizontal');
  if (m.tablas.length !== r.tablas.length) { p('cambia el número de tablas'); continue; }
  m.tablas.forEach((t, k) => {
    const a = r.tablas[k];
    const q = (txt) => p(`${t.nombre}: ${txt}`);
    if (Math.abs(t.tabla.w - a.tabla.w) > 0.5 || Math.abs(t.tabla.h - a.tabla.h) > 0.5) q(`la tabla cambia de tamaño (${JSON.stringify(a.tabla)} → ${JSON.stringify(t.tabla)})`);
    const fondosResto = new Set(a.filas.map((f) => efectivo(f.fondo)));
    t.filas.forEach((f, i) => {
      const fa = a.filas[i];
      if (!fa || fa.dorsal !== f.dorsal) { q(`fila ${i + 1}: no coincide con la referencia`); return; }
      if (Math.abs(f.h - fa.h) > 0.5 || Math.abs(f.y - fa.y) > 0.5) q(`fila ${i + 1}: cambia de alto o de sitio (${fa.h.toFixed(1)} → ${f.h.toFixed(1)})`);
      const fondo = efectivo(f.fondo);
      for (const c of f.colores) { const x = contraste(c, fondo); minTexto = Math.min(minTexto, x); if (x < 4.5) q(`fila ${i + 1}: texto ${c} sobre ${fondo} a ${x.toFixed(2)}:1`); }
      if (['1', '2', '3'].includes(f.puesto)) {
        filasPodio++;
        if (f.clase !== `podium podium-${f.puesto}`) q(`puesto ${f.puesto}: clase «${f.clase}»`);
        if (fondosResto.has(fondo)) q(`puesto ${f.puesto}: el fondo ${fondo} es el de una fila normal`);
        if (!f.medalla || f.medalla.texto !== f.puesto) { q(`puesto ${f.puesto}: sin medalla con el número`); return; }
        if (f.medalla.peso < 700) q(`puesto ${f.puesto}: el número no va en negrita`);
        const x = contraste(f.medalla.color, f.medalla.fondo);
        minMedalla = Math.min(minMedalla, x);
        if (x < 4.5) q(`puesto ${f.puesto}: medalla a ${x.toFixed(2)}:1`);
        if (!f.franja.includes(f.medalla.fondo)) q(`puesto ${f.puesto}: la franja (${f.franja}) no es del color de la medalla (${f.medalla.fondo})`);
        if (!podio.has(f.puesto)) podio.set(f.puesto, new Set());
        podio.get(f.puesto).add(`${fondo} | ${f.medalla.fondo}`);
      } else {
        filasResto++;
        if (f.clase || f.medalla) q(`fila ${i + 1} (puesto ${f.puesto}): marcada como podio`);
        if (f.fondo !== fa.fondo) q(`fila ${i + 1} (puesto ${f.puesto}): cambia el fondo (${fa.fondo} → ${f.fondo})`);
        if (f.franja !== fa.franja) q(`fila ${i + 1}: aparece una franja (${f.franja})`);
      }
    });
  });
}
// Un color por puesto en todas las tablas y anchos, y los tres distintos entre sí.
const colores = [...podio.entries()].map(([k, v]) => [k, [...v]]);
for (const [k, v] of colores) if (v.length !== 1) problemas.push(`puesto ${k}: colores distintos según la tabla o el ancho (${v.join(' / ')})`);
if (colores.length !== 3 || new Set(colores.map(([, v]) => v[0].split(' | ')[0])).size !== 3) problemas.push(`no hay tres fondos de podio distintos: ${JSON.stringify(colores)}`);

if (!problemas.length) ok(`${filasPodio} filas del podio en ${ANCHOS.length} anchos con su fondo, su franja y su medalla en negrita (${colores.map(([k, v]) => `${k}.º ${v[0]}`).join('; ')}); ${filasResto} filas restantes sin cambios; alto de filas y tamaño de las tablas con 0 px de diferencia; contraste mínimo del texto ${minTexto.toFixed(2)}:1 y de las medallas ${minMedalla.toFixed(2)}:1; sin desbordamientos`);
else fallo(`${problemas.length} problemas:\n  ${problemas.slice(0, 25).join('\n  ')}`);

const { primera, buscado, femenino } = filtros;
if (buscado.length === 1 && buscado[0].puesto === '1' && buscado[0].fondo === primera.fondo) ok(`búsqueda del dorsal ${primera.dorsal}: el 1.º conserva su color`);
else fallo(`búsqueda del ganador: ${JSON.stringify({ primera, buscado })}`);
const malFiltradas = femenino.filter((f) => !['1', '2', '3'].includes(f.puesto) && (f.clase || f.medalla));
if (femenino.length && !malFiltradas.length) ok(`filtro «Femenino»: las primeras filas (puestos ${femenino.map((f) => f.puesto).join(', ')}) no se colorean`);
else fallo(`filtro «Femenino»: ${JSON.stringify(femenino)}`);
