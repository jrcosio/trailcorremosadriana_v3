/**
 * Persistencia del panel por recursos (transición desde el documento único de la propuesta).
 *
 * `Admin.tsx` guarda siempre un `SiteData` completo. Este módulo compara el estado anterior con el
 * siguiente y envía cada cambio a su recurso en la API. Las secciones que aún no tienen
 * persistencia propia van a `PUT /api/content`, que responde «Esta sección del panel todavía no
 * guarda cambios.» Tras guardar se vuelve a leer la vista privada para mostrar los datos y las
 * versiones confirmados por el servidor.
 *
 * Recursos migrados: evento y pruebas (004), inscripciones y Dorsal Solidario (005), clasificaciones
 * (006), noticias (007). Orden: pruebas → evento → inscripciones → clasificaciones → resto (un enlace o una ficha de
 * prueba nueva deben existir antes de abrir inscripciones o clasificar).
 */
import { apiFetch } from './api';
import type { Item, SiteData } from './data';

export type Operacion = { metodo: 'PUT' | 'DELETE'; url: string; cuerpo?: unknown };
export type Resultado = { ok: true; datos: SiteData } | { ok: false; estado: number; error: string };

const CAMPOS_EVENTO = ['edition', 'date', 'countdown'] as const;
const CAMPOS_INSCRIPCION = ['registrationsOpen', 'registrationMessage', 'solidarityRegistration'] as const;
const CAMPOS_MIGRADOS = new Set<string>([...CAMPOS_EVENTO, ...CAMPOS_INSCRIPCION]);
const CAMPOS_TECNICOS = new Set(['eventVersion']);
const SECCIONES_SIN_PERSISTENCIA = ['albums', 'sponsors', 'collaborators', 'regulation'] as const;
const ERROR_GENERICO = 'No se han podido guardar los cambios. Inténtalo de nuevo.';

const igual = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);
const porId = (items: Item[]) => new Map(items.map((i) => [i.id, i]));

/** Colección con PUT/DELETE por id y control de versión (noticias y siguientes features). */
function recursoSimple(operaciones: Operacion[], anteriores: Item[], siguientes: Item[], url: string) {
  const previas = porId(anteriores);
  for (const item of siguientes) {
    const previa = previas.get(item.id);
    if (!previa || !igual(previa, item)) {
      operaciones.push({ metodo: 'PUT', url: `${url}/${encodeURIComponent(item.id)}`, cuerpo: { ...item, version: previa?.version ?? 0 } });
    }
  }
  const ids = new Set(siguientes.map((i) => i.id));
  for (const previa of anteriores) {
    if (!ids.has(previa.id)) operaciones.push({ metodo: 'DELETE', url: `${url}/${encodeURIComponent(previa.id)}?version=${previa.version ?? 0}` });
  }
}

export function planificar(anterior: SiteData, siguiente: SiteData): Operacion[] {
  const operaciones: Operacion[] = [];
  const a = anterior.settings;
  const s = siguiente.settings;

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

  let version = a.eventVersion ?? 0;
  if (CAMPOS_EVENTO.some((k) => !igual(a[k], s[k]))) {
    operaciones.push({
      metodo: 'PUT',
      url: '/api/admin/evento',
      cuerpo: { edition: s.edition, date: s.date ?? '', countdown: !!s.countdown, version },
    });
    version += 1; // evento e inscripciones comparten la versión de la edición
  }
  if (CAMPOS_INSCRIPCION.some((k) => !igual(a[k], s[k]))) {
    operaciones.push({
      metodo: 'PUT',
      url: '/api/admin/inscripciones',
      cuerpo: {
        registrationsOpen: !!s.registrationsOpen,
        registrationMessage: s.registrationMessage ?? '',
        solidarityRegistration: s.solidarityRegistration ?? '',
        version,
      },
    });
  }

  const clasificacionesPrevias = porId(anterior.results);
  for (const c of siguiente.results) {
    const previa = clasificacionesPrevias.get(c.id);
    if (!previa || !igual(previa, c)) {
      const cuerpo: Record<string, unknown> = { title: c.title, year: c.year, raceId: c.raceId, published: !!c.published, version: previa?.version ?? 0 };
      if (c.importToken) cuerpo.importToken = c.importToken;
      operaciones.push({ metodo: 'PUT', url: `/api/admin/clasificaciones/${encodeURIComponent(c.id)}`, cuerpo });
    }
  }
  const clasificacionesSiguientes = new Set(siguiente.results.map((c) => c.id));
  for (const previa of anterior.results) {
    if (!clasificacionesSiguientes.has(previa.id)) {
      operaciones.push({ metodo: 'DELETE', url: `/api/admin/clasificaciones/${encodeURIComponent(previa.id)}?version=${previa.version ?? 0}` });
    }
  }

  recursoSimple(operaciones, anterior.news, siguiente.news, '/api/admin/noticias');

  const ajustesPendientes = new Set([...Object.keys(a), ...Object.keys(s)]);
  const otrosAjustes = [...ajustesPendientes].some(
    (k) => !CAMPOS_MIGRADOS.has(k) && !CAMPOS_TECNICOS.has(k) && !igual(a[k], s[k]),
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
