/**
 * Persistencia del panel por recursos (transición desde el documento único de la propuesta).
 *
 * `Admin.tsx` guarda siempre un `SiteData` completo. Este módulo compara el estado anterior con el
 * siguiente y envía cada cambio a su recurso en la API. Las secciones que aún no tienen
 * persistencia propia van a `PUT /api/content`, que responde «Esta sección del panel todavía no
 * guarda cambios.» Tras guardar se vuelve a leer la vista privada para mostrar los datos y las
 * versiones confirmados por el servidor.
 *
 * Recursos migrados: evento (feature 004) y pruebas (feature 004).
 */
import { apiFetch } from './api';
import type { Item, SiteData } from './data';

export type Operacion = { metodo: 'PUT' | 'DELETE'; url: string; cuerpo?: unknown };
export type Resultado = { ok: true; datos: SiteData } | { ok: false; estado: number; error: string };

const CAMPOS_EVENTO = ['edition', 'date', 'countdown'] as const;
const CAMPOS_TECNICOS = new Set(['eventVersion']);
const SECCIONES_SIN_PERSISTENCIA = ['news', 'albums', 'results', 'sponsors', 'collaborators', 'regulation'] as const;
const ERROR_GENERICO = 'No se han podido guardar los cambios. Inténtalo de nuevo.';

const igual = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);
const porId = (items: Item[]) => new Map(items.map((i) => [i.id, i]));

export function planificar(anterior: SiteData, siguiente: SiteData): Operacion[] {
  const operaciones: Operacion[] = [];
  const a = anterior.settings;
  const s = siguiente.settings;

  if (CAMPOS_EVENTO.some((k) => !igual(a[k], s[k]))) {
    operaciones.push({
      metodo: 'PUT',
      url: '/api/admin/evento',
      cuerpo: { edition: s.edition, date: s.date ?? '', countdown: !!s.countdown, version: a.eventVersion ?? 0 },
    });
  }

  const previas = porId(anterior.races);
  for (const prueba of siguiente.races) {
    const previa = previas.get(prueba.id);
    if (!previa || !igual(previa, prueba)) {
      operaciones.push({
        metodo: 'PUT',
        url: `/api/admin/carreras/${encodeURIComponent(prueba.id)}`,
        cuerpo: { ...prueba, version: previa?.version ?? 0 },
      });
    }
  }
  const siguientes = new Set(siguiente.races.map((r) => r.id));
  for (const previa of anterior.races) {
    if (!siguientes.has(previa.id)) {
      operaciones.push({
        metodo: 'DELETE',
        url: `/api/admin/carreras/${encodeURIComponent(previa.id)}?version=${previa.version ?? 0}`,
      });
    }
  }

  const ajustesPendientes = new Set([...Object.keys(a), ...Object.keys(s)]);
  const otrosAjustes = [...ajustesPendientes].some(
    (k) => !CAMPOS_EVENTO.includes(k as (typeof CAMPOS_EVENTO)[number]) && !CAMPOS_TECNICOS.has(k) && !igual(a[k], s[k]),
  );
  if (otrosAjustes || SECCIONES_SIN_PERSISTENCIA.some((k) => !igual(anterior[k], siguiente[k]))) {
    operaciones.push({ metodo: 'PUT', url: '/api/content', cuerpo: { data: siguiente, revision: 0 } });
  }
  return operaciones;
}

async function error(respuesta: Response): Promise<Resultado> {
  const cuerpo = await respuesta.json().catch(() => ({}));
  return { ok: false, estado: respuesta.status, error: (cuerpo as { error?: string }).error || ERROR_GENERICO };
}

export async function guardarCambios(anterior: SiteData, siguiente: SiteData): Promise<Resultado> {
  try {
    for (const op of planificar(anterior, siguiente)) {
      const respuesta = await apiFetch(op.url, {
        method: op.metodo,
        headers: op.cuerpo === undefined ? undefined : { 'Content-Type': 'application/json' },
        body: op.cuerpo === undefined ? undefined : JSON.stringify(op.cuerpo),
      });
      if (!respuesta.ok) return error(respuesta);
    }
    const lectura = await apiFetch('/api/content?admin=1');
    if (!lectura.ok) return error(lectura);
    const { data } = (await lectura.json()) as { data: SiteData };
    return { ok: true, datos: data };
  } catch {
    return { ok: false, estado: 0, error: 'No se puede conectar con el servidor.' };
  }
}
