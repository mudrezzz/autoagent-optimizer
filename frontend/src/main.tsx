import React from "react";
import ReactDOM from "react-dom/client";

import "../styles.css";
import { App } from "./App";

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РѕС‡РєР° РІС…РѕРґР° React-РїСЂРёР»РѕР¶РµРЅРёСЏ, РјРѕРЅС‚РёСЂСѓСЋС‰Р°СЏ workbench РІ РєРѕСЂРЅРµРІРѕР№ РєРѕРЅС‚РµР№РЅРµСЂ.
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
