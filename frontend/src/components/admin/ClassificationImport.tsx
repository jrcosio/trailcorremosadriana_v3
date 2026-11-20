import { useEffect, useState } from 'react';
import { Upload, Check, X } from 'lucide-react';
import { guessMapping, mapClassification, MAX_CSV_BYTES, parseCsv, resultFields, type ClassificationRow, type ColumnMapping, type CsvTable } from '@/lib/classifications';
import ClassificationTable from '@/components/ClassificationTable';
import { apiFetch } from '@/lib/api';
type ImportValue = { rows: ClassificationRow[]; sourceFile: string; importedAt: string; importToken?: string };
/** Datos de la clasificación que se edita, necesarios para la validación del servidor (feature 006). */
export type ContextoImportacion = { raceId: string; year: string; id?: string };
export default function ClassificationImport({ value, onChange, onError, onPendingChange, contexto }: { value: ImportValue; onChange: (v: ImportValue) => void; onError: (v: string) => void; onPendingChange: (v: boolean) => void; contexto?: ContextoImportacion }) {
  const [pending, setPending] = useState<{ table: CsvTable; fileName: string; mapping: ColumnMapping; text: string } | null>(null), [busy, setBusy] = useState(false);
  async function confirmar(rows: ClassificationRow[]) {
    if (!pending) return;
    if (!contexto?.raceId) { onError('Selecciona la carrera antes de usar los resultados.'); return; }
    setBusy(true); onError('');
    try {
      // Validación definitiva en el servidor: prepara la importación ligada a la sesión.
      const r = await apiFetch('/api/admin/clasificaciones/vista-previa', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ csv: pending.text, mapping: pending.mapping, sourceFile: pending.fileName, raceId: contexto.raceId, year: contexto.year, id: contexto.id }) });
      const j: any = await r.json().catch(() => ({}));
      if (!r.ok) throw Error(j.error || 'No se ha podido validar el CSV.');
      onChange({ rows, sourceFile: pending.fileName, importedAt: new Date().toISOString(), importToken: j.token }); setPending(null);
    } catch (e) { onError((e as Error).message); } finally { setBusy(false); }
  }
  useEffect(() => onPendingChange(Boolean(pending) || busy), [pending, busy, onPendingChange]);
  async function read(file?: File) {
    if (!file) return;
    setPending(null); onError(''); setBusy(true);
    try {
      if (!file.name.toLowerCase().endsWith('.csv')) throw Error('Selecciona un archivo CSV.');
      if (file.size > MAX_CSV_BYTES) throw Error('El CSV debe ocupar como máximo 1 MB.');
      const bytes = await file.arrayBuffer(); let text: string;
      try { text = new TextDecoder('utf-8', { fatal: true }).decode(bytes); } catch { text = new TextDecoder('windows-1252').decode(bytes); }
      const table = parseCsv(text); setPending({ table, fileName: file.name.slice(0, 255), mapping: guessMapping(table.headers), text });
    } catch (e) { onError((e as Error).message); } finally { setBusy(false); }
  }
  let preview: ClassificationRow[] = [], validation = '';
  if (pending) { try { preview = mapClassification(pending.table, pending.mapping); } catch (e) { validation = (e as Error).message; } }
  return <section className="classification-import wide" aria-label="Importar clasificación CSV"><h3>Resultados desde CSV</h3><p>Importa un archivo por carrera y edición. Revisa las columnas antes de guardar.</p>
    <a className="text-link" href="/templates/clasificacion.csv" download>Descargar plantilla CSV</a>
    <label className="upload-zone csv-upload"><Upload size={24} /><strong>{busy ? 'Leyendo CSV…' : value.rows.length ? 'Seleccionar otro CSV' : 'Seleccionar CSV de la carrera'}</strong><small>CSV · Coma, punto y coma o tabulador · Máximo 1 MB y 5.000 participantes</small><input type="file" accept=".csv,text/csv" aria-label="Subir CSV de clasificación" disabled={busy} onChange={e => { const file = e.target.files?.[0]; e.target.value = ''; void read(file); }} /></label>
    {pending && <div className="csv-pending"><h4>{pending.fileName} · {pending.table.records.length} filas</h4><p>Relaciona cada campo con su columna. Los campos con * son obligatorios. Las columnas no seleccionadas no se importan.</p><div className="csv-mapping">{resultFields.map(([key, label, required]) => <label key={key}>{label}{required ? ' *' : ''}<select value={pending.mapping[key] ?? ''} onChange={e => { const mapping = { ...pending.mapping }; if (e.target.value === '') delete mapping[key]; else mapping[key] = Number(e.target.value); setPending({ ...pending, mapping }); }}><option value="">{required ? 'Selecciona una columna' : 'No importar'}</option>{pending.table.headers.map((header, i) => <option key={i} value={i}>{header} · columna {i + 1}</option>)}</select></label>)}</div>{validation ? <p role="alert" className="error-message">{validation}</p> : <ClassificationTable rows={preview} preview label="Vista previa del CSV" />}<div className="csv-actions"><button className="button" type="button" disabled={Boolean(validation) || !preview.length || busy} onClick={() => void confirmar(preview)}><Check size={17} /> Usar estos resultados</button><button className="button secondary" type="button" onClick={() => { setPending(null); onError(''); }}><X size={17} /> Cancelar importación</button></div></div>}
    {!pending && value.rows.length > 0 && <div className="csv-current"><p className="success-message"><Check size={17} /> {value.sourceFile} · {value.rows.length} participantes preparados</p><ClassificationTable rows={value.rows} preview label="Resultados preparados" /><p className="form-help">Pulsa «Guardar cambios» para guardar esta clasificación. Sustituir el CSV reemplaza todos sus participantes.</p></div>}
  </section>;
}
