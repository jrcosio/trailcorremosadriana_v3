/// <reference types="vitest/config" />
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { metadatosRutas } from './plugins/metadatos-rutas';

const apiDesarrollo = process.env.API_DESARROLLO ?? 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react(), metadatosRutas({ publicOrigin: process.env.PUBLIC_ORIGIN ?? 'http://localhost:8080' })],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: apiDesarrollo, changeOrigin: false },
      '/media': { target: apiDesarrollo, changeOrigin: false },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  test: {
    environment: 'node',
    include: ['tests/**/*.test.{ts,tsx}'],
  },
});
