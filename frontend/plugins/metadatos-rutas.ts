/**
 * Plugin de Vite: genera un HTML por ruta pública estática con sus metadatos
 * (título, descripción, Open Graph, Twitter y canonical), además de `app.html`
 * (genérico para rutas dinámicas) y los HTML con `noindex` de /admin y /pantallas.
 * Caddy elige el archivo según la ruta (infra/caddy/Caddyfile).
 */
import type { Plugin } from 'vite';
import {
  IMAGEN_COMPARTIR,
  METADATOS_GENERICOS,
  RUTAS_NOINDEX,
  RUTAS_PUBLICAS,
  type MetadatosRuta,
} from '../src/seo/rutas';

const MARCA = '<!-- metadatos-ruta -->';

const escapar = (valor: string) =>
  valor.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function htmlConMetadatos(
  plantilla: string,
  meta: MetadatosRuta,
  opciones: { publicOrigin: string; ruta?: string; noindex?: boolean },
): string {
  const origen = opciones.publicOrigin.replace(/\/+$/, '');
  const titulo = escapar(meta.titulo);
  const descripcion = escapar(meta.descripcion);
  const imagen = escapar(origen + IMAGEN_COMPARTIR);
  const etiquetas = [
    `<meta property="og:type" content="website" />`,
    `<meta property="og:site_name" content="Trail Peñasagra" />`,
    `<meta property="og:locale" content="es_ES" />`,
    `<meta property="og:title" content="${titulo}" />`,
    `<meta property="og:description" content="${descripcion}" />`,
    `<meta property="og:image" content="${imagen}" />`,
    `<meta name="twitter:card" content="summary_large_image" />`,
    `<meta name="twitter:title" content="${titulo}" />`,
    `<meta name="twitter:description" content="${descripcion}" />`,
    `<meta name="twitter:image" content="${imagen}" />`,
  ];
  if (opciones.ruta) {
    const url = escapar(origen + (opciones.ruta === '/' ? '/' : opciones.ruta));
    etiquetas.push(`<meta property="og:url" content="${url}" />`, `<link rel="canonical" href="${url}" />`);
  }
  if (opciones.noindex) etiquetas.push(`<meta name="robots" content="noindex, nofollow" />`);

  if (!plantilla.includes(MARCA)) throw new Error(`index.html no contiene la marca ${MARCA}`);
  return plantilla
    .replace(/<title>[^<]*<\/title>/, `<title>${titulo}</title>`)
    .replace(/<meta name="description" content="[^"]*" \/>/, `<meta name="description" content="${descripcion}" />`)
    .replace(MARCA, etiquetas.join('\n    '));
}

export function metadatosRutas({ publicOrigin }: { publicOrigin: string }): Plugin {
  return {
    name: 'metadatos-rutas',
    apply: 'build',
    enforce: 'post',
    generateBundle(_, bundle) {
      const indice = bundle['index.html'];
      if (!indice || indice.type !== 'asset') throw new Error('No se encontró index.html en el bundle');
      const plantilla = String(indice.source);

      for (const [ruta, meta] of Object.entries(RUTAS_PUBLICAS)) {
        const html = htmlConMetadatos(plantilla, meta, { publicOrigin, ruta });
        if (ruta === '/') indice.source = html;
        else this.emitFile({ type: 'asset', fileName: `${ruta.slice(1)}/index.html`, source: html });
      }
      this.emitFile({
        type: 'asset',
        fileName: 'app.html',
        source: htmlConMetadatos(plantilla, METADATOS_GENERICOS, { publicOrigin }),
      });
      for (const ruta of RUTAS_NOINDEX) {
        this.emitFile({
          type: 'asset',
          fileName: `${ruta.slice(1)}/index.html`,
          source: htmlConMetadatos(plantilla, METADATOS_GENERICOS, { publicOrigin, noindex: true }),
        });
      }
    },
  };
}
