import { describe, expect, it } from 'vitest';
import { fondoFoto } from '@/lib/fotos';

describe('fondoFoto', () => {
  it('devuelve la variable --foto con la URL entre comillas', () => {
    expect(fondoFoto('/reused/img/dorsal_solidario.webp')).toEqual({ '--foto': 'url("/reused/img/dorsal_solidario.webp")' });
    expect(fondoFoto('https://web.example/foto.jpg?a=1&b=2')).toEqual({ '--foto': 'url("https://web.example/foto.jpg?a=1&b=2")' });
  });

  it('escapa comillas, barras invertidas y saltos de línea', () => {
    const valor = (fondoFoto('/x"y\\z\nw') as Record<string, string>)['--foto'];
    expect(valor).toBe('url("/x%22y%5Cz%0Aw")');
    expect(valor.slice(5, -2)).not.toMatch(/["\\\n]/);
  });

  it('sin URL no añade estilo', () => {
    expect(fondoFoto('')).toEqual({});
    expect(fondoFoto(undefined)).toEqual({});
    expect(fondoFoto(null)).toEqual({});
  });
});
