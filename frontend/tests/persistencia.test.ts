import { afterEach, describe, expect, it, vi } from 'vitest';
import { guardarCambios, planificar } from '@/lib/persistencia';
import { seed, type SiteData } from '@/lib/data';

function base(): SiteData {
  const d = structuredClone(seed);
  d.settings.eventVersion = 3;
  d.races = d.races.map((r, i) => ({ ...r, version: i + 1 }));
  return d;
}

describe('planificar', () => {
  it('sin cambios no hay operaciones', () => {
    expect(planificar(base(), base())).toEqual([]);
  });

  it('cambio de fecha → evento con la versión vigente', () => {
    const a = base();
    const s = base();
    s.settings.date = '2027-07-10T07:00:00.000Z';
    expect(planificar(a, s)).toEqual([
      { metodo: 'PUT', url: '/api/admin/evento', cuerpo: { edition: '2027', date: '2027-07-10T07:00:00.000Z', countdown: true, version: 3 } },
    ]);
  });

  it('prueba editada, nueva y borrada', () => {
    const a = base();
    const s = base();
    s.races[0] = { ...s.races[0], km: '28' };
    s.races.push({ id: 'nueva', title: 'Nueva', published: false });
    s.races = s.races.filter((r) => r.id !== 'familiar-7k');
    const ops = planificar(a, s);
    expect(ops).toEqual([
      { metodo: 'PUT', url: '/api/admin/carreras/trail-27k', cuerpo: { ...s.races[0], version: 1 } },
      { metodo: 'PUT', url: '/api/admin/carreras/nueva', cuerpo: { id: 'nueva', title: 'Nueva', published: false, version: 0 } },
      { metodo: 'DELETE', url: '/api/admin/carreras/familiar-7k?version=3' },
    ]);
  });

  it('secciones sin persistencia → PUT /api/content (501 en el servidor)', () => {
    const a = base();
    const s = base();
    s.regulation += '\nNuevo';
    expect(planificar(a, s)).toEqual([{ metodo: 'PUT', url: '/api/content', cuerpo: { data: s, revision: 0 } }]);
  });

  it('inscripciones: enlaces de prueba primero y apertura después', () => {
    const a = base();
    const s = base();
    s.races[0] = { ...s.races[0], registration: 'https://example.com/insc' };
    s.settings.registrationsOpen = true;
    s.settings.solidarityRegistration = 'https://example.com/dorsal';
    expect(planificar(a, s).map((o) => `${o.metodo} ${o.url}`)).toEqual([
      'PUT /api/admin/carreras/trail-27k',
      'PUT /api/admin/inscripciones',
    ]);
    expect(planificar(a, s)[1].cuerpo).toEqual({
      registrationsOpen: true,
      registrationMessage: s.settings.registrationMessage,
      solidarityRegistration: 'https://example.com/dorsal',
      version: 3,
    });
  });

  it('evento e inscripciones juntos encadenan la versión compartida', () => {
    const a = base();
    const s = base();
    s.settings.countdown = false;
    s.settings.registrationMessage = 'Otro';
    const ops = planificar(a, s);
    expect(ops.map((o) => (o.cuerpo as { version: number }).version)).toEqual([3, 4]);
  });

  it('clasificaciones: nueva con importToken, metadatos y borrado', () => {
    const a = base();
    a.results = [{ id: 'c1', title: 'C1', year: '2026', raceId: 'trail-27k', published: true, version: 2, rows: [] }];
    const s = base();
    s.results = [
      { ...a.results[0], published: false },
      { id: 'c2', title: 'C2', year: '2026', raceId: 'speed-14k', published: false, rows: [], importToken: 'tok' },
    ];
    expect(planificar(a, s)).toEqual([
      { metodo: 'PUT', url: '/api/admin/clasificaciones/c1', cuerpo: { title: 'C1', year: '2026', raceId: 'trail-27k', published: false, version: 2 } },
      { metodo: 'PUT', url: '/api/admin/clasificaciones/c2', cuerpo: { title: 'C2', year: '2026', raceId: 'speed-14k', published: false, version: 0, importToken: 'tok' } },
    ]);
    const borrada = base();
    borrada.results = [];
    expect(planificar(a, borrada)).toEqual([{ metodo: 'DELETE', url: '/api/admin/clasificaciones/c1?version=2' }]);
  });

  it('noticias: nueva, editada y borrada', () => {
    const a = base();
    a.news = [{ id: 'n1', title: 'N1', body: 'x', published: true, version: 4 }];
    const s = base();
    s.news = [{ ...a.news[0], title: 'N1 bis' }, { id: 'n2', title: 'N2', body: 'y', published: false }];
    expect(planificar(a, s)).toEqual([
      { metodo: 'PUT', url: '/api/admin/noticias/n1', cuerpo: { ...s.news[0], version: 4 } },
      { metodo: 'PUT', url: '/api/admin/noticias/n2', cuerpo: { ...s.news[1], version: 0 } },
    ]);
    const vacia = base();
    vacia.news = [];
    expect(planificar(a, vacia)).toEqual([{ metodo: 'DELETE', url: '/api/admin/noticias/n1?version=4' }]);
  });

  it('eventVersion no se considera un cambio de contenido', () => {
    const a = base();
    const s = base();
    s.settings.eventVersion = 4;
    expect(planificar(a, s)).toEqual([]);
  });
});

describe('guardarCambios', () => {
  afterEach(() => vi.unstubAllGlobals());

  function servidor(respuestas: Record<string, Response>) {
    const llamadas: string[] = [];
    vi.stubGlobal('document', { cookie: 'penasagra_csrf=tok' });
    vi.stubGlobal('fetch', async (url: string, init: RequestInit) => {
      llamadas.push(`${init.method ?? 'GET'} ${url}`);
      return respuestas[`${init.method ?? 'GET'} ${url}`] ?? new Response('{}', { status: 500 });
    });
    return llamadas;
  }

  it('aplica y relee los datos confirmados', async () => {
    const a = base();
    const s = base();
    s.settings.countdown = false;
    const confirmados = { ...s, settings: { ...s.settings, eventVersion: 4 } };
    const llamadas = servidor({
      'PUT /api/admin/evento': new Response('{}'),
      'GET /api/content?admin=1': new Response(JSON.stringify({ data: confirmados, revision: 0 })),
    });
    const r = await guardarCambios(a, s);
    expect(r).toEqual({ ok: true, datos: confirmados });
    expect(llamadas).toEqual(['PUT /api/admin/evento', 'GET /api/content?admin=1']);
  });

  it('devuelve el primer error con su estado y no relee', async () => {
    const a = base();
    const s = base();
    s.races[0] = { ...s.races[0], km: '30' };
    const llamadas = servidor({
      'PUT /api/admin/carreras/trail-27k': new Response(JSON.stringify({ error: 'Otra persona ha modificado estos datos.' }), { status: 409 }),
    });
    expect(await guardarCambios(a, s)).toEqual({ ok: false, estado: 409, error: 'Otra persona ha modificado estos datos.' });
    expect(llamadas).toEqual(['PUT /api/admin/carreras/trail-27k']);
  });

  it('sin conexión', async () => {
    vi.stubGlobal('document', { cookie: '' });
    vi.stubGlobal('fetch', async () => {
      throw new TypeError('fallo de red');
    });
    const s = base();
    s.settings.countdown = false;
    expect(await guardarCambios(base(), s)).toEqual({ ok: false, estado: 0, error: 'No se puede conectar con el servidor.' });
  });
});
