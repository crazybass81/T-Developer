import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { frontendViteConfig } from './backend/src/performance/bundle-optimizer';

export default defineConfig({
  plugins: [react()],
  ...frontendViteConfig,
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
});