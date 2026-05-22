import type {
  C1SuccessPayload,
  CapabilityCatalogResponse,
  ErrorPayload,
  StubPayload,
} from "./types";

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: helper, РєРѕС‚РѕСЂС‹Р№ РїР°СЂСЃРёС‚ JSON Рё РїСЂРё РѕС€РёР±РєРµ СЃРѕР·РґР°РµС‚ С‡РµР»РѕРІРµРєРѕС‡РёС‚Р°РµРјРѕРµ СЃРѕРѕР±С‰РµРЅРёРµ.
async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new Error("Invalid JSON response from server.");
  }
  return payload as T;
}

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: Р·Р°РіСЂСѓР¶Р°РµС‚ capability-РєР°С‚Р°Р»РѕРі РґР»СЏ РїРѕСЃС‚СЂРѕРµРЅРёСЏ Р»РµРІРѕРіРѕ РјРµРЅСЋ.
export async function fetchCapabilityCatalog(): Promise<CapabilityCatalogResponse> {
  const response = await fetch("/api/capabilities");
  if (!response.ok) {
    throw new Error(`Failed to load capability catalog: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<CapabilityCatalogResponse>(response);
}

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РІС‹Р·С‹РІР°РµС‚ СЂРµР°Р»СЊРЅС‹Р№ C1 endpoint validate+compile.
export async function runC1ValidateCompile(
  dslFile: string,
): Promise<{ ok: true; payload: C1SuccessPayload } | { ok: false; payload: ErrorPayload }> {
  const response = await fetch("/api/c1/validate-compile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dsl_file: dslFile }),
  });

  if (!response.ok) {
    const payload = await parseJsonOrThrow<ErrorPayload>(response);
    return { ok: false, payload };
  }

  const payload = await parseJsonOrThrow<C1SuccessPayload>(response);
  return { ok: true, payload };
}

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: Р·Р°РіСЂСѓР¶Р°РµС‚ planned-preview payload РґР»СЏ C2..C6.
export async function fetchStubCapability(capabilityId: string): Promise<StubPayload> {
  const response = await fetch(`/api/${capabilityId}/sample`);
  if (!response.ok) {
    throw new Error(`Failed to load stub capability ${capabilityId}: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<StubPayload>(response);
}
