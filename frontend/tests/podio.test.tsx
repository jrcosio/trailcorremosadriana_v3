/**
 * Feature 012 · US6 (decisión P10 del propietario): los tres primeros de una clasificación se
 * distinguen con oro, plata y bronce (clase de fila y medalla con el número).
 */
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import ClassificationTable from '@/components/ClassificationTable';
import type { ClassificationRow } from '@/lib/classifications';

const fila = (position: number | null, bib: string): ClassificationRow =>
  ({ position, bib, name: `Participante ${bib}`, time: position ? '1:00:00' : '', category: '', club: '', gender: '', status: position ? '' : 'Sin salida' }) as ClassificationRow;

/** Filas de la tabla: clase del `<tr>` y contenido de la celda del puesto. */
function filas(rows: ClassificationRow[], preview = false) {
  const html = renderToStaticMarkup(<ClassificationTable rows={rows} preview={preview} label="Prueba" />);
  const cuerpo = html.match(/<tbody>(.*)<\/tbody>/)?.[1] ?? '';
  return [...cuerpo.matchAll(/<tr([^>]*)><td[^>]*>(.*?)<\/td>/g)].map(([, attrs, puesto]) => ({ clase: attrs.match(/class="([^"]*)"/)?.[1] ?? '', puesto }));
}

describe('Clasificaciones: podio (P10)', () => {
  const rows = [fila(1, '19'), fila(2, '7'), fila(3, '31'), fila(3, '44'), fila(4, '2'), fila(12, '80'), fila(null, '90')];

  it('marca con su color y su medalla solo los puestos 1, 2 y 3 (también los empates)', () => {
    expect(filas(rows)).toEqual([
      { clase: 'podium podium-1', puesto: '<span class="podium-medal">1</span>' },
      { clase: 'podium podium-2', puesto: '<span class="podium-medal">2</span>' },
      { clase: 'podium podium-3', puesto: '<span class="podium-medal">3</span>' },
      { clase: 'podium podium-3', puesto: '<span class="podium-medal">3</span>' },
      { clase: '', puesto: '4' },
      { clase: '', puesto: '12' },
      { clase: '', puesto: '—' },
    ]);
  });

  it('la vista previa del panel muestra el podio igual', () => {
    expect(filas(rows, true).slice(0, 3).map((f) => f.clase)).toEqual(['podium podium-1', 'podium podium-2', 'podium podium-3']);
  });

  it('sin puestos no colorea ninguna fila', () => {
    expect(filas([fila(null, '1'), fila(null, '2')]).every((f) => !f.clase && f.puesto === '—')).toBe(true);
  });
});
