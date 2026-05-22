// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: Р±РµР·РѕРїР°СЃРЅС‹Р№ JSON pretty-print РґР»СЏ debug-РїР°РЅРµР»РµР№.
export function prettyJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: СЌРєСЃРїРѕСЂС‚РёСЂСѓРµС‚ РѕР±СЉРµРєС‚ РІ JSON С„Р°Р№Р» С‡РµСЂРµР· Р±СЂР°СѓР·РµСЂРЅС‹Р№ download.
export function exportJsonToFile(payload: unknown, fileName: string): void {
  const blob = new Blob([prettyJson(payload)], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С„РѕСЂРјР°С‚РёСЂСѓРµС‚ С‚РµРєСѓС‰РёР№ timestamp РІ ISO-РѕСЂРёРµРЅС‚РёСЂРѕРІР°РЅРЅС‹Р№ С„Р°Р№Р»-РёРґРµРЅС‚РёС„РёРєР°С‚РѕСЂ.
export function makeTimestampedFileName(prefix: string): string {
  const ts = new Date().toISOString().replace(/[.:]/g, "-");
  return `${prefix}_${ts}.json`;
}
