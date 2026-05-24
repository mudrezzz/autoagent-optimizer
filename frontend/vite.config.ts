import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Русский комментарий: Vite-конфиг для React/TS фронтенда с проксированием API и design_system к Python backend.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: {
      // Русский комментарий: все backend API вызовы из фронта на dev-сервере идут через Python backend.
      "/api": {
        target: "http://127.0.0.1:4173",
        changeOrigin: true,
      },
      // Русский комментарий: design_system ассеты берем с Python backend, чтобы UI в dev совпадал с runtime.
      "/design_system": {
        target: "http://127.0.0.1:4173",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  test: {
    // Русский комментарий: UI-компонентные тесты запускаем в jsdom, чтобы проверять DOM-состояние и интерактив.
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
    css: true,
  },
});
