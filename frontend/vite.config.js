import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite konfiguracija. Frontend se vrti na portu 5173 (isti koji backend
// dopusta u CORS-u). Backend ocekujemo na http://localhost:8000.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
})
