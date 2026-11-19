// Utilidades compartidas por los scripts de verificación con Playwright.
import { chromium } from 'playwright';

export const ANCHOS = [360, 768, 1024, 1440];

export async function navegador() {
  return chromium.launch();
}

/** Desplaza la página hasta el final para forzar la carga de imágenes `loading="lazy"`. */
export async function cargarTodo(page) {
  await page.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 600) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 60));
    }
    window.scrollTo(0, 0);
  });
  await page.waitForLoadState('networkidle').catch(() => {});
}

export function fallo(mensaje) {
  console.error('FALLO ' + mensaje);
  process.exitCode = 1;
}

export function ok(mensaje) {
  console.log('OK    ' + mensaje);
}
