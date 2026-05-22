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

// Русский комментарий: fallback-каталог на случай временной недоступности capability API.
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

// Русский комментарий: иконки capability для левого меню.
const CAPABILITY_ICONS: Record<string, string> = {
  c1: "folders",
  c2: "messages-square",
  c3: "library",
  c4: "database",
  c5: "activity",
  c6: "package-check",
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
  bottleneckId: string;
  bottleneckText: string;
  suggestions: Array<{ tag: string; title: string; detail: string }>;
  exportMeta: string;
  lastPayload: Record<string, unknown> | null;
};

// Русский комментарий: корневой React-компонент frontend workbench в каркасе app-v3.
export function App(): JSX.Element {
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
    bottleneckId: "workspace_not_initialized",
    bottleneckText: "Create the first workspace to unlock project context.",
    suggestions: [
      {
        tag: "Step 1",
        title: "Create workspace",
        detail: "Start by creating a workspace that will hold project versions and runs.",
      },
      {
        tag: "Step 2",
        title: "Create project",
        detail: "Inside workspace create a project to activate the optimization lifecycle.",
      },
    ],
    exportMeta: "No payload available yet.",
    lastPayload: null,
  });

  // Русский комментарий: активная capability, отображаемая в центре интерфейса.
  const activeCapability = useMemo(
    () => state.capabilities.find((item) => item.id === state.activeCapabilityId) ?? FALLBACK_CAPABILITIES[0],
    [state.capabilities, state.activeCapabilityId],
  );

  // Русский комментарий: выбранный workspace для заголовков/формы project.
  const activeWorkspace = useMemo(
    () => state.workspaces.find((item) => item.workspace_id === state.activeWorkspaceId) ?? null,
    [state.workspaces, state.activeWorkspaceId],
  );

  // Русский комментарий: выбранный project для метрик и sidebar-индикаторов.
  const activeProject = useMemo(
    () => state.projects.find((item) => item.project_id === state.activeProjectId) ?? null,
    [state.projects, state.activeProjectId],
  );

  // Русский комментарий: загрузка capability-каталога при старте приложения.
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

  // Русский комментарий: первичная загрузка workspace/project данных для C1.
  useEffect(() => {
    void refreshWorkspacesAndProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Русский комментарий: после каждого рендера переинициализируем Lucide-иконки.
  useEffect(() => {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  });

  // Русский комментарий: обновляет список workspace и автоматически подгружает проекты выбранного workspace.
  async function refreshWorkspacesAndProjects(preferredWorkspaceId?: string): Promise<void> {
    try {
      const workspacesResponse = await listWorkspaces();
      const workspaces = workspacesResponse.workspaces;

      const nextWorkspaceId =
        preferredWorkspaceId && workspaces.some((item) => item.workspace_id === preferredWorkspaceId)
          ? preferredWorkspaceId
          : workspaces[0]?.workspace_id ?? "";

      let projects: ProjectRecord[] = [];
      if (nextWorkspaceId) {
        const projectsResponse = await listProjects(nextWorkspaceId);
        projects = projectsResponse.projects;
      }

      const nextProjectId = projects[0]?.project_id ?? "";
      const snapshot = {
        status: "success",
        c1_slice: "workspace_registry_v0",
        workspaces,
        active_workspace_id: nextWorkspaceId,
        projects,
        active_project_id: nextProjectId,
      };

      setState((prev) => ({
        ...prev,
        workspaces,
        activeWorkspaceId: nextWorkspaceId,
        projects,
        activeProjectId: nextProjectId,
        budgetPercent: 100,
        budgetStage: "loaded",
        metricWorkspaces: String(workspaces.length),
        metricProjects: String(projects.length),
        metricWorkspaceStatus: nextWorkspaceId ? "selected" : "not selected",
        metricProjectStatus: nextProjectId ? "selected" : "not selected",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        budgetPercent: 100,
        budgetStage: "failed",
        jsonText: prettyJson({ status: "error", message: String(error) }),
        bottleneckId: "workspace_api_error",
        bottleneckText: "Cannot load workspace registry. Verify backend dev server status.",
        suggestions: [
          {
            tag: "Backend",
            title: "Check dev server",
            detail: "Ensure python dev server is running and /api/workspaces responds with 200.",
          },
        ],
      }));
    }
  }

  // Русский комментарий: обрабатывает переключение capability в левом меню.
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
        bottleneckId: "planned_capability",
        bottleneckText: "This capability is intentionally locked until its vertical slice is delivered.",
        suggestions: [
          {
            tag: "Roadmap",
            title: "Continue with C1",
            detail: "Use C1 workspace/project flow before unlocking next capability slices.",
          },
        ],
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: создает workspace и обновляет списки/метрики.
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
      await refreshWorkspacesAndProjects(created.workspace.workspace_id);
      setState((prev) => ({
        ...prev,
        workspaceNameInput: "",
        workspaceDescriptionInput: "",
        bottleneckId: "workspace_created",
        bottleneckText: "Workspace created. Next step: create the first project.",
        suggestions: [
          {
            tag: "Step",
            title: "Create project",
            detail: "Use the project form below to create a project inside selected workspace.",
          },
        ],
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        budgetPercent: 100,
        budgetStage: "failed",
        jsonText: prettyJson({ status: "error", message: String(error) }),
        bottleneckId: "workspace_create_failed",
        bottleneckText: "Workspace create request failed. Check validation and duplicate names.",
      }));
    }
  }

  // Русский комментарий: загружает проекты выбранного workspace и фиксирует активный контекст.
  async function handleSelectWorkspace(workspaceId: string): Promise<void> {
    setState((prev) => ({ ...prev, activeWorkspaceId: workspaceId, activeProjectId: "", budgetStage: "loading projects" }));
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
        activeProjectId: nextProjectId,
        budgetPercent: 100,
        budgetStage: "workspace selected",
        metricProjects: String(projects.length),
        metricWorkspaceStatus: "selected",
        metricProjectStatus: nextProjectId ? "selected" : "not selected",
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

  // Русский комментарий: создает project в выбранном workspace.
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
        bottleneckId: "project_created",
        bottleneckText: "Project is active. Next slices will unlock chat and candidate generation.",
        suggestions: [
          {
            tag: "Next",
            title: "Proceed to C2",
            detail: "When C2 is unlocked, use this active project as chat context for candidate synthesis.",
          },
        ],
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

  const isC1Enabled = activeCapability.id === "c1" && activeCapability.status === "enabled";

  return (
    <div className="app" id="app-root">
      <aside className="app-sidebar">
        <div className="app-sidebar-brand">
          <img src="/design_system/assets/logo-lockup.svg" alt="AutoAgent Optimizer" />
        </div>

        <div className="app-sidebar-section">
          <div className="app-side-label">Workspace</div>
          <button type="button" className="app-side-pick" id="workspace-pick">
            <span className="ws-dot" />
            <span>{activeWorkspace?.name ?? "no workspace"}</span>
            <i data-lucide="chevrons-up-down" />
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
            <span className="tb-crumb">Workspaces</span>
            <span className="tb-sep">/</span>
            <span className="tb-id">registry_v0</span>
            <span className="tb-pill">{isC1Enabled ? "C1 enabled" : "planned capability"}</span>
          </div>

          <div className="tb-budget" id="budget-box">
            <div className="tb-budget-label">
              <i data-lucide="gauge" />
              <span>C1 progress</span>
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
            <button
              type="button"
              className="tb-btn tb-btn-ghost"
              onClick={() => {
                setState((prev) => ({
                  ...prev,
                  jsonText: prettyJson({ status: "notice", message: "Compare action is planned for C5/C6 slices." }),
                }));
              }}
            >
              <i data-lucide="git-compare" />
              Compare
            </button>
            <button
              type="button"
              className="tb-btn tb-btn-primary"
              onClick={() => {
                setState((prev) => ({
                  ...prev,
                  jsonText: prettyJson({ status: "notice", message: "Promote action is planned for C6 slice." }),
                }));
              }}
            >
              Promote champion
            </button>
          </div>
        </header>

        <div className="app-content">
          <main className="app-center">
            <section className="content-head">
              <div>
                <h1 className="ch-title">
                  Workspace &amp; Project Registry <span>- C1 vertical slice</span>
                </h1>
                <p className="ch-sub">
                  {isC1Enabled
                    ? "Create and manage workspace/project context for future chat, dataset, and optimization runs."
                    : "Capability is visible in the product shell and will be unlocked by roadmap slices."}
                </p>
              </div>
              <div className="ch-actions">
                <span className="ch-pill">
                  <span className="dot" />
                  {state.activeCapabilityId.toUpperCase()} - {activeCapability.name}
                </span>
              </div>
            </section>

            <section className="metric-strip" id="metric-strip">
              <article className="ms-cell">
                <div className="ms-lbl">Workspaces</div>
                <div className="ms-row">
                  <div className="ms-val">{state.metricWorkspaces}</div>
                </div>
                <div className="ms-cap">Registry size</div>
              </article>

              <article className="ms-cell">
                <div className="ms-lbl">Projects</div>
                <div className="ms-row">
                  <div className="ms-val">{state.metricProjects}</div>
                </div>
                <div className="ms-cap">Selected workspace scope</div>
              </article>

              <article className="ms-cell">
                <div className="ms-lbl">Workspace context</div>
                <div className="ms-row">
                  <div className="ms-val">{state.metricWorkspaceStatus}</div>
                </div>
                <div className="ms-cap">Required for C2</div>
              </article>

              <article className="ms-cell">
                <div className="ms-lbl">Project context</div>
                <div className="ms-row">
                  <div className="ms-val">{state.metricProjectStatus}</div>
                </div>
                <div className="ms-cap">Run-ready context</div>
              </article>
            </section>

            <section className="arch-list">
              <header className="arch-list-head">
                <div className="al-label">Create workspace</div>
                <div className="al-tools">
                  <button type="button" className="al-tool" onClick={handleFillWorkspaceExample} disabled={!isC1Enabled}>
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
                    disabled={!isC1Enabled}
                  />
                  <textarea
                    id="workspace-description-input"
                    value={state.workspaceDescriptionInput}
                    onChange={(event) => {
                      handleWorkspaceDescriptionChange(event.target.value);
                    }}
                    placeholder="Optional workspace description"
                    disabled={!isC1Enabled}
                  />
                  <button type="button" className="tb-btn tb-btn-primary" onClick={() => void handleCreateWorkspace()} disabled={!isC1Enabled}>
                    Create workspace
                  </button>
                </div>
              </div>
            </section>

            <section className="trace-view">
              <header className="tv-head">
                <div className="tv-title">
                  <i data-lucide="folders" />
                  <span>Workspace list</span>
                  <span className="tv-arch">{state.workspaces.length} total</span>
                </div>
              </header>
              <div className="tv-body">
                <div className="issues-box">
                  {state.workspaces.length === 0 ? (
                    <div className="issue-row info">No workspace yet. Create one to continue.</div>
                  ) : (
                    state.workspaces.map((workspace) => (
                      <div key={workspace.workspace_id} className={`issue-row info${workspace.workspace_id === state.activeWorkspaceId ? " selected-row" : ""}`}>
                        <div className="row-main">
                          <b>{workspace.name}</b> <span className="muted">({workspace.workspace_id})</span>
                          <div className="row-sub">{workspace.description || "No description"}</div>
                        </div>
                        <button
                          type="button"
                          className="sg-apply"
                          onClick={() => {
                            void handleSelectWorkspace(workspace.workspace_id);
                          }}
                        >
                          Open
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </section>

            <section className="arch-list">
              <header className="arch-list-head">
                <div className="al-label">Create project in active workspace</div>
                <div className="al-tools">
                  <button
                    type="button"
                    className="al-tool"
                    onClick={handleFillProjectExample}
                    disabled={!isC1Enabled || !state.activeWorkspaceId}
                  >
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
                    disabled={!isC1Enabled || !state.activeWorkspaceId}
                  />
                  <textarea
                    id="project-description-input"
                    value={state.projectDescriptionInput}
                    onChange={(event) => {
                      handleProjectDescriptionChange(event.target.value);
                    }}
                    placeholder="Optional project description"
                    disabled={!isC1Enabled || !state.activeWorkspaceId}
                  />
                  <button
                    type="button"
                    className="tb-btn tb-btn-primary"
                    onClick={() => {
                      void handleCreateProject();
                    }}
                    disabled={!isC1Enabled || !state.activeWorkspaceId}
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
          </main>

          <aside className="rail">
            <section className="rail-section">
              <div className="rail-label">Bottleneck found</div>
              <div className="rail-bottleneck">
                <div className="rb-top">
                  <div className="rb-icon">
                    <i data-lucide="triangle-alert" />
                  </div>
                  <div className="rb-id">{state.bottleneckId}</div>
                </div>
                <p className="rb-copy">{state.bottleneckText}</p>
              </div>
            </section>

            <section className="rail-section">
              <div className="rail-label">Suggested interventions</div>
              <div className="suggest">
                {state.suggestions.length === 0 ? (
                  <div className="sg-row">
                    <div>
                      <div className="sg-tag">Idle</div>
                      <div className="sg-title">No interventions yet</div>
                      <div className="sg-sub">Run C1 actions to generate actionable guidance.</div>
                    </div>
                    <button type="button" className="sg-apply" disabled>
                      Apply
                    </button>
                  </div>
                ) : (
                  state.suggestions.map((item, index) => (
                    <div className="sg-row" key={`${item.tag}-${index}`}>
                      <div>
                        <div className="sg-tag">{item.tag}</div>
                        <div className="sg-title">{item.title}</div>
                        <div className="sg-sub">{item.detail}</div>
                      </div>
                      <button type="button" className="sg-apply" disabled>
                        Apply
                      </button>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="rail-section">
              <div className="rail-label">Export</div>
              <button type="button" className="rail-export" onClick={handleExportPayload}>
                <i data-lucide="file-json-2" />
                Export C1 snapshot
              </button>
              <div className="rail-export-meta">{state.exportMeta}</div>
            </section>

            <section className="rail-section">
              <div className="rail-label">Active context</div>
              <div className="rail-export-meta">
                Workspace: {activeWorkspace?.name ?? "none"}
                <br />
                Project: {activeProject?.name ?? "none"}
              </div>
            </section>
          </aside>
        </div>
      </div>
    </div>
  );
}

