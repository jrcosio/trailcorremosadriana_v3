export function isRegistrationUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' && !url.username && !url.password;
  } catch {
    return false;
  }
}

export function solidarityRegistration(settings: { registrationsOpen?: boolean; solidarityRegistration?: string }) {
  const url = typeof settings.solidarityRegistration === 'string' ? settings.solidarityRegistration.trim() : '';
  const available = settings.registrationsOpen === true && isRegistrationUrl(url);
  return {
    available,
    href: available ? url : undefined,
    label: available ? 'Pagar dorsal solidario' : 'Próximamente disponible',
    message: available
      ? 'Completa el pago en la web oficial de inscripciones.'
      : settings.registrationsOpen
        ? 'Pronto estará disponible el enlace para conseguir tu dorsal solidario.'
        : 'Disponible cuando se abran las inscripciones.',
  };
}
