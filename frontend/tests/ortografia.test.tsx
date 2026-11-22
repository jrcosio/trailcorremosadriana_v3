/**
 * Feature 012 · US11 (decisión P13 del propietario): «PEÑASAGRA» con Ñ y textos bien escritos.
 * Cubre los errores que encontró la revisión ortográfica (research.md R11), para que no vuelvan.
 */
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import Site from '@/components/Site';
import { mapClassification, parseCsv } from '@/lib/classifications';
import { etiquetaSubida, informacionDe, invitacionVacia, nombreLista } from '@/lib/textosPanel';

describe('Portada: título (FR-032)', () => {
  it('dice «TRAIL» y «PEÑASAGRA», con Ñ, en dos líneas', () => {
    const html = renderToStaticMarkup(<Site path="/" />);
    expect(html).toContain('<h1>TRAIL<br/><em>PEÑASAGRA</em></h1>');
    expect(html).not.toContain('PENASAGRA');
  });
});

describe('Contacto: textos de ayuda (FR-036)', () => {
  it('las preguntas llevan los signos de apertura y cierre', () => {
    const html = renderToStaticMarkup(<Site path="/contacto" />);
    expect(html).toContain('placeholder="¿Cómo te llamas?"');
    expect(html).toContain('placeholder="¿Sobre qué quieres hablar?"');
  });
});

describe('Panel: textos que dependen de la sección (FR-033)', () => {
  it.each([
    ['noticias', 'noticias', 'Información de la noticia', 'Añade una noticia y publícala cuando esté lista.'],
    ['galeria', 'galería', 'Información del álbum', 'Añade un álbum y publícalo cuando esté listo.'],
    ['recorridos', 'recorridos', 'Información de la prueba', 'Añade una prueba y publícala cuando esté lista.'],
    ['patrocinadores', 'patrocinadores', 'Información del patrocinador', 'Añade un patrocinador y publícalo cuando esté listo.'],
    ['colaboradores', 'colaboradores', 'Información del colaborador', 'Añade un colaborador y publícalo cuando esté listo.'],
  ])('%s', (seccion, lista, informacion, invitacion) => {
    expect(nombreLista(seccion)).toBe(lista);
    expect(informacionDe(seccion)).toBe(informacion);
    expect(invitacionVacia(seccion)).toBe(invitacion);
  });
});

describe('Panel: nombre accesible de las subidas (FR-034)', () => {
  it.each([
    ['Imagen de portada', 'Subir imagen de portada'],
    ['Fotografías del álbum', 'Subir fotografías del álbum'],
    ['Fotografía de la prueba', 'Subir fotografía de la prueba'],
    ['Logotipo', 'Subir logotipo'],
    ['Track GPX', 'Subir track GPX'],
  ])('«%s» → «%s»', (etiqueta, nombre) => {
    expect(etiquetaSubida(etiqueta)).toBe(nombre);
  });
});

describe('CSV: errores de longitud con el campo en español (FR-035)', () => {
  const CABECERA = 'posicion;dorsal;nombre;tiempo;categoria;club;sexo;estado';
  const fila = (celdas: Partial<Record<'categoria' | 'club' | 'tiempo' | 'sexo' | 'estado', string>>) =>
    `1;101;Ana;${celdas.tiempo ?? '1:00:00'};${celdas.categoria ?? 'Senior F'};${celdas.club ?? ''};${celdas.sexo ?? 'F'};${celdas.estado ?? ''}`;
  const error = (texto: string) => {
    const tabla = parseCsv(`${CABECERA}\n${texto}\n`);
    try {
      mapClassification(tabla, { position: 0, bib: 1, name: 2, time: 3, category: 4, club: 5, gender: 6, status: 7 });
    } catch (e) {
      return (e as Error).message;
    }
    return '';
  };
  it.each([
    [{ categoria: 'C'.repeat(151) }, 'Fila de datos 1: «Categoría» admite hasta 150 caracteres.'],
    [{ club: 'C'.repeat(151) }, 'Fila de datos 1: «Club» admite hasta 150 caracteres.'],
    [{ tiempo: '1'.repeat(61) }, 'Fila de datos 1: «Tiempo» admite hasta 60 caracteres.'],
    [{ sexo: 'F'.repeat(61) }, 'Fila de datos 1: «Sexo» admite hasta 60 caracteres.'],
    [{ estado: 'R'.repeat(61) }, 'Fila de datos 1: «Estado» admite hasta 60 caracteres.'],
  ])('%o', (celdas, mensaje) => {
    expect(error(fila(celdas))).toBe(mensaje);
  });
});
