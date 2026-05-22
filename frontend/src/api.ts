import type {
  C1SuccessPayload,
  CapabilityCatalogResponse,
  ErrorPayload,
  ProjectCreateResponse,
  ProjectGetResponse,
  ProjectsListResponse,
  StubPayload,
  WorkspaceCreateResponse,
  WorkspacesListResponse,
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

// Русский комментарий: загружает список workspace из C1 backend API.
export async function listWorkspaces(): Promise<WorkspacesListResponse> {
  const response = await fetch("/api/workspaces");
  if (!response.ok) {
    throw new Error(`Failed to load workspaces: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<WorkspacesListResponse>(response);
}

// Русский комментарий: создает workspace через C1 backend API.
export async function createWorkspace(name: string, description: string): Promise<WorkspaceCreateResponse> {
  const response = await fetch("/api/workspaces", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });

  if (!response.ok) {
    const payload = await parseJsonOrThrow<ErrorPayload>(response);
    throw new Error(payload.message || `Failed to create workspace: HTTP ${response.status}`);
  }

  return parseJsonOrThrow<WorkspaceCreateResponse>(response);
}

// Русский комментарий: загружает проекты выбранного workspace.
export async function listProjects(workspaceId: string): Promise<ProjectsListResponse> {
  const response = await fetch(`/api/workspaces/${encodeURIComponent(workspaceId)}/projects`);
  if (!response.ok) {
    throw new Error(`Failed to load projects: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<ProjectsListResponse>(response);
}

// Русский комментарий: создает проект в выбранном workspace.
export async function createProject(
  workspaceId: string,
  name: string,
  description: string,
): Promise<ProjectCreateResponse> {
  const response = await fetch(`/api/workspaces/${encodeURIComponent(workspaceId)}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });

  if (!response.ok) {
    const payload = await parseJsonOrThrow<ErrorPayload>(response);
    throw new Error(payload.message || `Failed to create project: HTTP ${response.status}`);
  }

  return parseJsonOrThrow<ProjectCreateResponse>(response);
}

// Русский комментарий: загружает проект по id, чтобы подтвердить активный выбор.
export async function getProject(projectId: string): Promise<ProjectGetResponse> {
  const response = await fetch(`/api/projects/${encodeURIComponent(projectId)}`);
  if (!response.ok) {
    throw new Error(`Failed to load project: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<ProjectGetResponse>(response);
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

// Русский комментарий: загружает planned-preview payload для C2..C6.
export async function fetchStubCapability(capabilityId: string): Promise<StubPayload> {
  const response = await fetch(`/api/${capabilityId}/sample`);
  if (!response.ok) {
    throw new Error(`Failed to load stub capability ${capabilityId}: HTTP ${response.status}`);
  }
  return parseJsonOrThrow<StubPayload>(response);
}
