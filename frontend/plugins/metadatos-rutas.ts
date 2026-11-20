/**
 * Plugin de Vite: genera un HTML por ruta pública estática con sus metadatos
 * (título, descripción, Open Graph, Twitter y canonical), además de `app.html`
 * (genérico), los HTML con `noindex` de /admin y /pantallas y, desde la feature 011:
 * - `plantilla.html`: plantilla de Caddy para detalles y rutas desconocidas. Pide a la API los
 *   metadatos del detalle (`/api/meta`), responde 404 si no existe y usa los genéricos si la API
 *   no responde (specs/011-cierre/research.md R1).
 * - `404.html`: página «no encontrada» (noindex) que Caddy sirve con estado 404.
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
export const MARCADOR_META = '<!-- meta -->';
export const METADATOS_404: MetadatosRuta = {
  titulo: 'Página no encontrada | Trail Peñasagra',
  descripcion: 'La página no existe o todavía no está publicada.',
};

const escapar = (valor: string) =>
  valor.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

type OpcionesMetadatos = { publicOrigin: string; ruta?: string; noindex?: boolean };

/** Etiquetas Open Graph, Twitter, canonical y robots (sin título ni descripción). */
function etiquetasExtra(meta: MetadatosRuta, opciones: OpcionesMetadatos): string[] {
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
  return etiquetas;
}

const TITULO = /<title>[^<]*<\/title>/;
const DESCRIPCION = /<meta name="description" content="[^"]*" \/>/;

export function htmlConMetadatos(plantilla: string, meta: MetadatosRuta, opciones: OpcionesMetadatos): string {
  if (!plantilla.includes(MARCA)) throw new Error(`index.html no contiene la marca ${MARCA}`);
  return plantilla
    .replace(TITULO, `<title>${escapar(meta.titulo)}</title>`)
    .replace(DESCRIPCION, `<meta name="description" content="${escapar(meta.descripcion)}" />`)
    .replace(MARCA, etiquetasExtra(meta, opciones).join('\n    '));
}

/**
 * Plantilla de Caddy (`templates`, specs/011-cierre/research.md R1). Pide los metadatos a
 * `/api/meta`: «no-encontrada» → 404 real; respuesta con el marcador → se inserta; cualquier otra
 * (API caída) → metadatos genéricos.
 */
export function plantillaCaddy(plantilla: string, opciones: { publicOrigin: string }): string {
  if (!plantilla.includes(MARCA)) throw new Error(`index.html no contiene la marca ${MARCA}`);
  if (!TITULO.test(plantilla) || !DESCRIPCION.test(plantilla)) throw new Error('index.html sin título o descripción');
  const base = plantilla.replace(new RegExp(TITULO.source + '\\s*'), '').replace(new RegExp(DESCRIPCION.source + '\\s*'), '');
  if (base.includes('{{')) throw new Error('index.html no puede contener «{{» (plantillas de Caddy)');
  const generico = [
    `<title>${escapar(METADATOS_GENERICOS.titulo)}</title>`,
    `<meta name="description" content="${escapar(METADATOS_GENERICOS.descripcion)}" />`,
    ...etiquetasExtra(METADATOS_GENERICOS, opciones),
  ].join('\n    ');
  const bloque = [
    '{{- $meta := httpInclude (printf "/api/meta?ruta=%s" (.OriginalReq.URL.Path | urlquery)) -}}',
    '{{- if eq $meta "no-encontrada" }}{{ httpError 404 }}{{ end -}}',
    `{{ if hasPrefix "${MARCADOR_META}" $meta }}{{ $meta }}{{ else }}`,
    generico,
    '{{ end }}',
  ].join('\n    ');
  return base.replace(MARCA, bloque);
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
      this.emitFile({ type: 'asset', fileName: 'plantilla.html', source: plantillaCaddy(plantilla, { publicOrigin }) });
      this.emitFile({
        type: 'asset',
        fileName: '404.html',
        source: htmlConMetadatos(plantilla, METADATOS_404, { publicOrigin, noindex: true }),
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
