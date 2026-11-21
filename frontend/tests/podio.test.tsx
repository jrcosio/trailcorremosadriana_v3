/**
 * Feature 012 · US6 (decisión P10) y US10 (decisión P12): podio de las clasificaciones.
 * Hay un podio por sexo (o de la general si no hay datos de sexo) y, con el filtro de categoría,
 * uno de la categoría. Las filas del podio llevan `podium podium-N` y una etiqueta junto al nombre;
 * «Pos.» conserva la posición general. La regla es la misma que la del servidor (FR-028).
 */
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import ClassificationTable from '@/components/ClassificationTable';
import { etiquetaPodio, rangosPodio, type ClassificationRow } from '@/lib/classifications';

const fila = (position: number | null, bib: string, gender = '', category = ''): ClassificationRow =>
  ({ position, bib, name: `Participante ${bib}`, time: position ? '1:00:00' : '', category, club: '', gender, status: position ? '' : 'Retirado' });

// Hombres 1–4 y 6; mujeres 5, 7 (empate), 9 y 10; con puesto y sin sexo; sin puesto.
const filas = [
  fila(1, 'H1', 'Masculino', 'Vet A M'), fila(2, 'H2', 'Masculino', 'Senior M'), fila(3, 'H3', 'Masculino', 'Vet A M'),
  fila(4, 'H4', 'Masculino', 'Senior M'), fila(5, 'M1', 'Femenino', 'Senior F'), fila(6, 'H5', 'Masculino', 'Vet A M'),
  fila(7, 'M2', 'Femenino', 'Vet A F'), fila(7, 'M2b', 'Femenino', 'Senior F'), fila(9, 'M4', 'Femenino', 'Senior F'),
  fila(10, 'M5', 'Femenino', 'Vet A F'), fila(11, 'SinSexo'), fila(null, 'SinPuesto', 'Femenino', 'Senior F'),
];
const podio = (rows: ClassificationRow[], filtro = {}) => Object.fromEntries([...rangosPodio(rows, filtro)].map(([r, p]) => [r.bib, p]));

describe('rangosPodio (FR-028)', () => {
  it('sin filtros: 3 hombres y 3 mujeres; el empate comparte el 2.º y deja sin 3.º; sin sexo no entra', () => {
    expect(podio(filas)).toEqual({ H1: 1, H2: 2, H3: 3, M1: 1, M2: 2, M2b: 2 });
  });
  it('con el filtro de sexo, el podio de ese sexo', () => {
    expect(podio(filas, { gender: 'Femenino' })).toEqual({ M1: 1, M2: 2, M2b: 2 });
    expect(podio(filas, { gender: 'Masculino' })).toEqual({ H1: 1, H2: 2, H3: 3 });
  });
  it('con el filtro de categoría, el podio de la categoría', () => {
    expect(podio(filas, { category: 'Senior F' })).toEqual({ M1: 1, M2b: 2, M4: 3 });
    expect(podio(filas, { category: 'Vet A M' })).toEqual({ H1: 1, H3: 2, H5: 3 });
  });
  it('sin datos de sexo en la clasificación: podio de la general', () => {
    expect(podio(filas.map((r) => ({ ...r, gender: '' })))).toEqual({ H1: 1, H2: 2, H3: 3 });
  });
  it('sin puestos no hay podio', () => {
    expect(podio([fila(null, 'A', 'Femenino'), fila(null, 'B', 'Masculino')])).toEqual({});
  });
});

describe('etiquetaPodio (FR-029)', () => {
  it.each([
    [1, 'Femenino', '', '1.ª mujer'], [2, 'Masculino', '', '2.º hombre'], [3, 'F', '', '3.ª mujer'], [1, 'M', '', '1.º hombre'],
    [1, 'Masculino', 'Vet A M', '1.º Vet A M'], [1, 'Femenino', 'Senior F', '1.ª Senior F'], [1, '', '', '1.º general'], [2, 'Mixto', '', '2.º Mixto'],
  ])('puesto %i, sexo «%s», categoría «%s» → «%s»', (puesto, sexo, categoria, texto) => {
    expect(etiquetaPodio(puesto, sexo, categoria)).toBe(texto);
  });
});

/** Filas de la tabla: clase del `<tr>`, celda «Pos.» y etiqueta. */
function tabla(rows: ClassificationRow[], preview = false) {
  const html = renderToStaticMarkup(<ClassificationTable rows={rows} preview={preview} label="Prueba" />);
  const cuerpo = html.match(/<tbody>(.*)<\/tbody>/)?.[1] ?? '';
  return [...cuerpo.matchAll(/<tr([^>]*)><td[^>]*>(.*?)<\/td>(.*?)<\/tr>/g)].map(([, attrs, puesto, resto]) => ({
    clase: attrs.match(/class="([^"]*)"/)?.[1] ?? '', puesto, etiqueta: resto.match(/<span class="podium-label">([^<]*)<\/span>/)?.[1] ?? null,
  }));
}

describe('Tabla: podio en el modo cliente (panel)', () => {
  it('marca a los 3 primeros de cada sexo con su etiqueta y deja la posición general en «Pos.»', () => {
    const t = tabla(filas);
    expect(t.filter((f) => f.clase)).toEqual([
      { clase: 'podium podium-1', puesto: '1', etiqueta: '1.º hombre' },
      { clase: 'podium podium-2', puesto: '2', etiqueta: '2.º hombre' },
      { clase: 'podium podium-3', puesto: '3', etiqueta: '3.º hombre' },
      { clase: 'podium podium-1', puesto: '5', etiqueta: '1.ª mujer' },
      { clase: 'podium podium-2', puesto: '7', etiqueta: '2.ª mujer' },
      { clase: 'podium podium-2', puesto: '7', etiqueta: '2.ª mujer' },
    ]);
    expect(t.filter((f) => !f.clase).every((f) => f.etiqueta === null)).toBe(true);
    expect(renderToStaticMarkup(<ClassificationTable rows={filas} label="Prueba" />)).not.toContain('podium-medal');
  });

  it('la vista previa del panel aplica la misma regla', () => {
    expect(tabla(filas, true).slice(0, 3).map((f) => f.etiqueta)).toEqual(['1.º hombre', '2.º hombre', '3.º hombre']);
  });

  it('sin puestos no colorea ninguna fila', () => {
    expect(tabla([fila(null, '1'), fila(null, '2')]).every((f) => !f.clase && f.puesto === '—')).toBe(true);
  });
});
