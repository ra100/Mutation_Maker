import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      shared: path.resolve(__dirname, './src/shared'),
      scenes: path.resolve(__dirname, './src/scenes'),
      services: path.resolve(__dirname, './src/services'),
      typings: path.resolve(__dirname, './src/typings'),
      'feature-viewer': path.resolve(__dirname, './feature-viewer/index.js')
    }
  },
  optimizeDeps: {
    include: ['feature-viewer'],
    esbuild: {
      loader: 'cjs'
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/v1': 'http://localhost:8000'
    }
  },
  build: {
    outDir: 'build',
    commonjsOptions: {
      include: [/node_modules/, /feature-viewer/]
    }
  }
})
