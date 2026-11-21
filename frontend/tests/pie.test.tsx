/**
 * Feature 012 · US5 (decisión P9 del propietario): la línea inferior del pie dice
 * «Hecho por la Escuela Hacker Cosío» en lugar de «Hecho con pasión por JR BLANCO · Hackers Cosío».
 * El pie es común a todas las páginas públicas, incluida la de página no encontrada.
 */
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import Site from '@/components/Site';

const RUTAS = [
  '/', '/carreras', '/carreras/trail-27k', '/recorridos', '/solidaridad', '/inscripciones', '/noticias',
  '/galeria', '/clasificaciones', '/reglamento', '/patrocinadores', '/contacto', '/no-existe',
];
const FRASE = 'Hecho por la Escuela Hacker Cosío';

describe('Pie: frase de autoría (P9)', () => {
  it.each(RUTAS)('%s muestra la frase nueva sin restos de la anterior', (ruta) => {
    const html = renderToStaticMarkup(<Site path={ruta} />);
    const franja = html.match(/<div class="container footer-bottom">(.*?)<\/div><\/footer>/)?.[1];
    expect(franja, 'sin línea inferior del pie').toBeDefined();
    const lineas = [...franja!.matchAll(/<span>(.*?)<\/span>/g)].map((m) => m[1]);
    // El aviso de copyright no cambia; la frase nueva es texto, sin enlace (FR-017, FR-018).
    expect(lineas).toEqual([`© ${new Date().getFullYear()} Asociación Peñasagra`, FRASE]);
    expect(franja).not.toMatch(/<a\b/);
    expect(html).not.toMatch(/Hecho con pasión|JR BLANCO|Hackers Cosío|jrblanco\.es/);
  });
});
