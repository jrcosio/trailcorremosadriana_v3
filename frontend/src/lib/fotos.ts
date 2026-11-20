import type { CSSProperties } from 'react';

/**
 * Decisión P6 del propietario (feature 012): las fotos se ven siempre completas.
 * Devuelve el estilo con la variable `--foto` (la propia imagen). `ajustes.css` (A-004) la usa
 * como fondo oscurecido del `<img>`, visible solo en el espacio que deja `object-fit: contain`.
 * React la aplica por CSSOM, así que la CSP no la bloquea.
 */
export function fondoFoto(src: string | undefined | null): CSSProperties {
  if (!src) return {};
  const url = src.replace(/["\\\n\r]/g, (c) => encodeURIComponent(c));
  return { '--foto': `url("${url}")` } as CSSProperties;
}
