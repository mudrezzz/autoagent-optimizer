import { useEffect, useMemo, useState } from "react";

import {
  createProject,
  createWorkspace,
  fetchCapabilityCatalog,
  fetchStubCapability,
  getProject,
  listProjects,
  listWorkspaces,
} from "./api";
import type { Capability, ProjectRecord, StubPayload, WorkspaceRecord } from "./types";
import { exportJsonToFile, makeTimestampedFileName, prettyJson } from "./utils";

declare global {
  interface Window {
    lucide?: {
      createIcons: () => void;
    };
  }
}

// Русский комментарий: fallback-каталог capability на случай временной недоступности capability API.
const FALLBACK_CAPABILITIES: Capability[] = [
  {
    id: "c1",
    name: "Workspace & Projects",
    description: "Manage workspaces and projects.",
    status: "enabled",
    badge_count: 1,
  },
  {
    id: "c2",
    name: "Task Chat + Candidates",
    description: "Planned slice for chat-driven candidate generation.",
    status: "planned",
    badge_count: 0,
  },
  {
    id: "c3",
    name: "Pattern Library + RAG",
    description: "Planned slice for pattern retrieval and controls.",
    status: "planned",
    badge_count: 0,
  },
  {
    id: "c4",
    name: "Dataset & Metrics Studio",
    description: "Planned slice for datasets and evaluators.",
    status: "planned",
    badge_count: 0,
  },
  {
    id: "c5",
    name: "Optimizer Run Monitor",
    description: "Planned slice for run timeline and metrics monitor.",
    status: "planned",
    badge_count: 0,
  },
  {
    id: "c6",
    name: "Report + Champion Export/Import",
    description: "Planned slice for reports and native loop.",
    status: "planned",
    badge_count: 0,
  },
];

// Русский комментарий: иконки capability для меню рабочего экрана проекта.
const CAPABILITY_ICONS: Record<string, string> = {
  c1: "folders",
  c2: "messages-square",
  c3: "library",
  c4: "database",
  c5: "activity",
  c6: "package-check",
};

// Русский комментарий: структурный тип маршрута для двух основных экранов SaaS-каркаса.
type ScreenRoute =
  | { name: "projects_hub" }
  | {
      name: "workspace";
      workspaceId: string;
    };

// Русский комментарий: структура состояния UI для C1 и planned-preview capability.
type UiState = {
  capabilities: Capability[];
  activeCapabilityId: string;
  workspaces: WorkspaceRecord[];
  activeWorkspaceId: string;
  projects: ProjectRecord[];
  activeProjectId: string;
  workspaceNameInput: string;
  workspaceDescriptionInput: string;
  projectNameInput: string;
  projectDescriptionInput: string;
  budgetPercent: number;
  budgetStage: string;
  metricWorkspaces: string;
  metricProjects: string;
  metricWorkspaceStatus: string;
  metricProjectStatus: string;
  jsonText: string;
  exportMeta: string;
  lastPayload: Record<string, unknown> | null;
};

// Русский комментарий: корневой React-компонент frontend workbench с разделением на Projects Hub и Project Workspace.
export function App(): JSX.Element {
  const [route, setRoute] = useState<ScreenRoute>(() => parseRoute(window.location.pathname));
  const [state, setState] = useState<UiState>({
    capabilities: FALLBACK_CAPABILITIES,
    activeCapabilityId: "c1",
    workspaces: [],
    activeWorkspaceId: "",
    projects: [],
    activeProjectId: "",
    workspaceNameInput: "",
    workspaceDescriptionInput: "",
    projectNameInput: "",
    projectDescriptionInput: "",
    budgetPercent: 0,
    budgetStage: "idle",
    metricWorkspaces: "0",
    metricProjects: "0",
    metricWorkspaceStatus: "not selected",
    metricProjectStatus: "not selected",
    jsonText: "Run C1 actions to see API payloads.",
    exportMeta: "No payload available yet.",
    lastPayload: null,
  });

  // Русский комментарий: активная capability, отображаемая в меню рабочего экрана проекта.
  const activeCapability = useMemo(
    () => state.capabilities.find((item) => item.id === state.activeCapabilityId) ?? FALLBACK_CAPABILITIES[0],
    [state.capabilities, state.activeCapabilityId],
  );

  // Русский комментарий: выбранный workspace для заголовков и операций C1.
  const activeWorkspace = useMemo(
    () => state.workspaces.find((item) => item.workspace_id === state.activeWorkspaceId) ?? null,
    [state.workspaces, state.activeWorkspaceId],
  );

  // Русский комментарий: загружает capability-каталог при старте приложения.
  useEffect(() => {
    void (async () => {
      try {
        const catalog = await fetchCapabilityCatalog();
        setState((prev) => ({ ...prev, capabilities: catalog.capabilities }));
      } catch {
        // Русский комментарий: fallback остается активным, чтобы UI не ломался при сетевых сбоях.
      }
    })();
  }, []);

  // Русский комментарий: загружает список workspace и синхронизирует его с текущим маршрутом.
  useEffect(() => {
    void refreshWorkspaces();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Русский комментарий: слушает переходы браузера назад/вперед и обновляет локальный route-state.
  useEffect(() => {
    const onPopState = (): void => {
      setRoute(parseRoute(window.location.pathname));
    };
    window.addEventListener("popstate", onPopState);
    return () => {
      window.removeEventListener("popstate", onPopState);
    };
  }, []);

  // Русский комментарий: при переходе в workspace-route подгружает проекты нужного workspace.
  useEffect(() => {
    if (route.name !== "workspace") {
      return;
    }
    if (!route.workspaceId) {
      return;
    }
    void loadWorkspaceProjects(route.workspaceId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [route]);

  // Русский комментарий: после каждого рендера переинициализирует Lucide-иконки.
  useEffect(() => {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  });

  // Русский комментарий: переключает интерфейс на Projects Hub и синхронизирует URL.
  function navigateToProjectsHub(): void {
    const path = "/projects";
    window.history.pushState({}, "", path);
    setRoute({ name: "projects_hub" });
    setState((prev) => ({
      ...prev,
      activeCapabilityId: "c1",
      activeWorkspaceId: "",
      projects: [],
      activeProjectId: "",
      metricProjects: "0",
      metricWorkspaceStatus: "not selected",
      metricProjectStatus: "not selected",
    }));
  }

  // Русский комментарий: переключает интерфейс на рабочий экран конкретного workspace и синхронизирует URL.
  function navigateToWorkspace(workspaceId: string): void {
    const path = `/projects/${encodeURIComponent(workspaceId)}/workspace`;
    window.history.pushState({}, "", path);
    setRoute({ name: "workspace", workspaceId });
  }

  // Русский комментарий: обновляет список workspace и поддерживает консистентность активного контекста.
  async function refreshWorkspaces(preferredWorkspaceId?: string): Promise<void> {
    try {
      const workspacesResponse = await listWorkspaces();
      const workspaces = workspacesResponse.workspaces;

      let nextWorkspaceId = "";
      if (preferredWorkspaceId && workspaces.some((item) => item.workspace_id === preferredWorkspaceId)) {
        nextWorkspaceId = preferredWorkspaceId;
      } else if (route.name === "workspace" && workspaces.some((item) => item.workspace_id === route.workspaceId)) {
        nextWorkspaceId = route.workspaceId;
      }

      const snapshot = {
        status: "success",
        c1_slice: "workspace_registry_v0",
        workspaces,
        active_workspace_id: nextWorkspaceId,
      };

      setState((prev) => ({
        ...prev,
        workspaces,
        activeWorkspaceId: nextWorkspaceId,
        metricWorkspaces: String(workspaces.length),
        metricWorkspaceStatus: nextWorkspaceId ? "selected" : "not selected",
        budgetPercent: 100,
        budgetStage: "loaded",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));

      if (route.name === "workspace" && nextWorkspaceId === "") {
        navigateToProjectsHub();
      }
    } catch (error) {
      setState((prev) => ({
        ...prev,
        budgetPercent: 100,
        budgetStage: "failed",
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: подгружает проекты выбранного workspace и фиксирует активный project-контекст.
  async function loadWorkspaceProjects(workspaceId: string): Promise<void> {
    setState((prev) => ({ ...prev, activeWorkspaceId: workspaceId, budgetStage: "loading projects" }));

    try {
      const projectsResponse = await listProjects(workspaceId);
      const projects = projectsResponse.projects;
      const nextProjectId = projects[0]?.project_id ?? "";
      const snapshot = {
        status: "success",
        action: "select_workspace",
        workspace_id: workspaceId,
        projects,
      };

      setState((prev) => ({
        ...prev,
        projects,
        activeWorkspaceId: workspaceId,
        activeProjectId: nextProjectId,
        metricProjects: String(projects.length),
        metricWorkspaceStatus: "selected",
        metricProjectStatus: nextProjectId ? "selected" : "not selected",
        budgetPercent: 100,
        budgetStage: "workspace selected",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        projects: [],
        activeProjectId: "",
        budgetPercent: 100,
        budgetStage: "failed",
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: обрабатывает переключение capability в рабочем экране проекта.
  async function handleSwitchCapability(capabilityId: string): Promise<void> {
    setState((prev) => ({
      ...prev,
      activeCapabilityId: capabilityId,
      budgetPercent: capabilityId === "c1" ? prev.budgetPercent : 10,
      budgetStage: capabilityId === "c1" ? prev.budgetStage : "planned",
    }));

    if (capabilityId === "c1") {
      return;
    }

    try {
      const payload: StubPayload = await fetchStubCapability(capabilityId);
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson(payload),
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: создает workspace на Projects Hub и перезагружает список workspace.
  async function handleCreateWorkspace(): Promise<void> {
    const name = state.workspaceNameInput.trim();
    const description = state.workspaceDescriptionInput.trim();
    if (!name) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: "Workspace name is required." }),
      }));
      return;
    }

    setState((prev) => ({ ...prev, budgetPercent: 35, budgetStage: "creating workspace" }));

    try {
      const created = await createWorkspace(name, description);
      await refreshWorkspaces(created.workspace.workspace_id);
      setState((prev) => ({
        ...prev,
        workspaceNameInput: "",
        workspaceDescriptionInput: "",
        jsonText: prettyJson({ status: "success", action: "create_workspace", workspace: created.workspace }),
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        budgetPercent: 100,
        budgetStage: "failed",
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: открывает выбранный workspace и загружает его проектный контекст.
  async function handleOpenWorkspace(workspaceId: string): Promise<void> {
    navigateToWorkspace(workspaceId);
    await loadWorkspaceProjects(workspaceId);
  }

  // Русский комментарий: создает project в активном workspace.
  async function handleCreateProject(): Promise<void> {
    const workspaceId = state.activeWorkspaceId;
    if (!workspaceId) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: "Select workspace before creating project." }),
      }));
      return;
    }

    const name = state.projectNameInput.trim();
    const description = state.projectDescriptionInput.trim();
    if (!name) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: "Project name is required." }),
      }));
      return;
    }

    setState((prev) => ({ ...prev, budgetPercent: 50, budgetStage: "creating project" }));

    try {
      const created = await createProject(workspaceId, name, description);
      const projectsResponse = await listProjects(workspaceId);
      const projects = projectsResponse.projects;
      const snapshot = {
        status: "success",
        action: "create_project",
        workspace_id: workspaceId,
        created_project_id: created.project.project_id,
        projects,
      };

      setState((prev) => ({
        ...prev,
        projects,
        activeProjectId: created.project.project_id,
        projectNameInput: "",
        projectDescriptionInput: "",
        budgetPercent: 100,
        budgetStage: "project created",
        metricProjects: String(projects.length),
        metricProjectStatus: "selected",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        budgetPercent: 100,
        budgetStage: "failed",
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: выбирает project и подтверждает выбор через GET /api/projects/{id}.
  async function handleSelectProject(projectId: string): Promise<void> {
    setState((prev) => ({ ...prev, activeProjectId: projectId, budgetStage: "loading project" }));
    try {
      const response = await getProject(projectId);
      const snapshot = {
        status: "success",
        action: "select_project",
        project: response.project,
      };

      setState((prev) => ({
        ...prev,
        budgetPercent: 100,
        budgetStage: "project selected",
        metricProjectStatus: "selected",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        budgetPercent: 100,
        budgetStage: "failed",
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: экспортирует последний JSON payload для ручной инспекции.
  function handleExportPayload(): void {
    if (!state.lastPayload) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "No payload to export yet." }) }));
      return;
    }

    const fileName = makeTimestampedFileName("c1_workspace_snapshot");
    exportJsonToFile(state.lastPayload, fileName);
    setState((prev) => ({ ...prev, exportMeta: `Saved: ${fileName}` }));
  }

  // Русский комментарий: синхронизирует input названия workspace.
  function handleWorkspaceNameChange(nextValue: string): void {
    setState((prev) => ({ ...prev, workspaceNameInput: nextValue }));
  }

  // Русский комментарий: синхронизирует input описания workspace.
  function handleWorkspaceDescriptionChange(nextValue: string): void {
    setState((prev) => ({ ...prev, workspaceDescriptionInput: nextValue }));
  }

  // Русский комментарий: синхронизирует input названия project.
  function handleProjectNameChange(nextValue: string): void {
    setState((prev) => ({ ...prev, projectNameInput: nextValue }));
  }

  // Русский комментарий: синхронизирует input описания project.
  function handleProjectDescriptionChange(nextValue: string): void {
    setState((prev) => ({ ...prev, projectDescriptionInput: nextValue }));
  }

  // Русский комментарий: подставляет demo-значения в форму workspace.
  function handleFillWorkspaceExample(): void {
    setState((prev) => ({
      ...prev,
      workspaceNameInput: "support-qa",
      workspaceDescriptionInput: "Workspace for support quality optimization experiments.",
    }));
  }

  // Русский комментарий: подставляет demo-значения в форму project.
  function handleFillProjectExample(): void {
    setState((prev) => ({
      ...prev,
      projectNameInput: "support-qa.v1",
      projectDescriptionInput: "First project version for stylizer and support benchmark loops.",
    }));
  }

  const isWorkspaceRoute = route.name === "workspace";
  const isC1Enabled = activeCapability.id === "c1" && activeCapability.status === "enabled";

  return (
    <div className={`app${isWorkspaceRoute ? " app--workspace" : " app--hub"}`} id="app-root">
      <aside className="app-sidebar">
        <div className="app-sidebar-brand">
          <img src="/design_system/assets/logo-lockup.svg" alt="AutoAgent Optimizer" />
        </div>

        {isWorkspaceRoute ? (
          <>
            <div className="app-sidebar-section">
              <div className="app-side-label">Project Workspace</div>
              <button type="button" className="app-side-pick" onClick={navigateToProjectsHub}>
                <i data-lucide="arrow-left" />
                <span>Back to Projects Hub</span>
              </button>
            </div>

            <nav className="app-side-nav" id="capability-nav" aria-label="Capabilities">
              {state.capabilities.map((capability) => {
                const iconName = CAPABILITY_ICONS[capability.id] ?? "circle";
                const statusClass = capability.status === "enabled" ? "enabled" : "planned";
                return (
                  <button
                    key={capability.id}
                    type="button"
                    className={`cap-link${capability.id === state.activeCapabilityId ? " active" : ""}${
                      capability.status === "planned" ? " disabled" : ""
                    }`}
                    onClick={() => {
                      void handleSwitchCapability(capability.id);
                    }}
                  >
                    <i data-lucide={iconName} className="cap-icon" />
                    <span className="cap-name">{capability.name}</span>
                    <span className={`cap-badge ${statusClass}`}>
                      {capability.status === "enabled" ? "live" : "planned"}
                      {capability.badge_count ? ` ${capability.badge_count}` : ""}
                    </span>
                  </button>
                );
              })}
            </nav>
          </>
        ) : (
          <div className="app-sidebar-section">
            <div className="app-side-label">Workspace</div>
            <button type="button" className="app-side-pick" disabled>
              <span className="ws-dot" />
              <span>Projects Hub</span>
            </button>
          </div>
        )}

        <div className="app-sidebar-foot">
          <div className="app-side-user">
            <div className="avatar">AO</div>
            <div>
              <div className="user-name">Optimizer Team</div>
              <div className="user-org">vertical delivery mode</div>
            </div>
            <i data-lucide="settings-2" />
          </div>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-topbar">
          <div className="tb-left">
            {isWorkspaceRoute ? (
              <>
                <span className="tb-crumb">Projects</span>
                <span className="tb-sep">/</span>
                <span className="tb-id">{activeWorkspace?.name ?? route.workspaceId}</span>
                <span className="tb-pill">workspace mode</span>
              </>
            ) : (
              <>
                <span className="tb-crumb">Projects</span>
                <span className="tb-sep">/</span>
                <span className="tb-id">hub</span>
                <span className="tb-pill">workspace registry</span>
              </>
            )}
          </div>

          <div className="tb-budget" id="budget-box">
            <div className="tb-budget-label">
              <i data-lucide="gauge" />
              <span>{isWorkspaceRoute ? "Workspace progress" : "Hub progress"}</span>
            </div>
            <div className="tb-budget-bar">
              <div className="tb-budget-fill" style={{ width: `${state.budgetPercent}%` }} />
            </div>
            <div className="tb-budget-vals">
              <span>{Math.round(state.budgetPercent)}%</span>
              <span className="muted">{state.budgetStage}</span>
            </div>
          </div>

          <div className="tb-right">
            <button type="button" className="tb-btn tb-btn-ghost" onClick={handleExportPayload}>
              <i data-lucide="file-json-2" />
              Export snapshot
            </button>
          </div>
        </header>

        <div className="app-content app-content--single">
          <main className="app-center">
            {!isWorkspaceRoute ? (
              <>
                <section className="content-head">
                  <div>
                    <h1 className="ch-title">
                      Projects Hub <span>- SaaS workspace list</span>
                    </h1>
                    <p className="ch-sub">
                      Create and browse workspaces. Each workspace is an isolated customer project context.
                    </p>
                  </div>
                </section>

                <section className="metric-strip" id="metric-strip">
                  <article className="ms-cell">
                    <div className="ms-lbl">Workspaces</div>
                    <div className="ms-row">
                      <div className="ms-val">{state.metricWorkspaces}</div>
                    </div>
                    <div className="ms-cap">Visible in current tenant scope</div>
                  </article>

                  <article className="ms-cell">
                    <div className="ms-lbl">Selected workspace</div>
                    <div className="ms-row">
                      <div className="ms-val">{state.metricWorkspaceStatus}</div>
                    </div>
                    <div className="ms-cap">Project workspace entrypoint</div>
                  </article>

                  <article className="ms-cell">
                    <div className="ms-lbl">Last export</div>
                    <div className="ms-row">
                      <div className="ms-val">JSON</div>
                    </div>
                    <div className="ms-cap">{state.exportMeta}</div>
                  </article>

                  <article className="ms-cell">
                    <div className="ms-lbl">Backend status</div>
                    <div className="ms-row">
                      <div className="ms-val">online</div>
                    </div>
                    <div className="ms-cap">C1 API connected</div>
                  </article>
                </section>

                <section className="arch-list">
                  <header className="arch-list-head">
                    <div className="al-label">Create workspace</div>
                    <div className="al-tools">
                      <button type="button" className="al-tool" onClick={handleFillWorkspaceExample}>
                        <i data-lucide="wand-sparkles" />
                        Example
                      </button>
                    </div>
                  </header>
                  <div className="c1-form-row">
                    <label className="c1-field-label" htmlFor="workspace-name-input">
                      Workspace name
                    </label>
                    <div className="c1-form-controls c1-form-stack">
                      <input
                        id="workspace-name-input"
                        type="text"
                        value={state.workspaceNameInput}
                        onChange={(event) => {
                          handleWorkspaceNameChange(event.target.value);
                        }}
                        placeholder="support-qa"
                      />
                      <textarea
                        id="workspace-description-input"
                        value={state.workspaceDescriptionInput}
                        onChange={(event) => {
                          handleWorkspaceDescriptionChange(event.target.value);
                        }}
                        placeholder="Optional workspace description"
                      />
                      <button type="button" className="tb-btn tb-btn-primary" onClick={() => void handleCreateWorkspace()}>
                        Create workspace
                      </button>
                    </div>
                  </div>
                </section>

                <section className="trace-view">
                  <header className="tv-head">
                    <div className="tv-title">
                      <i data-lucide="folders" />
                      <span>Workspace tiles</span>
                      <span className="tv-arch">{state.workspaces.length} total</span>
                    </div>
                  </header>
                  <div className="tv-body">
                    <div className="workspace-grid" id="workspace-grid">
                      {state.workspaces.length === 0 ? (
                        <div className="workspace-card workspace-card--empty">No workspace yet. Create one to continue.</div>
                      ) : (
                        state.workspaces.map((workspace) => (
                          <article key={workspace.workspace_id} className="workspace-card">
                            <div className="workspace-card-title">{workspace.name}</div>
                            <div className="workspace-card-sub">{workspace.description || "No description"}</div>
                            <div className="workspace-card-meta">{workspace.workspace_id}</div>
                            <button
                              type="button"
                              className="sg-apply"
                              onClick={() => {
                                void handleOpenWorkspace(workspace.workspace_id);
                              }}
                            >
                              Open workspace
                            </button>
                          </article>
                        ))
                      )}
                    </div>
                    <pre className="json-view">{state.jsonText}</pre>
                  </div>
                </section>
              </>
            ) : (
              <>
                <section className="content-head">
                  <div>
                    <h1 className="ch-title">
                      {activeWorkspace?.name ?? route.workspaceId} <span>- project workspace</span>
                    </h1>
                    <p className="ch-sub">
                      Use this screen to work with projects, then unlock next capabilities by roadmap slices.
                    </p>
                  </div>
                </section>

                <section className="metric-strip" id="metric-strip-workspace">
                  <article className="ms-cell">
                    <div className="ms-lbl">Workspace</div>
                    <div className="ms-row">
                      <div className="ms-val">{activeWorkspace?.name ?? "n/a"}</div>
                    </div>
                    <div className="ms-cap">Active workspace context</div>
                  </article>

                  <article className="ms-cell">
                    <div className="ms-lbl">Projects</div>
                    <div className="ms-row">
                      <div className="ms-val">{state.metricProjects}</div>
                    </div>
                    <div className="ms-cap">Inside selected workspace</div>
                  </article>

                  <article className="ms-cell">
                    <div className="ms-lbl">Project context</div>
                    <div className="ms-row">
                      <div className="ms-val">{state.metricProjectStatus}</div>
                    </div>
                    <div className="ms-cap">Run-ready context</div>
                  </article>

                  <article className="ms-cell">
                    <div className="ms-lbl">Capability</div>
                    <div className="ms-row">
                      <div className="ms-val">{activeCapability.id.toUpperCase()}</div>
                    </div>
                    <div className="ms-cap">{activeCapability.name}</div>
                  </article>
                </section>

                {isC1Enabled ? (
                  <>
                    <section className="arch-list">
                      <header className="arch-list-head">
                        <div className="al-label">Create project in active workspace</div>
                        <div className="al-tools">
                          <button type="button" className="al-tool" onClick={handleFillProjectExample} disabled={!state.activeWorkspaceId}>
                            <i data-lucide="wand-sparkles" />
                            Example
                          </button>
                        </div>
                      </header>
                      <div className="c1-form-row">
                        <label className="c1-field-label" htmlFor="project-name-input">
                          Project name ({activeWorkspace?.name ?? "no workspace"})
                        </label>
                        <div className="c1-form-controls c1-form-stack">
                          <input
                            id="project-name-input"
                            type="text"
                            value={state.projectNameInput}
                            onChange={(event) => {
                              handleProjectNameChange(event.target.value);
                            }}
                            placeholder="support-qa.v1"
                            disabled={!state.activeWorkspaceId}
                          />
                          <textarea
                            id="project-description-input"
                            value={state.projectDescriptionInput}
                            onChange={(event) => {
                              handleProjectDescriptionChange(event.target.value);
                            }}
                            placeholder="Optional project description"
                            disabled={!state.activeWorkspaceId}
                          />
                          <button
                            type="button"
                            className="tb-btn tb-btn-primary"
                            onClick={() => {
                              void handleCreateProject();
                            }}
                            disabled={!state.activeWorkspaceId}
                          >
                            Create project
                          </button>
                        </div>
                      </div>
                    </section>

                    <section className="trace-view">
                      <header className="tv-head">
                        <div className="tv-title">
                          <i data-lucide="folder-open" />
                          <span>Projects in workspace</span>
                          <span className="tv-arch">{state.projects.length} total</span>
                        </div>
                      </header>
                      <div className="tv-body">
                        <div className="issues-box">
                          {state.projects.length === 0 ? (
                            <div className="issue-row info">No project in selected workspace yet.</div>
                          ) : (
                            state.projects.map((project) => (
                              <div key={project.project_id} className={`issue-row info${project.project_id === state.activeProjectId ? " selected-row" : ""}`}>
                                <div className="row-main">
                                  <b>{project.name}</b> <span className="muted">({project.project_id})</span>
                                  <div className="row-sub">{project.description || "No description"}</div>
                                </div>
                                <button
                                  type="button"
                                  className="sg-apply"
                                  onClick={() => {
                                    void handleSelectProject(project.project_id);
                                  }}
                                >
                                  Select
                                </button>
                              </div>
                            ))
                          )}
                        </div>
                        <pre className="json-view">{state.jsonText}</pre>
                      </div>
                    </section>
                  </>
                ) : (
                  <section className="trace-view">
                    <header className="tv-head">
                      <div className="tv-title">
                        <i data-lucide="lock" />
                        <span>Planned capability preview</span>
                      </div>
                    </header>
                    <div className="tv-body">
                      <div className="issue-row warning">
                        Capability {activeCapability.id.toUpperCase()} is visible in shell, but not unlocked yet in this slice.
                      </div>
                      <pre className="json-view">{state.jsonText}</pre>
                    </div>
                  </section>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

// Русский комментарий: парсит URL и определяет активный экран приложения.
function parseRoute(pathname: string): ScreenRoute {
  const workspaceMatch = pathname.match(/^\/projects\/([^/]+)\/workspace\/?$/);
  if (workspaceMatch && workspaceMatch[1]) {
    return { name: "workspace", workspaceId: decodeURIComponent(workspaceMatch[1]) };
  }
  return { name: "projects_hub" };
}
