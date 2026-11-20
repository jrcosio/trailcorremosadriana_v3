import { describe, expect, it } from 'vitest';
import { usuarioInstagram } from '@/lib/contacto';
import { seed } from '@/lib/data';

describe('usuarioInstagram', () => {
  it('con el enlace de la semilla mantiene el texto aprobado', () => {
    expect(usuarioInstagram(seed.settings.instagram)).toBe('@asociacion_penasagra');
  });

  it('se deriva de cualquier enlace de perfil', () => {
    expect(usuarioInstagram('https://instagram.com/otra_cuenta')).toBe('@otra_cuenta');
    expect(usuarioInstagram('https://www.instagram.com/otra.cuenta/?hl=es')).toBe('@otra.cuenta');
  });

  it('sin usuario o con un enlace no válido muestra «Instagram»', () => {
    for (const enlace of ['https://www.instagram.com/', '', 'no es un enlace', undefined]) {
      expect(usuarioInstagram(enlace)).toBe('Instagram');
    }
  });
});
