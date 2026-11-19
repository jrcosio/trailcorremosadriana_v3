/**
 * Comprobaciones portadas de la propuesta (scripts/check-solidarity.tsx, partes de cliente).
 * Las comprobaciones de servidor (guardar, rechazar URLs inseguras, abrir sin destino) se
 * reimplementan contra FastAPI + PostgreSQL en la feature 005.
 */
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { solidarityRegistration } from '@/lib/registration';
import DorsalSolidario from '@/components/DorsalSolidario';
import { seed } from '@/lib/data';

const destino = 'https://example.com/inscripciones?modalidad=dorsal-solidario';

describe('Dorsal Solidario: disponibilidad del pago', () => {
  const casos = [
    [false, '', false],
    [false, destino, false],
    [true, '', false],
    [true, destino, true],
    [true, 'javascript:alert(1)', false],
  ] as const;

  it.each(casos)('abiertas=%s url=%s → disponible=%s', (abiertas, url, disponible) => {
    const r = solidarityRegistration({ registrationsOpen: abiertas, solidarityRegistration: url });
    expect(r.available).toBe(disponible);
    expect(r.href).toBe(disponible ? destino : undefined);
  });

  it('rechaza URLs con credenciales o sin HTTPS', () => {
    for (const url of ['http://example.com/pago', 'https://usuario:clave@example.com/pago', 'ftp://example.com']) {
      expect(solidarityRegistration({ registrationsOpen: true, solidarityRegistration: url }).available).toBe(false);
    }
  });

  it('mensajes según el estado', () => {
    expect(solidarityRegistration({ registrationsOpen: false }).label).toBe('Próximamente disponible');
    expect(solidarityRegistration({ registrationsOpen: false }).message).toBe('Disponible cuando se abran las inscripciones.');
    expect(solidarityRegistration({ registrationsOpen: true }).message).toMatch(/Pronto estará disponible/);
    expect(solidarityRegistration({ registrationsOpen: true, solidarityRegistration: destino }).label).toBe(
      'Pagar dorsal solidario',
    );
  });
});

describe.each(['banner', 'card'] as const)('Componente DorsalSolidario (%s)', (variante) => {
  it('con inscripciones abiertas enlaza directamente al pago externo', () => {
    const html = renderToStaticMarkup(
      <DorsalSolidario variant={variante} settings={{ ...seed.settings, registrationsOpen: true, solidarityRegistration: destino }} />,
    );
    expect(html).toContain('Pagar dorsal solidario');
    expect(html).toContain(`href="${destino}"`);
    expect(html).toContain('target="_blank"');
  });

  it('cerradas: sin enlace de pago ni desvío a otra página', () => {
    const html = renderToStaticMarkup(
      <DorsalSolidario variant={variante} settings={{ ...seed.settings, registrationsOpen: false, solidarityRegistration: destino }} />,
    );
    expect(html).toContain('disabled');
    expect(html).not.toContain('href=');
    expect(html).not.toContain('/contacto');
  });
});
