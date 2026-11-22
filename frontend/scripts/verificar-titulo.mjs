// Feature 012 · US11 (decisión P13 del propietario): el título de la portada dice «TRAIL» y
// «PEÑASAGRA», con Ñ, con el mismo tamaño, color y posición que antes.
// Comprueba a 320, 360, 768, 1024 y 1440 px:
// - el texto del título y la fuente que lo dibuja (Barlow Condensed, que tiene la Ñ);
// - que el título y sus dos líneas ocupan la misma caja que en la referencia previa;
// - que no hay desbordamiento horizontal;
// - la separación entre la virgulilla de la Ñ y la línea «TRAIL» (se informa; falla si se tocan).
// Uso (desde frontend/, con Docker Compose en marcha):
//   node scripts/verificar-titulo.mjs --referencia capturas/titulo-antes-012.json   # antes del cambio
//   node scripts/verificar-titulo.mjs --comparar capturas/titulo-antes-012.json
import { readFileSync, writeFileSync } from 'node:fs';
import { fallo, navegador, ok } from './comun.mjs';

const [modo, archivo] = process.argv.slice(2);
if (!['--referencia', '--comparar'].includes(modo) || !archivo) {
  console.error('Uso: verificar-titulo.mjs --referencia|--comparar <archivo.json> [url-base]');
  process.exit(2);
}
const base = process.argv[4] ?? 'http://localhost:8080';
const ANCHOS = [320, 360, 768, 1024, 1440];
const redondear = (r) => ({ x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) });

const browser = await navegador();
const medidas = {};
for (const ancho of ANCHOS) {
  const page = await browser.newPage({ viewport: { width: ancho, height: 900 } });
  await page.goto(base + '/', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  medidas[ancho] = await page.evaluate(() => {
    const h1 = document.querySelector('.hero h1');
    const em = h1.querySelector('em');
    const estilo = getComputedStyle(h1);
    const tamano = parseFloat(estilo.fontSize);
    const lineas = [h1.firstChild, em.firstChild].map((nodo) => {
      const r = document.createRange();
      r.selectNodeContents(nodo);
      return r.getBoundingClientRect();
    });
    // Virgulilla de la Ñ frente a la línea «TRAIL»: con las métricas reales de la fuente, la
    // separación vertical entre la base de «TRAIL» y lo más alto de la Ñ es el interlineado menos
    // el alto de la Ñ sobre su línea base y lo que «TRAIL» baja de la suya.
    const lienzo = document.createElement('canvas').getContext('2d');
    lienzo.font = `${estilo.fontWeight} ${estilo.fontSize} ${estilo.fontFamily}`;
    const n = em.textContent.indexOf('Ñ');
    let virgulilla = null;
    if (n >= 0) {
      const rN = document.createRange();
      rN.setStart(em.firstChild, n);
      rN.setEnd(em.firstChild, n + 1);
      const cajaN = rN.getBoundingClientRect();
      const interlineado = lineas[1].top - lineas[0].top;
      const separacion = interlineado - lienzo.measureText('Ñ').actualBoundingBoxAscent - lienzo.measureText('TRAIL').actualBoundingBoxDescent;
      const debajoDeTrail = cajaN.left < lineas[0].right && cajaN.right > lineas[0].left;
      virgulilla = { separacion: Math.round(separacion * 10) / 10, debajoDeTrail };
    }
    return {
      texto: h1.innerText.replace(/\s+/g, ' ').trim(),
      em: em.textContent,
      fuente: estilo.fontFamily,
      barlow: document.fonts.check(`${estilo.fontWeight} ${estilo.fontSize} "Barlow Condensed"`, em.textContent),
      tamano,
      color: getComputedStyle(em).color,
      h1: h1.getBoundingClientRect().toJSON(),
      lineas: lineas.map((l) => l.toJSON()),
      virgulilla,
      desborda: document.documentElement.scrollWidth > window.innerWidth,
    };
  });
  // Recorte del título: `<archivo>-<ancho>.png` en la referencia y `<archivo>-comparado-<ancho>.png` al comparar.
  await page.locator('.hero h1').screenshot({ path: archivo.replace(/\.json$/, `${modo === '--referencia' ? '' : '-comparado'}-${ancho}.png`) });
  await page.close();
}
await browser.close();

if (modo === '--referencia') {
  writeFileSync(archivo, JSON.stringify(medidas, null, 2));
  for (const [ancho, m] of Object.entries(medidas)) console.log(`${ancho}px «${m.texto}» h1 ${JSON.stringify(redondear(m.h1))} desborda=${m.desborda}`);
  console.log(`Referencia guardada en ${archivo}`);
  process.exit(0);
}

const referencia = JSON.parse(readFileSync(archivo, 'utf8'));
for (const ancho of ANCHOS) {
  const m = medidas[ancho], r = referencia[ancho];
  const errores = [];
  if (m.texto !== 'TRAIL PEÑASAGRA') errores.push(`el título dice «${m.texto}»`);
  if (m.em !== 'PEÑASAGRA') errores.push(`la segunda línea dice «${m.em}»`);
  if (!m.barlow || !m.fuente.startsWith('"Barlow Condensed"')) errores.push(`la fuente no es Barlow Condensed (${m.fuente})`);
  if (m.tamano !== r.tamano) errores.push(`tamaño ${m.tamano}px (antes ${r.tamano}px)`);
  if (m.color !== r.color) errores.push(`color ${m.color} (antes ${r.color})`);
  // La caja del título y la de cada línea: misma posición y alto; el ancho de la 2.ª línea puede
  // variar unos píxeles porque la Ñ y la N no miden exactamente lo mismo.
  const a = redondear(m.h1), b = redondear(r.h1);
  if (a.x !== b.x || a.y !== b.y || a.w !== b.w || a.h !== b.h) errores.push(`caja del título ${JSON.stringify(a)} (antes ${JSON.stringify(b)})`);
  m.lineas.forEach((l, i) => {
    const la = redondear(l), lb = redondear(r.lineas[i]);
    const tolerancia = i === 1 ? Math.ceil(m.tamano * 0.05) : 0;
    if (la.x !== lb.x || la.y !== lb.y || la.h !== lb.h || Math.abs(la.w - lb.w) > tolerancia) errores.push(`línea ${i + 1} ${JSON.stringify(la)} (antes ${JSON.stringify(lb)})`);
  });
  if (m.desborda) errores.push('desbordamiento horizontal de la página');
  if (!m.virgulilla) errores.push('no se encuentra la Ñ');
  else if (m.virgulilla.debajoDeTrail && m.virgulilla.separacion < 0) errores.push(`la virgulilla de la Ñ invade la línea «TRAIL» (${m.virgulilla.separacion}px)`);
  const detalle = m.virgulilla ? ` · virgulilla a ${m.virgulilla.separacion}px de «TRAIL»${m.virgulilla.debajoDeTrail ? '' : ' (fuera de su vertical)'}` : '';
  if (errores.length) fallo(`${ancho}px: ${errores.join('; ')}`);
  else ok(`${ancho}px «${m.texto}» en Barlow Condensed ${m.tamano}px, misma caja que antes, sin desbordamiento${detalle}`);
}
