// Verifica todas las rutas de FR-001: estado HTTP y pantalla esperada al abrir y al recargar.
// Desde la feature 011 las rutas inexistentes responden 404 real (DISCREPANCIAS U4).
// Uso: node scripts/verificar-rutas.mjs [url-base]
import { fallo, navegador, ok } from './comun.mjs';

const base = process.argv[2] ?? 'http://localhost:8080';
// /pantallas solo existe con PANTALLAS=si (revisión local, decisión P5); si no, 404 real.
const pantallasActivas = (await fetch(base + '/pantallas')).status === 200;
const NO_ENCONTRADA = 'Este sendero no está en el mapa.';
const ADMIN = ['', '/noticias', '/noticias/nuevo', '/noticias/proxima-edicion', '/clasificaciones', '/clasificaciones/nuevo', '/galeria', '/galeria/nuevo', '/galeria/edicion-2026', '/recorridos', '/recorridos/nuevo', '/recorridos/trail-27k', '/patrocinadores', '/patrocinadores/nuevo', '/colaboradores', '/colaboradores/nuevo', '/inscripciones', '/evento', '/reglamento', '/ajustes'];
// [ruta, texto que debe aparecer]
const RUTAS = [
  ['/', 'PEÑASAGRA'],
  ['/carreras', 'Trail Peñasagra'],
  ['/carreras/trail-27k', 'Trail Peñasagra'],
  ['/carreras/speed-14k', 'Speed Trail'],
  ['/carreras/familiar-7k', 'Familiar'],
  ['/recorridos', 'Speed Trail'],
  ['/recorridos/speed-14k', 'Speed Trail'],
  ['/inscripciones', 'Inscripciones'],
  ['/noticias', 'Peñasagra 2027'],
  ['/noticias/proxima-edicion', 'Peñasagra 2027 ya está en el horizonte'],
  ['/galeria', 'Volver a sentir la montaña'],
  ['/galeria/edicion-2026', 'Volver a sentir la montaña'],
  ['/clasificaciones', 'Clasificaciones'],
  ['/reglamento', 'Reglamento'],
  ['/solidaridad', 'Nuestra razón para correr.'],
  ['/patrocinadores', 'Patrocinadores'],
  ['/contacto', 'asociacionpenasagra@gmail.com'],
  ['/pantallas', 'Todo Peñasagra, pantalla a pantalla.'],
  ['/admin', 'Hola, equipo.'],
  ['/carreras/no-existe', 'Este sendero no está en el mapa.'],
  ['/noticias/no-existe', 'Este sendero no está en el mapa.'],
  ['/no-existe', 'Este sendero no está en el mapa.'],
  ...ADMIN.map((s) => ['/pantallas/admin' + s, 'Vista de diseño']),
];

const browser = await navegador();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
let comprobadas = 0;
for (const [ruta, previsto] of RUTAS) {
  const esperado = !pantallasActivas && ruta.startsWith('/pantallas') ? NO_ENCONTRADA : previsto;
  const respuesta = await page.goto(base + ruta, { waitUntil: 'networkidle' });
  const estado = respuesta?.status();
  const texto1 = await page.evaluate(() => document.body.innerText);
  await page.reload({ waitUntil: 'networkidle' });
  const texto2 = await page.evaluate(() => document.body.innerText);
  const estadoEsperado = esperado === NO_ENCONTRADA ? 404 : 200;
  if (estado !== estadoEsperado) fallo(`${ruta}: HTTP ${estado} (esperado ${estadoEsperado})`);
  else if (!texto1.includes(esperado)) fallo(`${ruta}: no aparece «${esperado}» al abrir`);
  else if (!texto2.includes(esperado)) fallo(`${ruta}: no aparece «${esperado}» al recargar`);
  else ok(`${ruta} → «${esperado}»`);
  comprobadas++;
}
await browser.close();
console.log(`\n${comprobadas} rutas comprobadas (/pantallas ${pantallasActivas ? 'activas' : 'retiradas'})`);
