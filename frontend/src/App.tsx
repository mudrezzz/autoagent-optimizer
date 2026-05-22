import { useEffect, useMemo, useState } from "react";

import {
  createProject,
  createWorkspace,
  deleteWorkspace,
  duplicateWorkspace,
  fetchCapabilityCatalog,
  fetchStubCapability,
  getProject,
  listProjects,
  listWorkspaces,
  renameWorkspace,
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

// Русский комментарий: режим модалки workspace для создания/переименования.
type WorkspaceDialogMode = "create" | "rename" | null;

// Русский комментарий: структура состояния UI для C1 и planned-preview capability.
type UiState = {
  capabilities: Capability[];
  activeCapabilityId: string;
  workspaces: WorkspaceRecord[];
  activeWorkspaceId: string;
  projects: ProjectRecord[];
  activeProjectId: string;
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

  const [workspaceDialogMode, setWorkspaceDialogMode] = useState<WorkspaceDialogMode>(null);
  const [workspaceDialogWorkspaceId, setWorkspaceDialogWorkspaceId] = useState<string>("");
  const [workspaceDialogName, setWorkspaceDialogName] = useState<string>("");
  const [workspaceDialogDescription, setWorkspaceDialogDescription] = useState<string>("");
  const [workspaceMenuOpenId, setWorkspaceMenuOpenId] = useState<string | null>(null);

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

  // Русский комментарий: закрывает меню workspace-карточки при клике за пределами меню.
  useEffect(() => {
    const onDocumentClick = (event: MouseEvent): void => {
      const target = event.target as Element | null;
      if (!target) {
        return;
      }
      if (target.closest(".workspace-menu-wrap")) {
        return;
      }
      setWorkspaceMenuOpenId(null);
    };
    document.addEventListener("click", onDocumentClick);
    return () => {
      document.removeEventListener("click", onDocumentClick);
    };
  }, []);

  // Русский комментарий: закрывает модалку по Escape для удобства UX.
  useEffect(() => {
    const onEsc = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        closeWorkspaceDialog();
      }
    };
    document.addEventListener("keydown", onEsc);
    return () => {
      document.removeEventListener("keydown", onEsc);
    };
  });

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

  // Русский комментарий: открывает модалку создания workspace.
  function openCreateWorkspaceDialog(): void {
    setWorkspaceDialogMode("create");
    setWorkspaceDialogWorkspaceId("");
    setWorkspaceDialogName("");
    setWorkspaceDialogDescription("");
    setWorkspaceMenuOpenId(null);
  }

  // Русский комментарий: открывает модалку переименования выбранного workspace.
  function openRenameWorkspaceDialog(workspace: WorkspaceRecord): void {
    setWorkspaceDialogMode("rename");
    setWorkspaceDialogWorkspaceId(workspace.workspace_id);
    setWorkspaceDialogName(workspace.name);
    setWorkspaceDialogDescription(workspace.description);
    setWorkspaceMenuOpenId(null);
  }

  // Русский комментарий: закрывает модалку workspace и очищает временный draft.
  function closeWorkspaceDialog(): void {
    setWorkspaceDialogMode(null);
    setWorkspaceDialogWorkspaceId("");
    setWorkspaceDialogName("");
    setWorkspaceDialogDescription("");
  }

  // Русский комментарий: создает или переименовывает workspace из модалки в зависимости от режима.
  async function handleSubmitWorkspaceDialog(): Promise<void> {
    const name = workspaceDialogName.trim();
    if (!name) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: "Workspace name is required." }),
      }));
      return;
    }

    try {
      if (workspaceDialogMode === "create") {
        const created = await createWorkspace(name, workspaceDialogDescription.trim());
        await refreshWorkspaces(created.workspace.workspace_id);
        setState((prev) => ({
          ...prev,
          jsonText: prettyJson({ status: "success", action: "create_workspace", workspace: created.workspace }),
        }));
      } else if (workspaceDialogMode === "rename") {
        const updated = await renameWorkspace(workspaceDialogWorkspaceId, name);
        await refreshWorkspaces(updated.workspace.workspace_id);
        setState((prev) => ({
          ...prev,
          jsonText: prettyJson({ status: "success", action: "rename_workspace", workspace: updated.workspace }),
        }));
      }
      closeWorkspaceDialog();
    } catch (error) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: дублирует workspace из меню карточки.
  async function handleDuplicateWorkspace(workspaceId: string): Promise<void> {
    setWorkspaceMenuOpenId(null);
    try {
      const duplicated = await duplicateWorkspace(workspaceId);
      await refreshWorkspaces(duplicated.workspace.workspace_id);
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "success", action: "duplicate_workspace", workspace: duplicated.workspace }),
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: удаляет workspace из меню карточки после подтверждения пользователя.
  async function handleDeleteWorkspace(workspaceId: string): Promise<void> {
    setWorkspaceMenuOpenId(null);
    const confirmed = window.confirm("Delete this workspace? This action cannot be undone.");
    if (!confirmed) {
      return;
    }
    try {
      await deleteWorkspace(workspaceId);
      await refreshWorkspaces();
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "success", action: "delete_workspace", workspace_id: workspaceId }),
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
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

  // Русский комментарий: синхронизирует input названия project.
  function handleProjectNameChange(nextValue: string): void {
    setState((prev) => ({ ...prev, projectNameInput: nextValue }));
  }

  // Русский комментарий: синхронизирует input описания project.
  function handleProjectDescriptionChange(nextValue: string): void {
    setState((prev) => ({ ...prev, projectDescriptionInput: nextValue }));
  }

  // Русский комментарий: возвращает демонстрационные агрегаты карточки workspace для живого визуального заполнения.
  function buildWorkspaceCardMetrics(workspace: WorkspaceRecord, index: number): {
    agents: number;
    tests: number;
    dataRows: number;
    statusLabel: string;
  } {
    const seed = hashString(workspace.workspace_id) + index * 17;
    const agents = 2 + (seed % 8);
    const tests = 24 + (seed % 7) * 12;
    const dataRows = 120 + (seed % 9) * 80;
    const statusLabel = index === 0 ? "Champion" : "Baseline";
    return { agents, tests, dataRows, statusLabel };
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
                      Manage customer workspaces and open a project context for optimization lifecycle.
                    </p>
                  </div>
                  <div className="hub-actions">
                    <button type="button" className="btn btn-primary" onClick={openCreateWorkspaceDialog}>
                      <i data-lucide="plus" />
                      Add workspace
                    </button>
                  </div>
                </section>

                <section className="workspace-board">
                  <header className="workspace-board-head">
                    <div className="workspace-board-label">Workspaces</div>
                    <div className="workspace-board-count">{state.workspaces.length} total</div>
                  </header>

                  <div className="workspace-grid" id="workspace-grid">
                    {state.workspaces.length === 0 ? (
                      <div className="workspace-card workspace-card--empty">
                        No workspace yet. Click <b>Add workspace</b> to create the first one.
                      </div>
                    ) : (
                      state.workspaces.map((workspace, index) => {
                        const metrics = buildWorkspaceCardMetrics(workspace, index);
                        const isChampionCard = index === 0;
                        const isCardMenuOpen = workspaceMenuOpenId === workspace.workspace_id;
                        return (
                          <article
                            key={workspace.workspace_id}
                            className={`workspace-arch-card${isChampionCard ? " is-champion" : ""}`}
                          >
                            <div className="workspace-arch-head">
                              <div>
                                <div className="workspace-card-title">{workspace.name}</div>
                                <div className="workspace-card-meta">{workspace.workspace_id}</div>
                              </div>
                              <div className="workspace-head-actions">
                                <span className={`workspace-pill${isChampionCard ? " champ" : " base"}`}>
                                  <span className="dot" />
                                  {metrics.statusLabel}
                                </span>
                                <div className="workspace-menu-wrap">
                                  <button
                                    type="button"
                                    className="workspace-menu-trigger"
                                    onClick={(event) => {
                                      event.stopPropagation();
                                      setWorkspaceMenuOpenId((prev) =>
                                        prev === workspace.workspace_id ? null : workspace.workspace_id,
                                      );
                                    }}
                                  >
                                    <i data-lucide="ellipsis" />
                                  </button>
                                  {isCardMenuOpen ? (
                                    <div className="workspace-menu">
                                      <button
                                        type="button"
                                        className="workspace-menu-item"
                                        onClick={() => {
                                          openRenameWorkspaceDialog(workspace);
                                        }}
                                      >
                                        Rename
                                      </button>
                                      <button
                                        type="button"
                                        className="workspace-menu-item"
                                        onClick={() => {
                                          void handleDuplicateWorkspace(workspace.workspace_id);
                                        }}
                                      >
                                        Duplicate
                                      </button>
                                      <button
                                        type="button"
                                        className="workspace-menu-item is-destructive"
                                        onClick={() => {
                                          void handleDeleteWorkspace(workspace.workspace_id);
                                        }}
                                      >
                                        Delete
                                      </button>
                                    </div>
                                  ) : null}
                                </div>
                              </div>
                            </div>

                            <div className="workspace-arch-metrics">
                              <div className="workspace-metric">
                                <span className="m-val">{metrics.agents}</span>
                                <span className="m-lbl">agents</span>
                              </div>
                              <div className="workspace-metric">
                                <span className="m-val">{metrics.tests}</span>
                                <span className="m-lbl">tests</span>
                              </div>
                              <div className="workspace-metric">
                                <span className="m-val">{metrics.dataRows}</span>
                                <span className="m-lbl">data rows</span>
                              </div>
                            </div>

                            <div className="workspace-card-footer">
                              <div className="workspace-card-sub">{workspace.description || "No description"}</div>
                              <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={() => {
                                  void handleOpenWorkspace(workspace.workspace_id);
                                }}
                              >
                                Open workspace
                              </button>
                            </div>
                          </article>
                        );
                      })
                    )}
                  </div>
                </section>

                <section className="trace-view">
                  <header className="tv-head">
                    <div className="tv-title">
                      <i data-lucide="file-json-2" />
                      <span>Last C1 payload</span>
                    </div>
                  </header>
                  <div className="tv-body">
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

      {workspaceDialogMode ? (
        <div className="workspace-modal-overlay" onClick={closeWorkspaceDialog}>
          <div
            className="workspace-modal-card"
            onClick={(event) => {
              event.stopPropagation();
            }}
          >
            <div className="workspace-modal-title">
              {workspaceDialogMode === "create" ? "Create workspace" : "Rename workspace"}
            </div>
            <div className="workspace-modal-subtitle">
              {workspaceDialogMode === "create"
                ? "Add a new workspace for a separate optimization project."
                : "Update workspace display name."}
            </div>
            <div className="workspace-modal-form">
              <label htmlFor="workspace-dialog-name">Name</label>
              <input
                id="workspace-dialog-name"
                type="text"
                value={workspaceDialogName}
                onChange={(event) => {
                  setWorkspaceDialogName(event.target.value);
                }}
                placeholder="support-qa"
              />
              {workspaceDialogMode === "create" ? (
                <>
                  <label htmlFor="workspace-dialog-description">Description</label>
                  <textarea
                    id="workspace-dialog-description"
                    value={workspaceDialogDescription}
                    onChange={(event) => {
                      setWorkspaceDialogDescription(event.target.value);
                    }}
                    placeholder="Optional workspace description"
                  />
                </>
              ) : null}
            </div>
            <div className="workspace-modal-actions">
              <button type="button" className="btn btn-secondary" onClick={closeWorkspaceDialog}>
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => {
                  void handleSubmitWorkspaceDialog();
                }}
              >
                {workspaceDialogMode === "create" ? "Create workspace" : "Save name"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
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

// Русский комментарий: вычисляет простой стабильный hash для псевдо-детерминированных демо-метрик.
function hashString(value: string): number {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 31 + value.charCodeAt(index)) >>> 0;
  }
  return hash;
}
