/**
 * Llamadas a la API del panel con protección CSRF de doble envío (feature 002).
 * El servidor emite la cookie legible `penasagra_csrf`; toda escritura debe devolverla en la
 * cabecera `X-CSRF-Token`. La cookie de sesión es HttpOnly y viaja sola (mismo origen).
 */
export const COOKIE_CSRF = 'penasagra_csrf';
export const CABECERA_CSRF = 'X-CSRF-Token';
const METODOS_SEGUROS = new Set(['GET', 'HEAD', 'OPTIONS']);

export function leerCookie(nombre: string, cookies: string = typeof document === 'undefined' ? '' : document.cookie): string {
  for (const parte of cookies.split(';')) {
    const [clave, ...valor] = parte.trim().split('=');
    if (clave === nombre) return decodeURIComponent(valor.join('='));
  }
  return '';
}

export function apiFetch(url: string, init: RequestInit = {}): Promise<Response> {
  const metodo = (init.method ?? 'GET').toUpperCase();
  const cabeceras = new Headers(init.headers);
  if (!METODOS_SEGUROS.has(metodo)) {
    const token = leerCookie(COOKIE_CSRF);
    if (token) cabeceras.set(CABECERA_CSRF, token);
  }
  return fetch(url, { ...init, headers: cabeceras, credentials: 'same-origin' });
}
