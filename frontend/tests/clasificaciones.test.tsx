/**
 * Comprobaciones portadas de la propuesta (scripts/check-classifications.tsx, partes de cliente).
 * Las comprobaciones de esquema y persistencia en servidor pasan a pytest + PostgreSQL en la
 * feature 006.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import {
  classificationRaces,
  guessMapping,
  isSolidarityRace,
  mapClassification,
  parseCsv,
  visibleClassifications,
} from '@/lib/classifications';
import ClassificationTable from '@/components/ClassificationTable';
import ClassificationManager from '@/components/admin/ClassificationManager';
import Results from '@/components/Results';
import { publicData, seed } from '@/lib/data';

const plantilla = readFileSync(fileURLToPath(new URL('../public/templates/clasificacion.csv', import.meta.url)), 'utf8');
const tabla = parseCsv(plantilla);
const mapeo = guessMapping(tabla.headers);
const filas = mapClassification(tabla, mapeo);

describe('Lectura y mapeo de CSV', () => {
  it('importa todos los participantes de la plantilla, incluido el DNF', () => expect(filas).toHaveLength(3));
  it('el DNF no recibe posición inventada', () => expect(filas[2].position).toBeNull());
  it('combina nombre y apellidos', () => expect(filas[0].name).toBe('Participante Ejemplo Uno'));
  it('admite BOM y finales de línea Windows', () =>
    expect(parseCsv('﻿' + plantilla.replace(/\n/g, '\r\n')).records).toHaveLength(3));
  it('CSV con comas, separadores entre comillas, comillas escapadas y orden por puesto', () =>
    expect(
      mapClassification(parseCsv('Rank,Bib,Name,Time\n2,002,"López, Ana",1:23:45\n1,001,"Peña ""Paz""",1:20:00'), {
        position: 0,
        bib: 1,
        name: 2,
        time: 3,
      })[1].name,
    ).toBe('López, Ana'));
  it('CSV separado por tabuladores', () =>
    expect(parseCsv('Puesto\tDorsal\tNombre\tTiempo\n1\t01\tAna\t1:01:01').delimiter).toBe('\t'));
  it('mapeo manual y ceros a la izquierda', () =>
    expect(
      mapClassification(parseCsv('Orden;Número;Atleta;Marca\n1;001;Ana;00:45:03'), { position: 0, bib: 1, name: 2, time: 3 })[0].bib,
    ).toBe('001'));
  it('rechaza un número de columnas incorrecto', () => expect(() => parseCsv('pos;dorsal;nombre;tiempo\n1;2;Ana')).toThrow(/columnas/));
  it('rechaza comillas sin cerrar', () => expect(() => parseCsv('pos;dorsal\n1;"Ana')).toThrow(/comillas/i));
  it('exige las columnas obligatorias', () => expect(() => mapClassification(tabla, {})).toThrow(/Posición/));
  it('una columna de origen por campo', () =>
    expect(() => mapClassification(tabla, { ...mapeo, bib: mapeo.name })).toThrow(/distinta/));
  it('rechaza dorsales repetidos', () =>
    expect(() => mapClassification(parseCsv(plantilla.replace(';102;', ';101;')), mapeo)).toThrow(/repetido/));
  it('un participante clasificado necesita tiempo', () =>
    expect(() => mapClassification(parseCsv(plantilla.replace('01:42:10', '')), mapeo)).toThrow(/tiempo/));
  it('dorsal vacío solo en participantes sin posición (decisión P3)', () => {
    const t = parseCsv('pos;dorsal;nombre;tiempo;estado\n1;1;A;1:00;\n;;B;;Sin salida\n;;C;;Sin salida');
    expect(mapClassification(t, guessMapping(t.headers)).map(r => r.bib)).toEqual(['1', '', '']);
    expect(() => mapClassification(parseCsv('pos;dorsal;nombre;tiempo\n1;;A;1:00'), { position: 0, bib: 1, name: 2, time: 3 })).toThrow(/clasificados/);
  });
  it('límite de tamaño de 1 MB', () => expect(() => parseCsv('x'.repeat(1000001))).toThrow(/1 MB/));
  it('límite de 5000 filas', () => expect(() => parseCsv('pos;dorsal\n' + '1;2\n'.repeat(5001))).toThrow(/5000/));
});

describe('Formato de producción (feature 006)', () => {
  it('detecta «Pos» y «Meta» sin confundir «Pos Categoria» ni «Pos Genero»', () => {
    const t = parseCsv('Pos,Dorsal,Nombre,Apellidos,Categoria,Pos Categoria,Genero,Pos Genero,Club,Meta,Estado\n1,250,Ana,Peña,Senior F,1,Femenino,1,Club,01:19:45,Finalizado');
    expect(guessMapping(t.headers)).toEqual({ position: 0, bib: 1, name: 2, surname: 3, time: 9, category: 4, club: 8, gender: 6, status: 10 });
  });
  it('visibleClassifications acepta el recuento del servidor sin filas', () => {
    expect(visibleClassifications([{ id: 'x', published: true, participants: 3, rows: [] }])).toHaveLength(1);
    expect(visibleClassifications([{ id: 'y', published: true, participants: 0, rows: [] }])).toHaveLength(0);
  });
});

describe('Exclusión del Dorsal Solidario y vista pública', () => {
  const resultado = {
    id: 'classification-test',
    title: 'Clasificación de prueba',
    year: '2026',
    raceId: seed.races[0].id,
    race: seed.races[0].title,
    sourceFile: 'ejemplo.csv',
    importedAt: new Date().toISOString(),
    rows: filas,
    published: true,
  };
  const solidaria = { ...resultado, id: 'solidario', raceId: 'dorsal-solidario', race: 'Dorsal Solidario' };
  const d = structuredClone(seed);
  d.results = [resultado, solidaria, { ...resultado, id: 'draft', published: false }];
  d.races.push({ id: 'dorsal-solidario', title: 'Dorsal Solidario' });

  it('reconoce la modalidad solidaria con mayúsculas y tildes', () =>
    expect(isSolidarityRace({ title: 'DORSAL SOLIDÁRIO' })).toBe(true));
  it('excluye la modalidad solidaria de las carreras elegibles', () =>
    expect(classificationRaces(d.races)).toHaveLength(seed.races.length));
  it('la lista pública excluye la solidaria y los borradores', () => expect(visibleClassifications(d.results)).toHaveLength(1));
  it('publicData filtra la clasificación solidaria', () => expect(publicData(d).results).toHaveLength(1));
  it('la página pública muestra la clasificación (filas desde el servidor) sin la modalidad solidaria', () => {
    const html = renderToStaticMarkup(<Results d={d} />);
    expect(html).toContain('Clasificación de prueba');
    expect(html).toContain('3 participantes');
    expect(html).not.toContain('Dorsal Solidario');
    expect(html).not.toContain('PDF');
  });
  it('la pantalla de alta ofrece CSV y solo carreras competitivas', () => {
    const html = renderToStaticMarkup(<ClassificationManager itemId="nuevo" d={d} save={async () => false} busy={false} />);
    expect(html).toContain('Subir CSV de clasificación');
    expect(html).not.toContain('Dorsal Solidario');
    expect(html).not.toContain('PDF');
  });
  it('/clasificaciones/{año} filtra por el año inicial', () => {
    const html = renderToStaticMarkup(<Results d={d} anio="2025" />);
    expect(html).toContain('No hay resultados para estos filtros.');
    expect(renderToStaticMarkup(<Results d={d} anio="2026" />)).toContain('Clasificación de prueba');
  });
  it('las celdas del CSV se muestran como texto escapado', () => {
    const html = renderToStaticMarkup(<ClassificationTable rows={[{ ...filas[0], name: '<script>alert(1)</script>' }]} />);
    expect(html).not.toContain('<script>alert');
    expect(html).toContain('&lt;script&gt;');
  });
});
