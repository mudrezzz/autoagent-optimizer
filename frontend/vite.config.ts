import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РєРѕРЅС„РёРіСѓСЂР°С†РёСЏ Vite РґР»СЏ СЃР±РѕСЂРєРё React/TS С„СЂРѕРЅС‚РµРЅРґР° РІ СЃС‚Р°С‚РёС‡РµСЃРєРёР№ РєР°С‚Р°Р»РѕРі, РєРѕС‚РѕСЂС‹Р№ РѕС‚РґР°РµС‚ Python dev server.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    emptyOutDir: true
  }
});
