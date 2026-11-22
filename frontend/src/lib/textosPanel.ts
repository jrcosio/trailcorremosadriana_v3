/**
 * Feature 012 · US11 (decisión P13): textos del panel que dependen de la sección. Usan el nombre
 * de cada lista y de cada elemento con tilde, y su artículo y género. Ya no salen del nombre
 * interno de la sección (`galeria`) ni de un nombre sin artículo («Añade noticia y publícalo»).
 */
type Seccion = { lista: string; elemento: string; femenino: boolean };

const SECCIONES: Record<string, Seccion> = {
  noticias: { lista: 'noticias', elemento: 'noticia', femenino: true },
  clasificaciones: { lista: 'clasificaciones', elemento: 'clasificación', femenino: true },
  galeria: { lista: 'galería', elemento: 'álbum', femenino: false },
  recorridos: { lista: 'recorridos', elemento: 'prueba', femenino: true },
  patrocinadores: { lista: 'patrocinadores', elemento: 'patrocinador', femenino: false },
  colaboradores: { lista: 'colaboradores', elemento: 'colaborador', femenino: false },
};

const seccion = (s: string): Seccion => SECCIONES[s] ?? { lista: s, elemento: s, femenino: false };

/** Nombre de un elemento de la sección: «noticia», «álbum», «prueba»… */
export const nombreElemento = (s: string) => seccion(s).elemento;

/** Nombre de la lista, para el buscador y el enlace de vuelta: «Buscar galería…», «Volver a galería». */
export const nombreLista = (s: string) => seccion(s).lista;

/** Título del bloque del formulario: «Información de la noticia», «Información del álbum». */
export const informacionDe = (s: string) => {
  const { elemento, femenino } = seccion(s);
  return `Información ${femenino ? 'de la' : 'del'} ${elemento}`;
};

/** Invitación de la lista vacía: «Añade una noticia y publícala cuando esté lista.». */
export const invitacionVacia = (s: string) => {
  const { elemento, femenino } = seccion(s);
  return femenino
    ? `Añade una ${elemento} y publícala cuando esté lista.`
    : `Añade un ${elemento} y publícalo cuando esté listo.`;
};

/** Nombre accesible de un campo de subida: «Subir imagen de portada», con la etiqueta en minúscula. */
export const etiquetaSubida = (etiqueta: string) => `Subir ${etiqueta.charAt(0).toLowerCase()}${etiqueta.slice(1)}`;
