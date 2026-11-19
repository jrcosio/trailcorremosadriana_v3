import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiFetch, leerCookie } from '@/lib/api';

describe('leerCookie', () => {
  it('lee el valor de una cookie concreta', () => {
    expect(leerCookie('penasagra_csrf', 'a=1; penasagra_csrf=abc-_123; b=2')).toBe('abc-_123');
  });
  it('devuelve vacío si no existe', () => {
    expect(leerCookie('penasagra_csrf', 'a=1')).toBe('');
  });
  it('no confunde prefijos', () => {
    expect(leerCookie('csrf', 'penasagra_csrf=x')).toBe('');
  });
});

describe('apiFetch', () => {
  afterEach(() => vi.unstubAllGlobals());

  function preparar(cookie: string) {
    const llamadas: { url: string; init: RequestInit }[] = [];
    vi.stubGlobal('document', { cookie });
    vi.stubGlobal('fetch', async (url: string, init: RequestInit) => {
      llamadas.push({ url, init });
      return new Response('{}');
    });
    return llamadas;
  }

  it('añade X-CSRF-Token en escrituras', async () => {
    const llamadas = preparar('penasagra_csrf=tok');
    for (const method of ['POST', 'PUT', 'PATCH', 'DELETE', 'post']) await apiFetch('/api/x', { method });
    for (const { init } of llamadas) {
      expect(new Headers(init.headers).get('X-CSRF-Token')).toBe('tok');
      expect(init.credentials).toBe('same-origin');
    }
  });

  it('no lo añade en lecturas', async () => {
    const llamadas = preparar('penasagra_csrf=tok');
    await apiFetch('/api/session');
    await apiFetch('/api/content', { method: 'HEAD' });
    for (const { init } of llamadas) expect(new Headers(init.headers).has('X-CSRF-Token')).toBe(false);
  });

  it('conserva las cabeceras y el cuerpo originales', async () => {
    const llamadas = preparar('penasagra_csrf=tok');
    await apiFetch('/api/content', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: '{"a":1}' });
    const cabeceras = new Headers(llamadas[0].init.headers);
    expect(cabeceras.get('Content-Type')).toBe('application/json');
    expect(llamadas[0].init.body).toBe('{"a":1}');
  });
});
