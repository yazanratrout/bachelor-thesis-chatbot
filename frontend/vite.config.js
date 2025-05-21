import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/search': {
        target: 'http://localhost:8000', // FastAPI backend
        changeOrigin: true,
        secure: false,
      }
    }
  }
});
