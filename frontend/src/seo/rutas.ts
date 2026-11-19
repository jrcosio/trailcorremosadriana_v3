/**
 * Metadatos por ruta pública estática.
 * Contrato: specs/001-base-proyecto/contracts/rutas-web.md
 * Los títulos de `/`, `/recorridos`, `/galeria`, `/clasificaciones`, `/reglamento` y `/contacto`
 * conservan los de la web de producción.
 */
export type MetadatosRuta = { titulo: string; descripcion: string };

export const METADATOS_GENERICOS: MetadatosRuta = {
  titulo: 'Trail Peñasagra · Corremos por Adriana',
  descripcion:
    'Montaña, deporte y solidaridad en Cosío, Rionansa. Descubre el Trail Peñasagra, sus recorridos y todas las novedades.',
};

export const RUTAS_PUBLICAS: Record<string, MetadatosRuta> = {
  '/': {
    titulo: 'Trail Sierra de Peñasagra – Corremos por Adriana',
    descripcion:
      'Web oficial del Trail Sierra de Peñasagra – Corremos por Adriana. Carrera solidaria de montaña en Cosío, Rionansa (Cantabria).',
  },
  '/carreras': {
    titulo: 'Carreras y recorridos | Trail Peñasagra',
    descripcion:
      'Trail 27K, Speed Trail 14K y Familiar 7K: distancia, desnivel, avituallamientos y recorrido de cada prueba.',
  },
  '/recorridos': {
    titulo: 'Recorridos | Trail Peñasagra',
    descripcion:
      'Recorridos del Trail Peñasagra: 27K, 14K y marcha familiar de 7K. Perfiles, avituallamientos y material.',
  },
  '/inscripciones': {
    titulo: 'Inscripciones | Trail Peñasagra',
    descripcion: 'Estado de las inscripciones del Trail Peñasagra y acceso al Dorsal Solidario.',
  },
  '/noticias': {
    titulo: 'Noticias | Trail Peñasagra',
    descripcion: 'Novedades y anuncios del Trail Sierra de Peñasagra.',
  },
  '/galeria': {
    titulo: 'Galería | Trail Peñasagra',
    descripcion: 'Galería de fotos de las ediciones del Trail Sierra de Peñasagra.',
  },
  '/clasificaciones': {
    titulo: 'Clasificaciones | Trail Peñasagra',
    descripcion: 'Clasificaciones y resultados oficiales del Trail Sierra de Peñasagra.',
  },
  '/reglamento': {
    titulo: 'Reglamento | Trail Peñasagra',
    descripcion:
      'Reglamento oficial del Trail Sierra de Peñasagra: precios, categorías, material, seguridad y normativa.',
  },
  '/solidaridad': {
    titulo: 'Corremos por Adriana | Trail Peñasagra',
    descripcion: 'Por qué corremos: montaña, deporte y solidaridad. Colabora con el Dorsal Solidario.',
  },
  '/patrocinadores': {
    titulo: 'Patrocinadores y colaboradores | Trail Peñasagra',
    descripcion: 'Empresas e instituciones que hacen posible el Trail Peñasagra.',
  },
  '/contacto': {
    titulo: 'Contacto | Trail Peñasagra',
    descripcion: 'Contacta con la organización del Trail Sierra de Peñasagra.',
  },
};

/** Rutas privadas o de revisión: HTML propio con `noindex`. */
export const RUTAS_NOINDEX = ['/admin', '/pantallas'] as const;

export const IMAGEN_COMPARTIR = '/reused/logos/corremos_por_adriana.webp';
