/**
 * Usuario de Instagram que se lee en `/contacto`, derivado del enlace configurado (feature 010,
 * research R7). Con el enlace actual de la asociación da «@asociacion_penasagra», el mismo texto
 * que tenía fijo la propuesta.
 */
export function usuarioInstagram(enlace: string | undefined): string {
  try {
    const usuario = new URL(enlace ?? '').pathname.split('/').filter(Boolean)[0];
    return usuario ? '@' + decodeURIComponent(usuario) : 'Instagram';
  } catch {
    return 'Instagram';
  }
}
