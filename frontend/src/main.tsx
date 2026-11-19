import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import Site from '@/components/Site';
import '@/styles/globals.css';
import '@/styles/ajustes.css';

/** Ruta actual sin barra final (salvo la raíz), tal como la recibía el catch-all de la propuesta. */
export function rutaActual(pathname: string): string {
  const limpia = pathname.replace(/\/+$/, '');
  return limpia === '' ? '/' : limpia;
}

const raiz = document.getElementById('root');
if (raiz) {
  createRoot(raiz).render(
    <StrictMode>
      <Site path={rutaActual(window.location.pathname)} />
    </StrictMode>,
  );
}
