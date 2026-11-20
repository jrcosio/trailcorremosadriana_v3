export const MAX_CSV_BYTES = 1_000_000;
export const MAX_RESULT_ROWS = 5000;
export const resultFields = [
  ['position', 'Posición', true], ['bib', 'Dorsal', true], ['name', 'Nombre', true],
  ['surname', 'Apellidos', false], ['time', 'Tiempo', true], ['category', 'Categoría', false],
  ['club', 'Club', false], ['gender', 'Sexo', false], ['status', 'Estado', false],
] as const;
export type ResultField = typeof resultFields[number][0];
export type ColumnMapping = Partial<Record<ResultField, number>>;
export type ClassificationRow = { position: number | null; bib: string; name: string; time: string; category: string; club: string; gender: string; status: string };
export type CsvTable = { headers: string[]; records: string[][]; delimiter: string };
const normalize = (v: string) => v.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');
const aliases: Record<ResultField, string[]> = {
  position: ['posicion', 'pos', 'puesto', 'posgeneral', 'posiciongeneral', 'puestogeneral', 'clasificacion', 'rank', 'ranking', 'position'],
  bib: ['dorsal', 'numdorsal', 'numerodorsal', 'bib', 'bibnumber', 'numero', 'num'],
  name: ['nombre', 'nombrecompleto', 'nombreyapellidos', 'participante', 'corredor', 'atleta', 'name', 'firstname', 'fullname'],
  surname: ['apellido', 'apellidos', 'surname', 'lastname'],
  time: ['tiempo', 'tiempototal', 'tiempooficial', 'tiempofinal', 'tiemporeal', 'time', 'totaltime', 'finishtime', 'marca', 'meta'],
  category: ['categoria', 'category', 'cat'], club: ['club', 'equipo', 'team'],
  gender: ['sexo', 'genero', 'gender', 'sex'], status: ['estado', 'status', 'situacion'],
};
export function isSolidarityRace(value: { id?: string; title?: string; race?: string; raceId?: string }) {
  return [value.id, value.title, value.race, value.raceId].some(v => /solidari/.test(normalize(String(v || ''))));
}
export function classificationRaces<T extends { id: string; title?: string }>(races: T[]): T[] { return races.filter(r => !isSolidarityRace(r)); }
export function visibleClassifications<T extends { id: string; published?: boolean; rows?: ClassificationRow[]; participants?: number; race?: string; raceId?: string }>(results: T[]): T[] {
  return results.filter(r => r.published && !isSolidarityRace(r) && (r.participants ?? (Array.isArray(r.rows) ? r.rows.length : 0)) > 0);
}
function splitCsv(text: string, delimiter: string): string[][] {
  const rows: string[][] = []; let row: string[] = [], cell = '', quoted = false, closed = false;
  const pushCell = () => { row.push(cell.trim()); cell = ''; closed = false; if (row.length > 60) throw Error('El CSV supera las 60 columnas.'); };
  const pushRow = () => { pushCell(); if (row.some(v => v !== '')) rows.push(row); row = []; if (rows.length > MAX_RESULT_ROWS + 1) throw Error(`Máximo ${MAX_RESULT_ROWS} participantes por CSV.`); };
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else { quoted = false; closed = true; } } else cell += c; continue; }
    if (c === delimiter) { pushCell(); continue; }
    if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; pushRow(); continue; }
    if (c === '"') { if (closed || cell.trim()) throw Error('Comillas incorrectas en el CSV.'); cell = ''; quoted = true; continue; }
    if (closed && c.trim()) throw Error('Hay texto después del cierre de unas comillas.');
    cell += c;
    if (cell.length > 10000) throw Error('Una celda del CSV es demasiado larga.');
  }
  if (quoted) throw Error('Hay comillas sin cerrar en el CSV.');
  if (cell || row.length || closed) pushRow();
  return rows;
}
export function parseCsv(text: string): CsvTable {
  if (text.length > MAX_CSV_BYTES) throw Error('El CSV debe ocupar como máximo 1 MB.');
  text = text.replace(/^\uFEFF/, '');
  const candidates: { rows: string[][]; delimiter: string }[] = []; let failure = '';
  for (const delimiter of [';', ',', '\t']) { try { const rows = splitCsv(text, delimiter); if (rows[0]?.length > 1) candidates.push({ rows, delimiter }); } catch (e) { failure = (e as Error).message; } }
  candidates.sort((a, b) => b.rows[0].length - a.rows[0].length);
  const chosen = candidates[0];
  if (!chosen) throw Error(failure || 'Usa un CSV con cabeceras separado por coma, punto y coma o tabulador.');
  const [headers, ...records] = chosen.rows;
  if (headers.some(h => !h)) throw Error('Todas las columnas deben tener una cabecera.');
  if (!records.length) throw Error('El CSV no contiene participantes.');
  const bad = records.findIndex(r => r.length !== headers.length);
  if (bad !== -1) throw Error(`Fila de datos ${bad + 1}: hay ${records[bad].length} columnas; se esperaban ${headers.length}.`);
  return { headers, records, delimiter: chosen.delimiter };
}
export function guessMapping(headers: string[]): ColumnMapping {
  const map: ColumnMapping = {};
  for (const [field] of resultFields) { const matches = headers.map((h, i) => aliases[field].includes(normalize(h)) ? i : -1).filter(i => i >= 0); if (matches.length === 1) map[field] = matches[0]; }
  return map;
}
export function mapClassification(table: CsvTable, mapping: ColumnMapping): ClassificationRow[] {
  for (const [key, label, required] of resultFields) {
    const index = mapping[key];
    if (required && index === undefined) throw Error(`Selecciona la columna «${label}».`);
    if (index !== undefined && (!Number.isInteger(index) || index < 0 || index >= table.headers.length)) throw Error(`Columna inválida para «${label}».`);
  }
  const selected = Object.values(mapping).filter(v => v !== undefined);
  if (new Set(selected).size !== selected.length) throw Error('Cada campo debe utilizar una columna distinta.');
  const bibs = new Set<string>();
  return table.records.map((record, i) => {
    const read = (key: ResultField) => mapping[key] === undefined ? '' : record[mapping[key]!].replace(/\s+/g, ' ').trim();
    const fail = (message: string): never => { throw Error(`Fila de datos ${i + 1}: ${message}`); };
    const rawPosition = read('position'); const position = /^[1-9]\d*[.ºª]?$/.test(rawPosition) ? parseInt(rawPosition, 10) : null;
    if (position !== null && position > 100000) fail('posición demasiado grande.');
    if (position === null && rawPosition && !/^(?:-|nc|dnf|dns|dsq|dq|ret|retirad[oa]|abandono|no clasificad[oa]|no presentad[oa]|descalificad[oa])$/i.test(rawPosition)) fail('posición inválida. Usa un número, NC, DNF, DNS o DSQ.');
    const bib = read('bib'), name = [read('name'), read('surname')].filter(Boolean).join(' '), time = read('time');
    const status = read('status') || (position === null ? rawPosition : '');
    // Decisión del propietario (P3): el dorsal solo es obligatorio para participantes clasificados.
    if ((position !== null && !bib) || bib.length > 30) fail('el dorsal es obligatorio para los clasificados y admite hasta 30 caracteres.');
    if (bib && bibs.has(bib.toLowerCase())) fail(`el dorsal «${bib}» está repetido.`); if (bib) bibs.add(bib.toLowerCase());
    if (!name || name.length > 200) fail('el nombre es obligatorio y admite hasta 200 caracteres.');
    if (position !== null && !time) fail('falta el tiempo de un participante clasificado.');
    if (position === null && (!status || status === '-')) fail('indica un estado (por ejemplo, DNF) para un participante sin posición.');
    const row = { position, bib, name, time, category: read('category'), club: read('club'), gender: read('gender'), status };
    for (const key of ['category', 'club'] as const) if (row[key].length > 150) fail(`«${key}» admite hasta 150 caracteres.`);
    for (const key of ['time', 'gender', 'status'] as const) if (row[key].length > 60) fail(`«${key}» admite hasta 60 caracteres.`);
    return row;
  }).sort((a, b) => (a.position ?? Infinity) - (b.position ?? Infinity));
}
