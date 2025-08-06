import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
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
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': ['@mui/material', '@emotion/react', '@emotion/styled'],
          'vendor-utils': ['axios', 'lodash', 'date-fns'],
          'vendor-charts': ['recharts', 'd3'],
          'feature-editor': ['monaco-editor', '@monaco-editor/react'],
          'feature-analytics': ['./src/features/analytics/index.ts'],
          'feature-auth': ['./src/features/auth/index.ts']
        },
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? 
            path.basename(chunkInfo.facadeModuleId, path.extname(chunkInfo.facadeModuleId)) : 
            'chunk';
          return `${facadeModuleId}.[hash].js`;
        }
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.debug'],
        passes: 2
      }
    },
    chunkSizeWarningLimit: 500,
    cssCodeSplit: true,
    sourcemap: process.env.NODE_ENV !== 'production'
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
    exclude: ['@aws-sdk']
  }
});