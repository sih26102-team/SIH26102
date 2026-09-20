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
    host: true,
    proxy: {
      '/auth': {
        target: process.env.VITE_CASE_API_URL || 'http://localhost:8002',
        changeOrigin: true,
      },
      '/cases': {
        target: process.env.VITE_CASE_API_URL || 'http://localhost:8002',
        changeOrigin: true,
      },
      '/users': {
        target: process.env.VITE_CASE_API_URL || 'http://localhost:8002',
        changeOrigin: true,
      },
      '/works': {
        target: process.env.VITE_DATA_API_URL || 'http://localhost:8001',
        changeOrigin: true,
      },
      '/anomalies': {
        target: process.env.VITE_DATA_API_URL || 'http://localhost:8001',
        changeOrigin: true,
      },
      '/analytics': {
        target: process.env.VITE_DATA_API_URL || 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './tests/setup.js',
  },
});
