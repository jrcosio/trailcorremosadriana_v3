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

/**
 * Si el servidor respondió 404 (`404.html` lleva la marca `estado-pagina`), se muestra «no
 * encontrada» aunque la ruta exista en el SPA; por ejemplo, `/pantallas` retirada en producción
 * (decisión P5). Cualquier ruta desconocida para `Site` muestra esa página.
 */
export function rutaInicial(pathname: string, documento: Pick<Document, 'querySelector'>): string {
  const noEncontrada = documento.querySelector('meta[name="estado-pagina"]')?.getAttribute('content') === '404';
  return noEncontrada ? '/no-encontrada' : rutaActual(pathname);
}

const raiz = document.getElementById('root');
if (raiz) {
  createRoot(raiz).render(
    <StrictMode>
      <Site path={rutaInicial(window.location.pathname, document)} />
    </StrictMode>,
  );
}
