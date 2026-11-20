import { describe, expect, it } from 'vitest';
import { htmlConMetadatos, plantillaCaddy } from '../plugins/metadatos-rutas';
import { METADATOS_GENERICOS, RUTAS_PUBLICAS } from '@/seo/rutas';

const plantilla =
  '<html><head><title>x</title>\n<meta name="description" content="y" />\n<!-- metadatos-ruta --></head></html>';
const origen = 'https://trail.example';

describe('Metadatos por ruta', () => {
  it('las 11 rutas públicas estáticas tienen títulos distintos', () => {
    const rutas = ['/', '/carreras', '/recorridos', '/inscripciones', '/noticias', '/galeria', '/clasificaciones', '/reglamento', '/solidaridad', '/patrocinadores', '/contacto'];
    expect(Object.keys(RUTAS_PUBLICAS).sort()).toEqual([...rutas].sort());
    const titulos = rutas.map((r) => RUTAS_PUBLICAS[r].titulo);
    expect(new Set(titulos).size).toBe(rutas.length);
  });

  it('conserva los títulos de producción', () => {
    expect(RUTAS_PUBLICAS['/'].titulo).toBe('Trail Sierra de Peñasagra – Corremos por Adriana');
    expect(RUTAS_PUBLICAS['/recorridos'].titulo).toBe('Recorridos | Trail Peñasagra');
    expect(RUTAS_PUBLICAS['/reglamento'].titulo).toBe('Reglamento | Trail Peñasagra');
    expect(RUTAS_PUBLICAS['/contacto'].titulo).toBe('Contacto | Trail Peñasagra');
  });

  it('genera título, descripción, OG con imagen absoluta y canonical', () => {
    const html = htmlConMetadatos(plantilla, RUTAS_PUBLICAS['/reglamento'], { publicOrigin: origen, ruta: '/reglamento' });
    expect(html).toContain('<title>Reglamento | Trail Peñasagra</title>');
    expect(html).toContain(`<meta name="description" content="${RUTAS_PUBLICAS['/reglamento'].descripcion}" />`);
    expect(html).toContain('<meta property="og:image" content="https://trail.example/reused/logos/corremos_por_adriana.webp" />');
    expect(html).toContain('<link rel="canonical" href="https://trail.example/reglamento" />');
    expect(html).not.toContain('noindex');
  });

  it('admin y pantallas llevan noindex', () => {
    const html = htmlConMetadatos(plantilla, METADATOS_GENERICOS, { publicOrigin: origen, noindex: true });
    expect(html).toContain('<meta name="robots" content="noindex, nofollow" />');
  });

  it('escapa caracteres especiales', () => {
    const html = htmlConMetadatos(plantilla, { titulo: 'A "B" <C>', descripcion: 'x & y' }, { publicOrigin: origen });
    expect(html).toContain('<title>A &quot;B&quot; &lt;C&gt;</title>');
    expect(html).toContain('content="x &amp; y"');
  });

  it('plantilla de Caddy: metadatos de la API, 404 y respaldo genérico', () => {
    const html = plantillaCaddy(plantilla, { publicOrigin: origen });
    expect(html).toContain('httpInclude (printf "/api/meta?ruta=%s" (.OriginalReq.URL.Path | urlquery))');
    expect(html).toContain('{{- if eq $meta "no-encontrada" }}{{ httpError 404 }}{{ end -}}');
    expect(html).toContain('{{ if hasPrefix "<!-- meta -->" $meta }}{{ $meta }}{{ else }}');
    // Un solo título y una sola descripción, dentro del respaldo genérico.
    expect(html.match(/<title>/g)).toHaveLength(1);
    expect(html.match(/name="description"/g)).toHaveLength(1);
    const respaldo = html.slice(html.indexOf('{{ else }}'), html.indexOf('{{ end }}'));
    expect(respaldo).toContain(`<title>${METADATOS_GENERICOS.titulo}</title>`);
    expect(respaldo).not.toContain('canonical');
  });

  it('la plantilla rechaza un index.html con «{{»', () => {
    expect(() => plantillaCaddy(plantilla.replace('</head>', '<script>{{x}}</script></head>'), { publicOrigin: origen })).toThrow();
  });
});
