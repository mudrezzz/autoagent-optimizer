import type {
  ArenaDeleteResponse,
  ArenaGetResponse,
  ArenasListResponse,
  ArenaMutationResponse,
  C2ChatPostMessageResponse,
  C2ChatStateResponse,
  C1SuccessPayload,
  CapabilityCatalogResponse,
  ErrorPayload,
  StubPayload,
} from "./types";

// Русский комментарий: helper, который парсит JSON и при ошибке создает человекочитаемое сообщение.
async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new Error("Invalid JSON response from server.");
  }
  return payload as T;
}

// Русский комментарий: загружает capability-каталог для построения левого меню.
export async function fetchCapabilityCatalog(): Promise<CapabilityCatalogResponse> {
  const response = await fetch("/api/capabilities");
  if (!response.ok) {
    throw new Error(`Failed to load capability catalog: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<CapabilityCatalogResponse>(response);
}

// Русский комментарий: загружает список battle-арен из C1 backend API.
export async function listArenas(): Promise<ArenasListResponse> {
  const response = await fetch("/api/arenas");
  if (!response.ok) {
    throw new Error(`Failed to load arenas: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<ArenasListResponse>(response);
}

// Русский комментарий: создает arena через C1 backend API.
export async function createArena(name: string, description: string): Promise<ArenaMutationResponse> {
  const response = await fetch("/api/arenas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });

  if (!response.ok) {
    const payload = await parseJsonOrThrow<ErrorPayload>(response);
    throw new Error(payload.message || `Failed to create arena: HTTP ${response.status}`);
  }

  return parseJsonOrThrow<ArenaMutationResponse>(response);
}

// Русский комментарий: обновляет имя arena через C1 backend API.
export async function renameArena(arenaId: string, name: string): Promise<ArenaMutationResponse> {
  const response = await fetch(`/api/arenas/${encodeURIComponent(arenaId)}/rename`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!response.ok) {
    const payload = await parseJsonOrThrow<ErrorPayload>(response);
    throw new Error(payload.message || `Failed to rename arena: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<ArenaMutationResponse>(response);
}

// Русский комментарий: дублирует arena через C1 backend API.
export async function duplicateArena(arenaId: string): Promise<ArenaMutationResponse> {
  const response = await fetch(`/api/arenas/${encodeURIComponent(arenaId)}/duplicate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
  if (!response.ok) {
    const payload = await parseJsonOrThrow<ErrorPayload>(response);
    throw new Error(payload.message || `Failed to duplicate arena: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<ArenaMutationResponse>(response);
}

// Русский комментарий: удаляет arena через C1 backend API.
export async function deleteArena(arenaId: string): Promise<ArenaDeleteResponse> {
  const response = await fetch(`/api/arenas/${encodeURIComponent(arenaId)}/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
  if (!response.ok) {
    const payload = await parseJsonOrThrow<ErrorPayload>(response);
    throw new Error(payload.message || `Failed to delete arena: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<ArenaDeleteResponse>(response);
}

// Русский комментарий: загружает arena по id, чтобы подтвердить активный выбор.
export async function getArena(arenaId: string): Promise<ArenaGetResponse> {
  const response = await fetch(`/api/arenas/${encodeURIComponent(arenaId)}`);
  if (!response.ok) {
    throw new Error(`Failed to load arena: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<ArenaGetResponse>(response);
}

// Русский комментарий: загружает C2 chat state для выбранной arena.
export async function getArenaChatState(arenaId: string): Promise<C2ChatStateResponse> {
  const response = await fetch(`/api/arenas/${encodeURIComponent(arenaId)}/chat/state`);
  if (!response.ok) {
    const payload = await parseJsonOrThrow<ErrorPayload>(response);
    throw new Error(payload.message || `Failed to load C2 chat state: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<C2ChatStateResponse>(response);
}

// Русский комментарий: отправляет сообщение в C2 чат и опционально запускает генерацию candidate draft.
export async function postArenaChatMessage(
  arenaId: string,
  message: string,
  options: {
    generateCandidates: boolean;
    maxCandidates?: number;
  },
): Promise<C2ChatPostMessageResponse> {
  const maxCandidates = options.maxCandidates ?? 3;
  const response = await fetch(`/api/arenas/${encodeURIComponent(arenaId)}/chat/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      generate_candidates: options.generateCandidates,
      max_candidates: maxCandidates,
    }),
  });
  if (!response.ok) {
    const payload = await parseJsonOrThrow<ErrorPayload>(response);
    throw new Error(payload.message || `Failed to post C2 chat message: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<C2ChatPostMessageResponse>(response);
}

// Русский комментарий: legacy debug endpoint validate+compile оставлен для обратной совместимости.
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

// Русский комментарий: загружает planned-preview payload для C3..C6.
export async function fetchStubCapability(capabilityId: string): Promise<StubPayload> {
  const response = await fetch(`/api/${capabilityId}/sample`);
  if (!response.ok) {
    throw new Error(`Failed to load stub capability ${capabilityId}: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<StubPayload>(response);
}
