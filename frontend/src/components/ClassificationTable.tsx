import { useEffect, useMemo, useState } from 'react';
import { etiquetaPodio, rangosPodio, type ClassificationRow } from '@/lib/classifications';

type Columnas = { category: boolean; club: boolean; gender: boolean; status: boolean };
type PaginaServidor = {
  rows: ClassificationRow[]; total: number; filtered: number; page: number; pages: number;
  categories: string[]; genders: string[]; columns: Columnas;
};

/**
 * Tabla de participantes. Con `classificationId` consulta al servidor (búsqueda, filtros y
 * paginación de 50; feature 006). Sin él, filtra en el cliente las `rows` recibidas (vista previa
 * del panel). El marcado es el mismo en ambos modos.
 * Feature 012 · US6 y US10 (decisiones P10 y P12): las filas del podio llevan `podium podium-N`
 * y, junto al nombre, una etiqueta con su puesto en el podio («1.ª mujer»), en oro, plata o bronce
 * (`ajustes.css` A-007). «Pos.» conserva la posición general.
 * - Hay un podio por sexo o, con el filtro de categoría, uno de la categoría.
 * - En modo servidor el puesto llega en `podium`; en modo cliente lo calcula `rangosPodio`.
 * - La búsqueda no cambia el podio.
 */
export default function ClassificationTable({ rows, preview = false, label = 'Clasificación', classificationId }: { rows: ClassificationRow[]; preview?: boolean; label?: string; classificationId?: string }) {
  const [query, setQuery] = useState(''), [category, setCategory] = useState(''), [gender, setGender] = useState(''), [page, setPage] = useState(1);
  const [remota, setRemota] = useState<PaginaServidor | null>(null);
  const servidor = Boolean(classificationId) && !preview;
  useEffect(() => setPage(1), [query, category, gender, rows]);
  useEffect(() => {
    if (!servidor) return;
    const control = new AbortController();
    const temporizador = setTimeout(() => {
      const params = new URLSearchParams({ q: query, categoria: category, sexo: gender, pagina: String(page) });
      fetch(`/api/clasificaciones/${encodeURIComponent(classificationId!)}/participantes?${params}`, { signal: control.signal })
        .then(r => { if (!r.ok) throw Error(); return r.json(); })
        .then((p: PaginaServidor) => setRemota(p))
        .catch(() => {});
    }, query ? 250 : 0);
    return () => { clearTimeout(temporizador); control.abort(); };
  }, [servidor, classificationId, query, category, gender, page]);

  const normalized = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const filtered = servidor ? [] : rows.filter(r => (!category || r.category === category) && (!gender || r.gender === gender) && normalized(`${r.bib} ${r.name} ${r.club}`).includes(normalized(query)));
  const pageSize = preview ? 5 : 50;
  const pages = servidor ? remota?.pages ?? 1 : Math.max(1, Math.ceil(filtered.length / pageSize));
  const current = servidor ? remota?.page ?? 1 : Math.min(page, pages);
  const shown = servidor ? remota?.rows ?? [] : preview ? filtered.slice(0, 5) : filtered.slice((current - 1) * pageSize, current * pageSize);
  const total = servidor ? remota?.filtered ?? 0 : filtered.length;
  const has = (key: keyof Columnas) => (servidor ? Boolean(remota?.columns[key]) : rows.some(r => Boolean(r[key])));
  const categorias = servidor ? remota?.categories ?? [] : [...new Set(rows.map(r => r.category).filter(Boolean))].sort();
  const sexos = servidor ? remota?.genders ?? [] : [...new Set(rows.map(r => r.gender).filter(Boolean))].sort();
  const cargando = servidor && !remota;
  const podioCliente = useMemo(() => (servidor ? new Map<ClassificationRow, number>() : rangosPodio(rows, { category, gender })), [servidor, rows, category, gender]);
  return <div className="classification-table-block">
    {!preview && <div className="filters classification-filters"><label>Buscar participante<input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Nombre, dorsal o club" /></label><label>Categoría<select value={category} onChange={e => setCategory(e.target.value)}><option value="">Todas las categorías</option>{categorias.map(v => <option key={v}>{v}</option>)}</select></label><label>Sexo<select value={gender} onChange={e => setGender(e.target.value)}><option value="">Todos</option>{sexos.map(v => <option key={v}>{v}</option>)}</select></label></div>}
    <div className="classification-scroll" role="region" aria-label={label} tabIndex={0}><table className="classification-table"><caption>{preview ? `Vista previa: primeras ${Math.min(rows.length, 5)} filas de ${rows.length}` : `${total} participantes · ${label}`}</caption><thead><tr><th scope="col">Pos.</th><th scope="col">Dorsal</th><th scope="col">Participante</th><th scope="col">Tiempo</th>{has('category') && <th scope="col">Categoría</th>}{has('club') && <th scope="col">Club</th>}{has('gender') && <th scope="col">Sexo</th>}{has('status') && <th scope="col">Estado</th>}</tr></thead><tbody>{shown.map((r, i) => { const podio = (servidor ? r.podium : podioCliente.get(r)) ?? 0; return <tr key={`${r.bib}-${i}`} className={podio ? `podium podium-${podio}` : undefined}><td className={podio ? 'podium-position' : ''}>{r.position ?? '—'}</td><td>{r.bib}</td><td><strong>{r.name}</strong>{podio ? <>{' '}<span className="podium-label">{etiquetaPodio(podio, r.gender, category)}</span></> : null}</td><td className="result-time">{r.time || '—'}</td>{has('category') && <td>{r.category || '—'}</td>}{has('club') && <td>{r.club || '—'}</td>}{has('gender') && <td>{r.gender || '—'}</td>}{has('status') && <td>{r.status || '—'}</td>}</tr>; })}</tbody></table></div>
    {!shown.length && !cargando && <p className="muted" role="status">No hay participantes para estos filtros.</p>}
    {!preview && pages > 1 && <nav className="classification-pagination" aria-label={`Páginas de ${label}`}><button type="button" className="button secondary" disabled={current <= 1} onClick={() => setPage(current - 1)}>Anterior</button><span aria-live="polite">Página {current} de {pages}</span><button type="button" className="button secondary" disabled={current >= pages} onClick={() => setPage(current + 1)}>Siguiente</button></nav>}
  </div>;
}
