import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent as ReactKeyboardEvent } from "react";

import {
  assignArenaDatasets,
  createArenaDataset,
  createArena,
  deleteArena,
  fetchArenaDatasetState,
  duplicateArena,
  fetchArenaPatternSelection,
  fetchArenaOptimizerState,
  fetchCapabilityCatalog,
  fetchStubCapability,
  getArena,
  getArenaChatState,
  listArenas,
  postArenaChatMessage,
  renameArena,
  replaceArenaDatasetRows,
  saveArenaPatternSelection,
  saveArenaDatasetVersion,
  saveArenaOptimizerSetup,
  saveArenaOptimizerVersion,
  saveArenaEvaluationEvaluators,
  saveArenaEvaluationMatrix,
  saveArenaEvaluationStageMappings,
  autoMapArenaEvaluationStageMappings,
  saveArenaEvaluationMetrics,
  saveArenaEvaluationVersion,
  suggestArenaEvaluationMetrics,
  applyArenaEvaluationMetricProposal,
  searchArenaPatterns,
  selectArenaDataset,
  selectArenaCandidatesForTests,
  launchArenaOptimizer,
  fetchArenaEvaluationState,
  validateArenaDataset,
  validateArenaEvaluationProfile,
  validateArenaOptimizerSetup,
} from "./api";
import type {
  ArenaRecord,
  C4ComparativeMetric,
  C2CandidateDraftItem,
  C2CandidateSetDraft,
  C2ChatMessage,
  C4DiagnosticSignal,
  C4DatasetDetail,
  C4DatasetRow,
  C4DatasetSummary,
  C4DatasetTargetStage,
  C4EvaluationBudget,
  C4EvaluatorMetricLink,
  C4StageMapping,
  C4StageMappingCoverage,
  C4StageBinding,
  C4StageBindingCoverage,
  C4EvaluationVersion,
  C4MetricProposal,
  C4Evaluator,
  C5OptimizerBudget,
  C5OptimizerControl,
  C5OptimizerLaunchEntry,
  C5OptimizerMethod,
  C5OptimizerRunPlan,
  C5OptimizerVersion,
  C3PatternItem,
  Capability,
  StubPayload,
} from "./types";
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
  { id: "c1", name: "Battle Registry", description: "Manage battle arenas.", status: "enabled", badge_count: 1 },
  { id: "c3", name: "Pattern Library + RAG", description: "Pattern retrieval controls for candidate generation.", status: "enabled", badge_count: 1 },
  {
    id: "c2",
    name: "Task Chat + Candidates",
    description: "Chat-driven task brief and candidate draft generation.",
    status: "enabled",
    badge_count: 1,
  },
  { id: "c4", name: "Datasets", description: "Manage dataset lifecycle for benchmark runs.", status: "enabled", badge_count: 1 },
  { id: "c5", name: "Metrics", description: "Define comparative and diagnostic metrics.", status: "enabled", badge_count: 1 },
  { id: "c5s", name: "Stage Mapping", description: "Map target stages to candidate runtime nodes.", status: "enabled", badge_count: 1 },
  { id: "c6", name: "Evaluators", description: "Configure evaluator adapters and matrix coverage.", status: "enabled", badge_count: 1 },
  { id: "c7", name: "Optimizer Run Monitor", description: "Optimizer setup, launch guardrails and run queue.", status: "enabled", badge_count: 1 },
  { id: "c8", name: "Report + Champion Export/Import", description: "Planned slice for reports and native loop.", status: "planned", badge_count: 0 },
];

// Русский комментарий: иконки capability для меню рабочего экрана battle.
const CAPABILITY_ICONS: Record<string, string> = {
  c1: "swords",
  c2: "messages-square",
  c3: "library",
  c4: "database",
  c5: "line-chart",
  c5s: "waypoints",
  c6: "shield-check",
  c7: "activity",
  c8: "package-check",
};

// Русский комментарий: список capability, для которых battle-чат поддерживает контекстные действия в v0.
const CHAT_SUPPORTED_CAPABILITY_IDS = new Set(["c2", "c4", "c5", "c5s", "c6", "c7"]);

// Русский комментарий: дефолтные contextual action для non-C2 шагов wizard.
const CHAT_DEFAULT_CONTEXT_ACTION_BY_CAPABILITY: Record<string, string> = {
  c4: "add_dataset_row",
  c5: "suggest_metrics",
  c5s: "auto_map_stage_mappings",
  c6: "autofill_matrix_links",
  c7: "validate_optimizer_setup",
};

// Русский комментарий: маршруты двух экранов - hub и workspace.
type ScreenRoute = { name: "battles_hub" } | { name: "battle_workspace"; arenaId: string };

// Русский комментарий: режим модалки арены.
type ArenaDialogMode = "create" | "rename" | null;

// Русский комментарий: состояние React-приложения для C1/C2 с planned-заглушками.
type UiState = {
  capabilities: Capability[];
  activeCapabilityId: string;
  arenas: ArenaRecord[];
  activeArenaId: string;
  c2ChatInput: string;
  c2Messages: C2ChatMessage[];
  c2CopilotResolvedAction: string;
  c2CopilotAllowedActions: string[];
  c2CopilotSummary: string;
  c2CandidateSetDraft: C2CandidateSetDraft | null;
  c2SelectedCandidateId: string;
  c2SelectedForTestsIds: string[];
  c2ExpandedCandidateId: string;
  debugDrawerOpen: boolean;
  c3PatternQuery: string;
  c3Patterns: C3PatternItem[];
  c3SelectedPatternIds: string[];
  c3SelectionDirty: boolean;
  c3SelectionUpdatedAt: string;
  c3SearchMeta: string;
  c3ExpandedPatternId: string;
  c4Datasets: C4DatasetSummary[];
  c4ActiveDatasetId: string;
  c4ActiveDataset: C4DatasetDetail | null;
  c4AssignedDatasetIds: string[];
  c4SelectedDatasetIds: string[];
  c4SelectionDirty: boolean;
  c4ExpandedDatasetId: string;
  c4StudioTab: "datasets" | "metrics";
  c4ViewMode: "list" | "edit";
  c4EditorDatasetId: string;
  c4EditorRows: C4DatasetRow[];
  c4EditorImportJsonl: string;
  c4ComparativeMetrics: C4ComparativeMetric[];
  c4DiagnosticSignals: C4DiagnosticSignal[];
  c4Evaluators: C4Evaluator[];
  c4StageMappings: C4StageMapping[];
  c4StageMappingCoverage: C4StageMappingCoverage[];
  c4StageBindings: C4StageBinding[];
  c4StageBindingCoverage: C4StageBindingCoverage[];
  c4EvaluatorMetricLinks: C4EvaluatorMetricLink[];
  c4EvaluationBudget: C4EvaluationBudget;
  c4EvaluationVersions: C4EvaluationVersion[];
  c4MetricProposal: C4MetricProposal | null;
  c4SelectedMetricProposalItemIds: string[];
  c4EvaluationValidationStatus: "not_run" | "ready" | "warnings" | "invalid";
  c4EvaluationValidationIssues: Array<{ severity: string; code: string; message: string }>;
  c4CandidateFeatures: Record<string, boolean>;
  c5Methods: C5OptimizerMethod[];
  c5Controls: C5OptimizerControl[];
  c5RunPlan: C5OptimizerRunPlan;
  c5Budget: C5OptimizerBudget;
  c5Versions: C5OptimizerVersion[];
  c5LaunchHistory: C5OptimizerLaunchEntry[];
  c5ValidationStatus: "not_run" | "ready" | "warnings" | "invalid";
  c5ValidationIssues: Array<{ severity: string; code: string; message: string }>;
  c4NewDatasetName: string;
  c4NewDatasetDescription: string;
  c4ValidationIssues: Array<{ severity: string; code: string; row_index: number | null; message: string }>;
  c4ValidationStatus: string;
  budgetPercent: number;
  budgetStage: string;
  metricArenas: string;
  metricArenaStatus: string;
  jsonText: string;
  exportMeta: string;
  lastPayload: Record<string, unknown> | null;
};

// Русский комментарий: статус шага wizard-навигации внутри Battle Workspace.
type WizardStepStatus = "locked" | "available" | "in_progress" | "completed" | "blocked";

// Русский комментарий: расширенная модель capability для рендера wizard-меню.
type CapabilityWizardItem = Capability & {
  wizardStatus: WizardStepStatus;
  wizardReason: string;
  isInteractive: boolean;
};

// Русский комментарий: корневой компонент frontend shell.
export function App(): JSX.Element {
  const [route, setRoute] = useState<ScreenRoute>(() => parseRoute(window.location.pathname));
  const [state, setState] = useState<UiState>({
    capabilities: FALLBACK_CAPABILITIES,
    activeCapabilityId: "c3",
    arenas: [],
    activeArenaId: "",
    c2ChatInput: "",
    c2Messages: [],
    c2CopilotResolvedAction: "",
    c2CopilotAllowedActions: [],
    c2CopilotSummary: "",
    c2CandidateSetDraft: null,
    c2SelectedCandidateId: "",
    c2SelectedForTestsIds: [],
    c2ExpandedCandidateId: "",
    debugDrawerOpen: false,
    c3PatternQuery: "",
    c3Patterns: [],
    c3SelectedPatternIds: [],
    c3SelectionDirty: false,
    c3SelectionUpdatedAt: "",
    c3SearchMeta: "No C3 search yet.",
    c3ExpandedPatternId: "",
    c4Datasets: [],
    c4ActiveDatasetId: "",
    c4ActiveDataset: null,
    c4AssignedDatasetIds: [],
    c4SelectedDatasetIds: [],
    c4SelectionDirty: false,
    c4ExpandedDatasetId: "",
    c4StudioTab: "datasets",
    c4ViewMode: "list",
    c4EditorDatasetId: "",
    c4EditorRows: [],
    c4EditorImportJsonl: "",
    c4ComparativeMetrics: [],
    c4DiagnosticSignals: [],
    c4Evaluators: [],
    c4StageMappings: [],
    c4StageMappingCoverage: [],
    c4StageBindings: [],
    c4StageBindingCoverage: [],
    c4EvaluatorMetricLinks: [],
    c4EvaluationBudget: { max_cases: 0, max_llm_calls: 0, max_cost_usd: 0 },
    c4EvaluationVersions: [],
    c4MetricProposal: null,
    c4SelectedMetricProposalItemIds: [],
    c4EvaluationValidationStatus: "not_run",
    c4EvaluationValidationIssues: [],
    c4CandidateFeatures: {},
    c5Methods: [],
    c5Controls: [],
    c5RunPlan: { epochs_total: 0, candidates_per_epoch: 0, max_parallel_trials: 0, early_stop_patience: 0 },
    c5Budget: { max_cases: 0, max_llm_calls: 0, max_cost_usd: 0, max_runtime_minutes: 0 },
    c5Versions: [],
    c5LaunchHistory: [],
    c5ValidationStatus: "not_run",
    c5ValidationIssues: [],
    c4NewDatasetName: "",
    c4NewDatasetDescription: "",
    c4ValidationIssues: [],
    c4ValidationStatus: "not_run",
    budgetPercent: 0,
    budgetStage: "idle",
    metricArenas: "0",
    metricArenaStatus: "not selected",
    jsonText: "Run C1/C2 actions to see API payloads.",
    exportMeta: "No payload available yet.",
    lastPayload: null,
  });
  const [arenaDialogMode, setArenaDialogMode] = useState<ArenaDialogMode>(null);
  const [arenaDialogArenaId, setArenaDialogArenaId] = useState<string>("");
  const [arenaDialogName, setArenaDialogName] = useState<string>("");
  const [arenaDialogDescription, setArenaDialogDescription] = useState<string>("");
  const [arenaMenuOpenId, setArenaMenuOpenId] = useState<string | null>(null);
  const chatMessagesRef = useRef<HTMLDivElement | null>(null);
  const c4StageMappingAutoInitRef = useRef<Record<string, boolean>>({});

  // Русский комментарий: активная capability для контентной панели.
  const activeCapability = useMemo(
    () => state.capabilities.find((item) => item.id === state.activeCapabilityId) ?? FALLBACK_CAPABILITIES[0],
    [state.capabilities, state.activeCapabilityId],
  );

  // Русский комментарий: активная арена по выбранному id.
  const activeArena = useMemo(
    () => state.arenas.find((item) => item.workspace_id === state.activeArenaId) ?? null,
    [state.arenas, state.activeArenaId],
  );

  // Русский комментарий: в матрице Evaluator x Metric показываем только включенные evaluators.
  const enabledC4Evaluators = useMemo(
    () => state.c4Evaluators.filter((item) => item.enabled),
    [state.c4Evaluators],
  );

  // Русский комментарий: индекс coverage по mapping_id для быстрого рендера C6 Stage mapping таблицы.
  const c4StageCoverageByMappingId = useMemo(() => {
    const index = new Map<string, C4StageMappingCoverage>();
    for (const item of state.c4StageMappingCoverage) {
      if (!item?.mapping_id) {
        continue;
      }
      index.set(item.mapping_id, item);
    }
    return index;
  }, [state.c4StageMappingCoverage]);

  // Русский комментарий: workspace-меню работает как wizard с вычисляемыми статусами шагов.
  const capabilityWizardItems = useMemo(
    () => buildCapabilityWizardItems(state.capabilities, state, route.name === "battle_workspace"),
    [state.capabilities, state, route.name],
  );

  // Русский комментарий: загрузка capability-каталога.
  useEffect(() => {
    void (async () => {
      try {
        const catalog = await fetchCapabilityCatalog();
        setState((prev) => ({ ...prev, capabilities: ensureStageMappingCapability(catalog.capabilities) }));
      } catch {
        // Русский комментарий: fallback остается активным.
      }
    })();
  }, []);

  // Русский комментарий: первичная загрузка арен.
  useEffect(() => {
    void refreshArenas();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Русский комментарий: синхронизация route-state на popstate.
  useEffect(() => {
    const onPopState = (): void => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  // Русский комментарий: при переходе в workspace загружаем контекст арены.
  useEffect(() => {
    if (route.name !== "battle_workspace" || !route.arenaId) {
      return;
    }
    void loadArenaContext(route.arenaId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [route]);

  // Русский комментарий: закрывает меню карточки при клике вне зоны меню.
  useEffect(() => {
    const onDocumentClick = (event: MouseEvent): void => {
      const target = event.target as Element | null;
      if (target && target.closest(".workspace-menu-wrap")) {
        return;
      }
      setArenaMenuOpenId(null);
    };
    document.addEventListener("click", onDocumentClick);
    return () => document.removeEventListener("click", onDocumentClick);
  }, []);

  // Русский комментарий: закрытие модалки по клавише Escape.
  useEffect(() => {
    const onEsc = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        closeArenaDialog();
      }
    };
    document.addEventListener("keydown", onEsc);
    return () => document.removeEventListener("keydown", onEsc);
  });

  // Русский комментарий: переинициализация lucide-иконок после рендера.
  useEffect(() => {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  });

  // Русский комментарий: автоматически прокручивает chat-ленту к последнему сообщению.
  useEffect(() => {
    if (!chatMessagesRef.current) {
      return;
    }
    chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
  }, [state.c2Messages]);

  // Русский комментарий: при входе в Stage Mapping шаг автоматически инициализирует mapping, если строк еще нет.
  useEffect(() => {
    if (state.activeCapabilityId !== "c5s" || !state.activeArenaId) {
      return;
    }
    if (state.c4StageMappings.length > 0) {
      c4StageMappingAutoInitRef.current[state.activeArenaId] = true;
      return;
    }
    if (c4StageMappingAutoInitRef.current[state.activeArenaId]) {
      return;
    }
    c4StageMappingAutoInitRef.current[state.activeArenaId] = true;
    void handleAutoInitC4StageMappings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.activeCapabilityId, state.activeArenaId, state.c4StageMappings.length]);

  // Русский комментарий: переход на hub.
  function navigateToBattlesHub(): void {
    window.history.pushState({}, "", "/battles");
    setRoute({ name: "battles_hub" });
    setState((prev) => ({
      ...prev,
      activeCapabilityId: "c3",
      activeArenaId: "",
      c2ChatInput: "",
      c2Messages: [],
      c2CopilotResolvedAction: "",
      c2CopilotAllowedActions: [],
      c2CopilotSummary: "",
      c2CandidateSetDraft: null,
      c2SelectedCandidateId: "",
      c2SelectedForTestsIds: [],
      c2ExpandedCandidateId: "",
      debugDrawerOpen: false,
      c3PatternQuery: "",
      c3Patterns: [],
      c3SelectedPatternIds: [],
      c3SelectionDirty: false,
      c3SelectionUpdatedAt: "",
      c3SearchMeta: "No C3 search yet.",
      c3ExpandedPatternId: "",
      c4Datasets: [],
      c4ActiveDatasetId: "",
      c4ActiveDataset: null,
      c4AssignedDatasetIds: [],
      c4SelectedDatasetIds: [],
      c4SelectionDirty: false,
      c4ExpandedDatasetId: "",
      c4StudioTab: "datasets",
      c4ViewMode: "list",
      c4EditorDatasetId: "",
      c4EditorRows: [],
      c4EditorImportJsonl: "",
      c4ComparativeMetrics: [],
      c4DiagnosticSignals: [],
      c4Evaluators: [],
      c4StageMappings: [],
      c4StageMappingCoverage: [],
      c4StageBindings: [],
      c4StageBindingCoverage: [],
      c4EvaluatorMetricLinks: [],
      c4EvaluationBudget: { max_cases: 0, max_llm_calls: 0, max_cost_usd: 0 },
      c4EvaluationVersions: [],
      c4EvaluationValidationStatus: "not_run",
      c4EvaluationValidationIssues: [],
      c4CandidateFeatures: {},
      c5Methods: [],
      c5Controls: [],
      c5RunPlan: { epochs_total: 0, candidates_per_epoch: 0, max_parallel_trials: 0, early_stop_patience: 0 },
      c5Budget: { max_cases: 0, max_llm_calls: 0, max_cost_usd: 0, max_runtime_minutes: 0 },
      c5Versions: [],
      c5LaunchHistory: [],
      c5ValidationStatus: "not_run",
      c5ValidationIssues: [],
      c4NewDatasetName: "",
      c4NewDatasetDescription: "",
      c4ValidationIssues: [],
      c4ValidationStatus: "not_run",
      metricArenaStatus: "not selected",
    }));
  }

  // Русский комментарий: переход в workspace выбранной арены.
  function navigateToArenaWorkspace(arenaId: string): void {
    window.history.pushState({}, "", `/battles/${encodeURIComponent(arenaId)}`);
    setRoute({ name: "battle_workspace", arenaId });
  }

  // Русский комментарий: загрузка списка арен.
  async function refreshArenas(preferredArenaId?: string): Promise<void> {
    try {
      const arenasResponse = await listArenas();
      const arenas = arenasResponse.arenas;
      let nextArenaId = "";
      if (preferredArenaId && arenas.some((item) => item.workspace_id === preferredArenaId)) {
        nextArenaId = preferredArenaId;
      } else if (route.name === "battle_workspace" && arenas.some((item) => item.workspace_id === route.arenaId)) {
        nextArenaId = route.arenaId;
      }

      const snapshot = { status: "success", c1_slice: "battle_registry_v0", arenas, active_arena_id: nextArenaId };
      setState((prev) => ({
        ...prev,
        arenas,
        activeArenaId: nextArenaId,
        metricArenas: String(arenas.length),
        metricArenaStatus: nextArenaId ? "selected" : "not selected",
        budgetPercent: 100,
        budgetStage: "loaded",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
      if (route.name === "battle_workspace" && nextArenaId === "") {
        navigateToBattlesHub();
      }
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: загрузка C2-контекста по арене.
  async function loadArenaContext(arenaId: string): Promise<void> {
    setState((prev) => ({ ...prev, activeArenaId: arenaId, budgetStage: "loading battle", budgetPercent: 40 }));
    try {
      const arenaResponse = await getArena(arenaId);
      const chatResponse = await getArenaChatState(arenaId);
      const snapshot = {
        status: "success",
        action: "open_battle_workspace",
        arena: arenaResponse.arena,
        messages_total: chatResponse.messages_total,
        candidate_set_id: chatResponse.candidate_set_draft?.candidate_set_id ?? null,
      };
      setState((prev) => ({
        ...prev,
        activeArenaId: arenaId,
        c2Messages: chatResponse.messages,
        c2CopilotResolvedAction: "",
        c2CopilotAllowedActions: [],
        c2CopilotSummary: "",
        c2CandidateSetDraft: chatResponse.candidate_set_draft,
        c2SelectedCandidateId: chatResponse.candidate_set_draft?.candidates[0]?.candidate_id ?? "",
        c2SelectedForTestsIds:
          chatResponse.candidate_set_draft?.candidates
            .filter((candidate) => Boolean(candidate.selected_for_tests))
            .map((candidate) => candidate.candidate_id) ?? [],
        c2ExpandedCandidateId: "",
        metricArenaStatus: "selected",
        budgetPercent: 100,
        budgetStage: "battle ready",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
      await loadC3PatternState(arenaId, "", false);
      await loadC4DatasetState(arenaId, false);
      await loadC4EvaluationState(arenaId, false);
      await loadC5OptimizerState(arenaId, false);
    } catch (error) {
      setState((prev) => ({
        ...prev,
        c2Messages: [],
        c2CopilotResolvedAction: "",
        c2CopilotAllowedActions: [],
        c2CopilotSummary: "",
        c2CandidateSetDraft: null,
        c2SelectedCandidateId: "",
        c2ExpandedCandidateId: "",
        c3Patterns: [],
        c3SelectedPatternIds: [],
        c3SelectionDirty: false,
        c3SelectionUpdatedAt: "",
        c3SearchMeta: "No C3 search yet.",
        c3ExpandedPatternId: "",
        c4Datasets: [],
        c4ActiveDatasetId: "",
        c4ActiveDataset: null,
        c4AssignedDatasetIds: [],
        c4SelectedDatasetIds: [],
        c4SelectionDirty: false,
        c4ExpandedDatasetId: "",
        c4StudioTab: "datasets",
        c4ViewMode: "list",
        c4EditorDatasetId: "",
        c4EditorRows: [],
        c4EditorImportJsonl: "",
        c4ComparativeMetrics: [],
        c4DiagnosticSignals: [],
        c4Evaluators: [],
        c4StageMappings: [],
        c4StageMappingCoverage: [],
        c4StageBindings: [],
        c4StageBindingCoverage: [],
        c4EvaluatorMetricLinks: [],
        c4EvaluationBudget: { max_cases: 0, max_llm_calls: 0, max_cost_usd: 0 },
        c4EvaluationVersions: [],
        c4EvaluationValidationStatus: "not_run",
        c4EvaluationValidationIssues: [],
        c4CandidateFeatures: {},
        c5Methods: [],
        c5Controls: [],
        c5RunPlan: { epochs_total: 0, candidates_per_epoch: 0, max_parallel_trials: 0, early_stop_patience: 0 },
        c5Budget: { max_cases: 0, max_llm_calls: 0, max_cost_usd: 0, max_runtime_minutes: 0 },
        c5Versions: [],
        c5LaunchHistory: [],
        c5ValidationStatus: "not_run",
        c5ValidationIssues: [],
        c4ValidationIssues: [],
        c4ValidationStatus: "not_run",
        budgetPercent: 100,
        budgetStage: "failed",
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Русский комментарий: загружает C3 pattern selection и результаты поиска для выбранной арены.
  async function loadC3PatternState(arenaId: string, query: string, writeSnapshot = true): Promise<void> {
    const normalizedQuery = query.trim();
    const selectionResponse = await fetchArenaPatternSelection(arenaId);
    const searchResponse = await searchArenaPatterns(arenaId, normalizedQuery, 12);
    const selectedPatternIds = selectionResponse.selection.include_pattern_ids;
    const snapshot = {
      status: "success",
      capability_id: "c3",
      action: "search_patterns",
      arena_id: arenaId,
      query: searchResponse.query,
      returned: searchResponse.returned,
      selected_total: selectedPatternIds.length,
    };
    setState((prev) => ({
      ...prev,
      c3PatternQuery: normalizedQuery,
      c3Patterns: searchResponse.patterns,
      c3SelectedPatternIds: selectedPatternIds,
      c3SelectionDirty: false,
      c3SelectionUpdatedAt: selectionResponse.selection.updated_at,
      c3SearchMeta: `results ${searchResponse.returned}/${searchResponse.total_candidates} · query "${searchResponse.query}"`,
      c3ExpandedPatternId:
        prev.c3ExpandedPatternId && searchResponse.patterns.some((pattern) => pattern.pattern_id === prev.c3ExpandedPatternId)
          ? prev.c3ExpandedPatternId
          : "",
      jsonText: writeSnapshot ? prettyJson(snapshot) : prev.jsonText,
      lastPayload: writeSnapshot ? snapshot : prev.lastPayload,
      budgetStage: writeSnapshot ? "c3 patterns loaded" : prev.budgetStage,
      budgetPercent: writeSnapshot ? 100 : prev.budgetPercent,
    }));
  }

  // Русский комментарий: локально переключает выбранность паттерна до явного сохранения кнопкой Save.
  function handleToggleC3PatternSelection(patternId: string): void {
    setState((prev) => {
      const selectedSet = new Set(prev.c3SelectedPatternIds);
      if (selectedSet.has(patternId)) {
        selectedSet.delete(patternId);
      } else {
        selectedSet.add(patternId);
      }
      return {
        ...prev,
        c3SelectedPatternIds: Array.from(selectedSet),
        c3SelectionDirty: true,
      };
    });
  }

  // Русский комментарий: сохраняет выбранные паттерны в backend (только selected-модель без exclude).
  async function handleSaveC3PatternSelection(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "saving c3 selection", budgetPercent: 55 }));
    try {
      const selectedPatternIds = [...state.c3SelectedPatternIds];
      const saveResponse = await saveArenaPatternSelection(state.activeArenaId, selectedPatternIds, []);
      const searchResponse = await searchArenaPatterns(state.activeArenaId, state.c3PatternQuery, 12);
      const snapshot = {
        status: "success",
        capability_id: "c3",
        action: "update_pattern_selection",
        arena_id: state.activeArenaId,
        selection: saveResponse.selection,
        selected_total: saveResponse.selection.include_pattern_ids.length,
        returned: searchResponse.returned,
      };
      setState((prev) => ({
        ...prev,
        c3Patterns: searchResponse.patterns,
        c3SelectedPatternIds: saveResponse.selection.include_pattern_ids,
        c3SelectionDirty: false,
        c3SelectionUpdatedAt: saveResponse.selection.updated_at,
        c3SearchMeta: `results ${searchResponse.returned}/${searchResponse.total_candidates} · query "${searchResponse.query}"`,
        c3ExpandedPatternId:
          prev.c3ExpandedPatternId && searchResponse.patterns.some((pattern) => pattern.pattern_id === prev.c3ExpandedPatternId)
            ? prev.c3ExpandedPatternId
            : "",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
        budgetPercent: 100,
        budgetStage: "c3 selection saved",
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: выполняет поиск C3 паттернов по текущей строке запроса.
  async function handleC3Search(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "searching c3 patterns", budgetPercent: 50 }));
    try {
      await loadC3PatternState(state.activeArenaId, state.c3PatternQuery, true);
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: загружает состояние C4 Dataset Studio для активной арены.
  async function loadC4DatasetState(arenaId: string, writeSnapshot = true): Promise<void> {
    const response = await fetchArenaDatasetState(arenaId);
    const snapshot = {
      status: "success",
      capability_id: "c4",
      action: "load_dataset_studio",
      arena_id: arenaId,
      datasets_total: response.datasets.length,
      active_dataset_id: response.active_dataset_id,
      rows_total: response.active_dataset?.rows_total ?? 0,
      versions_total: response.active_dataset?.versions_total ?? 0,
    };
    setState((prev) => ({
      ...prev,
      c4Datasets: response.datasets,
      c4ActiveDatasetId: response.active_dataset_id,
      c4ActiveDataset: response.active_dataset,
      c4AssignedDatasetIds: response.assigned_dataset_ids,
      c4SelectedDatasetIds: response.assigned_dataset_ids,
      c4SelectionDirty: false,
      c4ExpandedDatasetId: "",
      c4StudioTab: "datasets",
      c4ViewMode: "list",
      c4EditorDatasetId: "",
      c4EditorRows: [],
      c4EditorImportJsonl: "",
      c4ValidationIssues: [],
      c4ValidationStatus: "not_run",
      budgetPercent: writeSnapshot ? 100 : prev.budgetPercent,
      budgetStage: writeSnapshot ? "c4 dataset studio ready" : prev.budgetStage,
      jsonText: writeSnapshot ? prettyJson(snapshot) : prev.jsonText,
      lastPayload: writeSnapshot ? snapshot : prev.lastPayload,
    }));
  }

  // Русский комментарий: загружает состояние C4 Metrics & Evaluators Studio для активной арены.
  async function loadC4EvaluationState(arenaId: string, writeSnapshot = true): Promise<void> {
    const response = await fetchArenaEvaluationState(arenaId);
    const snapshot = {
      status: "success",
      capability_id: "c4",
      action: "load_evaluation_studio",
      arena_id: arenaId,
      comparative_total: response.comparative_metrics.length,
      diagnostic_total: response.diagnostic_signals.length,
      evaluators_total: response.evaluators.length,
    };
    setState((prev) => ({
      ...prev,
      c4ComparativeMetrics: response.comparative_metrics,
      c4DiagnosticSignals: response.diagnostic_signals,
      c4Evaluators: response.evaluators,
      c4StageMappings: response.stage_mappings ?? [],
      c4StageMappingCoverage: response.stage_mapping_coverage ?? [],
      c4StageBindings: response.stage_bindings ?? [],
      c4StageBindingCoverage: response.stage_binding_coverage ?? [],
      c4EvaluatorMetricLinks: response.evaluator_metric_links,
      c4CandidateFeatures: response.candidate_features ?? {},
      c4EvaluationBudget: response.budget,
      c4EvaluationVersions: response.versions,
      c4MetricProposal: response.latest_metric_proposal ?? null,
      c4SelectedMetricProposalItemIds: buildDefaultMetricProposalSelection(response.latest_metric_proposal ?? null),
      c4EvaluationValidationStatus: "not_run",
      c4EvaluationValidationIssues: [],
      budgetPercent: writeSnapshot ? 100 : prev.budgetPercent,
      budgetStage: writeSnapshot ? "c4 evaluation studio ready" : prev.budgetStage,
      jsonText: writeSnapshot ? prettyJson(snapshot) : prev.jsonText,
      lastPayload: writeSnapshot ? snapshot : prev.lastPayload,
    }));
  }

  // Русский комментарий: загружает состояние C5 Optimizer Setup Studio для активной арены.
  async function loadC5OptimizerState(arenaId: string, writeSnapshot = true): Promise<void> {
    const response = await fetchArenaOptimizerState(arenaId);
    const snapshot = {
      status: "success",
      capability_id: "c5",
      action: "load_optimizer_setup",
      arena_id: arenaId,
      methods_total: response.methods.length,
      controls_total: response.controls.length,
      versions_total: response.versions.length,
      launches_total: response.launch_history.length,
    };
    setState((prev) => ({
      ...prev,
      c5Methods: response.methods,
      c5Controls: response.controls,
      c5RunPlan: response.run_plan,
      c5Budget: response.budget,
      c5Versions: response.versions,
      c5LaunchHistory: response.launch_history,
      c5ValidationStatus: "not_run",
      c5ValidationIssues: [],
      budgetPercent: writeSnapshot ? 100 : prev.budgetPercent,
      budgetStage: writeSnapshot ? "c5 optimizer setup ready" : prev.budgetStage,
      jsonText: writeSnapshot ? prettyJson(snapshot) : prev.jsonText,
      lastPayload: writeSnapshot ? snapshot : prev.lastPayload,
    }));
  }

  // Русский комментарий: создает dataset в C4 и обновляет UI-состояние.
  async function handleCreateC4Dataset(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    const name = state.c4NewDatasetName.trim();
    if (!name) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "Dataset name is required." }) }));
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "creating dataset", budgetPercent: 55 }));
    try {
      const response = await createArenaDataset(state.activeArenaId, name, state.c4NewDatasetDescription.trim());
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "create_dataset",
        arena_id: state.activeArenaId,
        dataset_id: response.dataset?.dataset_id ?? response.active_dataset_id,
        datasets_total: response.datasets.length,
      };
      setState((prev) => ({
        ...prev,
        c4Datasets: response.datasets,
        c4ActiveDatasetId: response.active_dataset_id,
        c4ActiveDataset: response.active_dataset,
        c4AssignedDatasetIds: response.assigned_dataset_ids,
        c4SelectedDatasetIds: response.assigned_dataset_ids,
        c4SelectionDirty: false,
        c4ExpandedDatasetId: "",
        c4StudioTab: "datasets",
        c4ViewMode: "list",
        c4EditorDatasetId: "",
        c4EditorRows: [],
        c4EditorImportJsonl: "",
        c4NewDatasetName: "",
        c4NewDatasetDescription: "",
        c4ValidationIssues: [],
        c4ValidationStatus: "not_run",
        budgetPercent: 100,
        budgetStage: "dataset created",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: переключает активный dataset в C4.
  async function handleSelectC4Dataset(datasetId: string): Promise<void> {
    if (!state.activeArenaId || !datasetId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "loading dataset", budgetPercent: 50 }));
    try {
      const response = await selectArenaDataset(state.activeArenaId, datasetId);
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "select_dataset",
        arena_id: state.activeArenaId,
        active_dataset_id: response.active_dataset_id,
      };
      setState((prev) => ({
        ...prev,
        c4Datasets: response.datasets,
        c4ActiveDatasetId: response.active_dataset_id,
        c4ActiveDataset: response.active_dataset,
        c4AssignedDatasetIds: response.assigned_dataset_ids,
        c4SelectedDatasetIds: prev.c4SelectionDirty ? prev.c4SelectedDatasetIds : response.assigned_dataset_ids,
        c4ValidationIssues: [],
        c4ValidationStatus: "not_run",
        budgetPercent: 100,
        budgetStage: "dataset selected",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: переключает локальный чекбокс выбора dataset для арены до явного сохранения кнопкой Save.
  function handleToggleC4DatasetSelection(datasetId: string): void {
    setState((prev) => {
      const selectedSet = new Set(prev.c4SelectedDatasetIds);
      if (selectedSet.has(datasetId)) {
        selectedSet.delete(datasetId);
      } else {
        selectedSet.add(datasetId);
      }
      return {
        ...prev,
        c4SelectedDatasetIds: Array.from(selectedSet),
        c4SelectionDirty: true,
      };
    });
  }

  // Русский комментарий: сохраняет назначение dataset-ов на арену явным действием Save.
  async function handleSaveC4DatasetAssignment(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "saving dataset assignment", budgetPercent: 60 }));
    try {
      const response = await assignArenaDatasets(state.activeArenaId, state.c4SelectedDatasetIds);
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "assign_datasets",
        arena_id: state.activeArenaId,
        assigned_dataset_ids: response.assigned_dataset_ids,
      };
      setState((prev) => ({
        ...prev,
        c4Datasets: response.datasets,
        c4ActiveDatasetId: response.active_dataset_id,
        c4ActiveDataset: response.active_dataset,
        c4AssignedDatasetIds: response.assigned_dataset_ids,
        c4SelectedDatasetIds: response.assigned_dataset_ids,
        c4SelectionDirty: false,
        budgetPercent: 100,
        budgetStage: "dataset assignment saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: раскрывает/сворачивает details-панель конкретного dataset в общем списке.
  function handleToggleC4DatasetDetails(datasetId: string): void {
    setState((prev) => ({
      ...prev,
      c4ExpandedDatasetId: prev.c4ExpandedDatasetId === datasetId ? "" : datasetId,
    }));
  }

  // Русский комментарий: открывает отдельный экран редактирования dataset с хлебными крошками.
  async function handleOpenC4DatasetEditor(datasetId: string): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "opening dataset editor", budgetPercent: 50 }));
    try {
      const response = await selectArenaDataset(state.activeArenaId, datasetId);
      const activeDataset = response.active_dataset;
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: "open_dataset_editor",
        arena_id: state.activeArenaId,
        dataset_id: response.active_dataset_id,
        rows_total: activeDataset?.rows_total ?? 0,
      };
      setState((prev) => ({
        ...prev,
        c4Datasets: response.datasets,
        c4ActiveDatasetId: response.active_dataset_id,
        c4ActiveDataset: activeDataset,
        c4AssignedDatasetIds: response.assigned_dataset_ids,
        c4SelectedDatasetIds: prev.c4SelectionDirty ? prev.c4SelectedDatasetIds : response.assigned_dataset_ids,
        c4ViewMode: "edit",
        c4EditorDatasetId: response.active_dataset_id,
        c4EditorRows: activeDataset?.rows.map((row) => ({ ...row })) ?? [],
        c4EditorImportJsonl: "",
        c4ValidationIssues: [],
        c4ValidationStatus: "not_run",
        budgetPercent: 100,
        budgetStage: "dataset editor ready",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: возвращает пользователя из editor-режима к общему списку dataset-ов.
  function handleBackToC4DatasetList(): void {
    setState((prev) => ({
      ...prev,
      c4ViewMode: "list",
      c4EditorDatasetId: "",
      c4EditorRows: [],
      c4EditorImportJsonl: "",
      c4ValidationIssues: [],
      c4ValidationStatus: "not_run",
    }));
  }

  // Русский комментарий: обновляет поле строки в editor-таблице dataset.
  function handleUpdateC4EditorRowField(
    rowIndex: number,
    field: "case_id" | "input" | "target_stage" | "expected" | "notes",
    value: string,
  ): void {
    setState((prev) => ({
      ...prev,
      c4EditorRows: prev.c4EditorRows.map((row, index) => {
        if (index !== rowIndex) {
          return row;
        }
        if (field === "target_stage") {
          const nextStage = normalizeDatasetTargetStage(value);
          const nextPayload = normalizeExpectedPayloadFromEditorInput({
            targetStage: nextStage,
            expected: row.expected,
            expectedPayload: row.expected_payload,
          });
          return {
            ...row,
            target_stage: nextStage,
            expected_payload: nextPayload,
            expected: stringifyExpectedPayloadForEditor(nextStage, nextPayload),
          };
        }
        if (field === "expected") {
          const currentStage = normalizeDatasetTargetStage(row.target_stage);
          const nextPayload = normalizeExpectedPayloadFromEditorInput({
            targetStage: currentStage,
            expected: value,
            expectedPayload: row.expected_payload,
          });
          return {
            ...row,
            expected: value,
            expected_payload: nextPayload,
          };
        }
        return { ...row, [field]: value };
      }),
    }));
  }

  // Русский комментарий: добавляет пустую строку в editor для ручного редактирования dataset.
  function handleAddC4EditorRow(): void {
    setState((prev) => ({
      ...prev,
      c4EditorRows: [
        ...prev.c4EditorRows,
        {
          case_id: "",
          input: "",
          target_stage: "final",
          expected_payload: { answer: "" },
          expected: "",
          notes: "",
        },
      ],
    }));
  }

  // Русский комментарий: удаляет выбранную строку из editor-таблицы dataset.
  function handleDeleteC4EditorRow(rowIndex: number): void {
    setState((prev) => ({
      ...prev,
      c4EditorRows: prev.c4EditorRows.filter((_, index) => index !== rowIndex),
    }));
  }

  // Русский комментарий: заменяет editor-содержимое dataset через JSONL-текст.
  function handleImportC4EditorJsonl(): void {
    const lines = state.c4EditorImportJsonl
      .split(/\r?\n/)
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
    if (lines.length === 0) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "JSONL payload is empty." }) }));
      return;
    }
    const parsedRows: C4DatasetRow[] = [];
    try {
      for (const line of lines) {
        const parsed = JSON.parse(line) as Record<string, unknown>;
        const targetStage = normalizeDatasetTargetStage(parsed.target_stage);
        const expectedPayload = normalizeExpectedPayloadFromEditorInput({
          targetStage,
          expected: parsed.expected,
          expectedPayload: parsed.expected_payload,
        });
        parsedRows.push({
          case_id: String(parsed.case_id ?? ""),
          input: String(parsed.input ?? parsed.query ?? ""),
          target_stage: targetStage,
          expected_payload: expectedPayload,
          expected: stringifyExpectedPayloadForEditor(targetStage, expectedPayload),
          notes: String(parsed.notes ?? ""),
        });
      }
    } catch (error) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: `Invalid JSONL row: ${String(error)}` }) }));
      return;
    }
    setState((prev) => ({
      ...prev,
      c4EditorRows: parsedRows,
      c4ValidationIssues: [],
      c4ValidationStatus: "not_run",
      jsonText: prettyJson({ status: "success", capability_id: "c4", action: "import_editor_jsonl", rows_total: parsedRows.length }),
    }));
  }

  // Русский комментарий: сохраняет изменения редактора в backend через replace-операцию.
  async function handleSaveC4EditorChanges(): Promise<void> {
    if (!state.activeArenaId || !state.c4EditorDatasetId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "saving dataset rows", budgetPercent: 65 }));
    try {
      const rowsToSave = state.c4EditorRows.map((row) => {
        const stage = normalizeDatasetTargetStage(row.target_stage);
        const payload = normalizeExpectedPayloadFromEditorInput({
          targetStage: stage,
          expected: row.expected,
          expectedPayload: row.expected_payload,
        });
        return {
          ...row,
          target_stage: stage,
          expected_payload: payload,
          expected: stringifyExpectedPayloadForEditor(stage, payload),
        };
      });
      const response = await replaceArenaDatasetRows(state.activeArenaId, state.c4EditorDatasetId, rowsToSave);
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "replace_rows",
        arena_id: state.activeArenaId,
        dataset_id: state.c4EditorDatasetId,
        rows_total: response.active_dataset?.rows_total ?? 0,
      };
      setState((prev) => ({
        ...prev,
        c4Datasets: response.datasets,
        c4ActiveDatasetId: response.active_dataset_id,
        c4ActiveDataset: response.active_dataset,
        c4AssignedDatasetIds: response.assigned_dataset_ids,
        c4SelectedDatasetIds: prev.c4SelectionDirty ? prev.c4SelectedDatasetIds : response.assigned_dataset_ids,
        c4EditorRows: response.active_dataset?.rows.map((row) => ({ ...row })) ?? [],
        c4ValidationIssues: [],
        c4ValidationStatus: "not_run",
        budgetPercent: 100,
        budgetStage: "dataset rows saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: запускает базовую проверку dataset и показывает issues в C4 UI.
  async function handleValidateC4Dataset(): Promise<void> {
    const targetDatasetId = state.c4ViewMode === "edit" ? state.c4EditorDatasetId : state.c4ActiveDatasetId;
    if (!state.activeArenaId || !targetDatasetId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "validating dataset", budgetPercent: 60 }));
    try {
      const response = await validateArenaDataset(state.activeArenaId, targetDatasetId);
      const validation = response.validation_report;
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "validate_dataset",
        arena_id: state.activeArenaId,
        dataset_id: validation?.dataset_id ?? targetDatasetId,
        validation_status: validation?.status ?? "unknown",
        issues_total: validation?.issues.length ?? 0,
      };
      setState((prev) => ({
        ...prev,
        c4Datasets: response.datasets,
        c4ActiveDatasetId: response.active_dataset_id,
        c4ActiveDataset: response.active_dataset,
        c4AssignedDatasetIds: response.assigned_dataset_ids,
        c4SelectedDatasetIds: prev.c4SelectionDirty ? prev.c4SelectedDatasetIds : response.assigned_dataset_ids,
        c4ValidationIssues: validation?.issues ?? [],
        c4ValidationStatus: validation?.status ?? "unknown",
        budgetPercent: 100,
        budgetStage: "dataset validated",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: сохраняет версию активного dataset как snapshot-артефакт.
  async function handleSaveC4DatasetVersion(): Promise<void> {
    const targetDatasetId = state.c4ViewMode === "edit" ? state.c4EditorDatasetId : state.c4ActiveDatasetId;
    if (!state.activeArenaId || !targetDatasetId) {
      return;
    }
    const label = `manual-${new Date().toISOString().slice(0, 19)}`;
    setState((prev) => ({ ...prev, budgetStage: "saving dataset version", budgetPercent: 65 }));
    try {
      const response = await saveArenaDatasetVersion(state.activeArenaId, targetDatasetId, label, "manual");
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "save_dataset_version",
        arena_id: state.activeArenaId,
        dataset_id: targetDatasetId,
        version_id: response.version?.version_id ?? "",
      };
      setState((prev) => ({
        ...prev,
        c4Datasets: response.datasets,
        c4ActiveDatasetId: response.active_dataset_id,
        c4ActiveDataset: response.active_dataset,
        c4AssignedDatasetIds: response.assigned_dataset_ids,
        c4SelectedDatasetIds: prev.c4SelectionDirty ? prev.c4SelectedDatasetIds : response.assigned_dataset_ids,
        c4EditorRows: prev.c4ViewMode === "edit" ? response.active_dataset?.rows.map((row) => ({ ...row })) ?? [] : prev.c4EditorRows,
        budgetPercent: 100,
        budgetStage: "dataset version saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: локально переключает сравнительную метрику в evaluation profile.
  function handleToggleC4ComparativeMetric(metricId: string): void {
    setState((prev) => ({
      ...prev,
      c4ComparativeMetrics: prev.c4ComparativeMetrics.map((item) =>
        item.metric_id === metricId ? { ...item, enabled: !item.enabled } : item
      ),
    }));
  }

  // Русский комментарий: обновляет вес сравнительной метрики в evaluation profile.
  function handleChangeC4ComparativeMetricWeight(metricId: string, value: string): void {
    const parsedValue = Number.parseFloat(value);
    const nextWeight = Number.isFinite(parsedValue) ? parsedValue : 0;
    setState((prev) => ({
      ...prev,
      c4ComparativeMetrics: prev.c4ComparativeMetrics.map((item) =>
        item.metric_id === metricId ? { ...item, weight: nextWeight } : item
      ),
    }));
  }

  // Русский комментарий: локально переключает diagnostic сигнал в evaluation profile.
  function handleToggleC4DiagnosticSignal(signalId: string): void {
    setState((prev) => ({
      ...prev,
      c4DiagnosticSignals: prev.c4DiagnosticSignals.map((item) =>
        item.signal_id === signalId ? { ...item, enabled: !item.enabled } : item
      ),
    }));
  }

  // Русский комментарий: переключает выбранность proposal item до явного Apply.
  function handleToggleC4MetricProposalItem(proposalItemId: string): void {
    setState((prev) => {
      const selected = new Set(prev.c4SelectedMetricProposalItemIds);
      if (selected.has(proposalItemId)) {
        selected.delete(proposalItemId);
      } else {
        selected.add(proposalItemId);
      }
      return { ...prev, c4SelectedMetricProposalItemIds: Array.from(selected) };
    });
  }

  // Русский комментарий: локально переключает evaluator adapter в evaluation profile.
  function handleToggleC4Evaluator(evaluatorId: string): void {
    setState((prev) => ({
      ...prev,
      c4Evaluators: prev.c4Evaluators.map((item) =>
        item.evaluator_id === evaluatorId ? { ...item, enabled: !item.enabled } : item
      ),
    }));
  }

  // Русский комментарий: локально переключает связь evaluator x metric в матрице покрытия.
  function handleToggleC4EvaluatorMetricLink(evaluatorId: string, metricKind: "comparative" | "diagnostic", metricId: string): void {
    setState((prev) => {
      const evaluator = prev.c4Evaluators.find((item) => item.evaluator_id === evaluatorId);
      const fallbackCompatibility = resolveEvaluatorMetricCompatibility(evaluator, metricKind, metricId);
      const index = prev.c4EvaluatorMetricLinks.findIndex(
        (link) =>
          link.evaluator_id === evaluatorId &&
          link.metric_kind === metricKind &&
          link.metric_id === metricId
      );
      if (index < 0) {
        if (fallbackCompatibility.status === "incompatible") {
          return prev;
        }
        return {
          ...prev,
          c4EvaluatorMetricLinks: [
            ...prev.c4EvaluatorMetricLinks,
            {
              evaluator_id: evaluatorId,
              metric_kind: metricKind,
              metric_id: metricId,
              enabled: true,
              compatibility_status: "compatible",
              compatibility_reason: "",
            },
          ],
        };
      }
      const currentLink = prev.c4EvaluatorMetricLinks[index];
      if (!currentLink.enabled && fallbackCompatibility.status === "incompatible") {
        return prev;
      }
      return {
        ...prev,
        c4EvaluatorMetricLinks: prev.c4EvaluatorMetricLinks.map((link, linkIndex) =>
          linkIndex === index ? { ...link, enabled: !link.enabled } : link
        ),
      };
    });
  }

  // Русский комментарий: сохраняет блок метрик evaluation profile в backend.
  async function handleSaveC4EvaluationMetrics(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "saving evaluation metrics", budgetPercent: 60 }));
    try {
      const response = await saveArenaEvaluationMetrics(
        state.activeArenaId,
        state.c4ComparativeMetrics,
        state.c4DiagnosticSignals
      );
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "save_evaluation_metrics",
        arena_id: state.activeArenaId,
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageMappings: response.stage_mappings ?? prev.c4StageMappings,
        c4StageMappingCoverage: response.stage_mapping_coverage ?? prev.c4StageMappingCoverage,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationBudget: response.budget,
        c4EvaluationVersions: response.versions,
        budgetPercent: 100,
        budgetStage: "evaluation metrics saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: запрашивает AI/deterministic proposal метрик без применения к profile.
  async function handleSuggestC4EvaluationMetrics(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "suggesting metrics", budgetPercent: 60 }));
    try {
      const response = await suggestArenaEvaluationMetrics(state.activeArenaId);
      const proposal = response.latest_metric_proposal ?? null;
      const snapshot = {
        status: "success",
        capability_id: "c5",
        action: response.action ?? "suggest_metrics",
        arena_id: state.activeArenaId,
        proposal_id: proposal?.proposal_id ?? "",
        proposal_items_total: proposal?.items.length ?? 0,
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageMappings: response.stage_mappings ?? prev.c4StageMappings,
        c4StageMappingCoverage: response.stage_mapping_coverage ?? prev.c4StageMappingCoverage,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationBudget: response.budget,
        c4EvaluationVersions: response.versions,
        c4MetricProposal: proposal,
        c4SelectedMetricProposalItemIds: buildDefaultMetricProposalSelection(proposal),
        budgetPercent: 100,
        budgetStage: "metric proposal ready",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: применяет выбранные proposal items как новую версию evaluation profile.
  async function handleApplyC4MetricProposal(): Promise<void> {
    if (!state.activeArenaId || !state.c4MetricProposal) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "applying metric proposal", budgetPercent: 65 }));
    try {
      const response = await applyArenaEvaluationMetricProposal(
        state.activeArenaId,
        state.c4MetricProposal.proposal_id,
        state.c4SelectedMetricProposalItemIds
      );
      const proposal = response.latest_metric_proposal ?? null;
      const snapshot = {
        status: "success",
        capability_id: "c5",
        action: response.action ?? "apply_metric_proposal",
        arena_id: state.activeArenaId,
        proposal_id: state.c4MetricProposal.proposal_id,
        applied_items_total: state.c4SelectedMetricProposalItemIds.length,
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageMappings: response.stage_mappings ?? prev.c4StageMappings,
        c4StageMappingCoverage: response.stage_mapping_coverage ?? prev.c4StageMappingCoverage,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationBudget: response.budget,
        c4EvaluationVersions: response.versions,
        c4MetricProposal: proposal,
        c4SelectedMetricProposalItemIds: buildDefaultMetricProposalSelection(proposal),
        budgetPercent: 100,
        budgetStage: "metric proposal applied",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: сохраняет блок evaluator-адаптеров evaluation profile в backend.
  async function handleSaveC4EvaluationEvaluators(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "saving evaluators", budgetPercent: 60 }));
    try {
      const response = await saveArenaEvaluationEvaluators(state.activeArenaId, state.c4Evaluators);
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "save_evaluation_evaluators",
        arena_id: state.activeArenaId,
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageMappings: response.stage_mappings ?? prev.c4StageMappings,
        c4StageMappingCoverage: response.stage_mapping_coverage ?? prev.c4StageMappingCoverage,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationBudget: response.budget,
        c4EvaluationVersions: response.versions,
        budgetPercent: 100,
        budgetStage: "evaluation evaluators saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: сохраняет матрицу Evaluator x Metric в backend.
  async function handleSaveC4EvaluationMatrix(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "saving evaluator-metric matrix", budgetPercent: 60 }));
    try {
      const response = await saveArenaEvaluationMatrix(state.activeArenaId, state.c4EvaluatorMetricLinks);
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "save_evaluation_matrix",
        arena_id: state.activeArenaId,
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageMappings: response.stage_mappings ?? prev.c4StageMappings,
        c4StageMappingCoverage: response.stage_mapping_coverage ?? prev.c4StageMappingCoverage,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationBudget: response.budget,
        c4EvaluationVersions: response.versions,
        budgetPercent: 100,
        budgetStage: "evaluation matrix saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: добавляет вручную новую строку stage mapping (human-first path).
  function handleAddC4StageMappingRow(): void {
    const firstCandidate = state.c2CandidateSetDraft?.candidates?.[0];
    const mappingId = `map_manual_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
    const nextRow: C4StageMapping = {
      mapping_id: mappingId,
      target_stage: "retrieval",
      candidate_id: firstCandidate?.candidate_id ?? "",
      candidate_title: firstCandidate?.title ?? "Select candidate",
      selected_node_ids: [],
      suggested_node_ids: [],
      status: "missing",
      confidence: 0,
      reason: "manual_row_created",
      enabled: true,
      notes: "",
      source: "manual",
    };
    setState((prev) => ({
      ...prev,
      c4StageMappings: [...prev.c4StageMappings, nextRow],
    }));
  }

  // Русский комментарий: удаляет одну строку stage mapping из локального списка.
  function handleDeleteC4StageMappingRow(mappingId: string): void {
    setState((prev) => ({
      ...prev,
      c4StageMappings: prev.c4StageMappings.filter((item) => item.mapping_id !== mappingId),
      c4StageMappingCoverage: prev.c4StageMappingCoverage.filter((item) => item.mapping_id !== mappingId),
    }));
  }

  // Русский комментарий: обновляет значения строки stage mapping в отдельном wizard-шаге.
  function handleUpdateC4StageMappingField(
    mappingId: string,
    field: "selected_node_ids" | "enabled" | "notes" | "target_stage" | "candidate_id",
    value: string | boolean,
  ): void {
    setState((prev) => ({
      ...prev,
      c4StageMappings: prev.c4StageMappings.map((item) => {
        if (item.mapping_id !== mappingId) {
          return item;
        }
        if (field === "enabled") {
          return { ...item, enabled: Boolean(value), source: "manual" };
        }
        if (field === "selected_node_ids") {
          const nodeIds = String(value)
            .split(",")
            .map((token) => token.trim())
            .filter((token, index, array) => token.length > 0 && array.indexOf(token) === index);
          return {
            ...item,
            selected_node_ids: nodeIds,
            status: nodeIds.length <= 0 ? "missing" : nodeIds.length > 1 ? "ambiguous" : "bound",
            confidence: nodeIds.length <= 0 ? 0 : nodeIds.length > 1 ? 0.55 : 0.8,
            source: "manual",
            reason: nodeIds.length === 1 ? "Manually confirmed by user." : item.reason,
          };
        }
        if (field === "target_stage") {
          return {
            ...item,
            target_stage: String(value),
            status: item.selected_node_ids.length === 1 ? "bound" : item.status,
            confidence: item.selected_node_ids.length === 1 ? Math.max(item.confidence || 0, 0.8) : item.confidence,
            reason: item.selected_node_ids.length === 1 ? "Manually confirmed by user." : item.reason,
            source: "manual",
          };
        }
        if (field === "candidate_id") {
          const nextCandidateId = String(value);
          const candidate = prev.c2CandidateSetDraft?.candidates?.find((candidateItem) => candidateItem.candidate_id === nextCandidateId);
          return {
            ...item,
            candidate_id: nextCandidateId,
            candidate_title: (candidate?.title ?? nextCandidateId) || "Unknown candidate",
            status: item.selected_node_ids.length === 1 ? "bound" : item.status,
            confidence: item.selected_node_ids.length === 1 ? Math.max(item.confidence || 0, 0.8) : item.confidence,
            reason: item.selected_node_ids.length === 1 ? "Manually confirmed by user." : item.reason,
            source: "manual",
          };
        }
        return {
          ...item,
          notes: String(value),
          status: item.selected_node_ids.length === 1 ? "bound" : item.status,
          confidence: item.selected_node_ids.length === 1 ? Math.max(item.confidence || 0, 0.8) : item.confidence,
          reason: item.selected_node_ids.length === 1 ? "Manually confirmed by user." : item.reason,
          source: "manual",
        };
      }),
    }));
  }

  // Русский комментарий: сохраняет stage mappings в backend и подтягивает coverage.
  async function handleSaveC4StageMappings(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "saving stage mappings", budgetPercent: 60 }));
    try {
      const response = await saveArenaEvaluationStageMappings(state.activeArenaId, state.c4StageMappings);
      const snapshot = {
        status: "success",
        capability_id: "c5s",
        action: response.action ?? "save_stage_mappings",
        arena_id: state.activeArenaId,
        stage_mappings_total: (response.stage_mappings ?? []).length,
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageMappings: response.stage_mappings ?? prev.c4StageMappings,
        c4StageMappingCoverage: response.stage_mapping_coverage ?? prev.c4StageMappingCoverage,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationBudget: response.budget,
        c4EvaluationVersions: response.versions,
        budgetPercent: 100,
        budgetStage: "stage mappings saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: запускает auto-map stage mappings по target_stage.
  async function handleAutoMapC4StageMappings(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "auto-mapping stage mappings", budgetPercent: 60 }));
    try {
      const response = await autoMapArenaEvaluationStageMappings(state.activeArenaId);
      const suggestedMappings = response.suggested_stage_mappings ?? [];
      const suggestedCoverage = response.suggested_stage_mapping_coverage ?? [];
      const snapshot = {
        status: "success",
        capability_id: "c5s",
        action: response.action ?? "auto_map_stage_mappings",
        arena_id: state.activeArenaId,
        suggested_total: suggestedMappings.length,
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageMappings: suggestedMappings.length > 0 ? suggestedMappings : prev.c4StageMappings,
        c4StageMappingCoverage: suggestedCoverage.length > 0 ? suggestedCoverage : prev.c4StageMappingCoverage,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationBudget: response.budget,
        c4EvaluationVersions: response.versions,
        budgetPercent: 100,
        budgetStage: "stage mappings auto-mapped",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: авто-инициализирует mapping при входе в шаг без обязательного ручного клика.
  async function handleAutoInitC4StageMappings(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "initializing stage mappings", budgetPercent: 55 }));
    try {
      const autoPayload = await autoMapArenaEvaluationStageMappings(state.activeArenaId);
      const suggestedMappings = autoPayload.suggested_stage_mappings ?? [];
      if (suggestedMappings.length <= 0) {
        setState((prev) => ({
          ...prev,
          budgetPercent: 100,
          budgetStage: "stage mapping initialized (manual mode)",
          jsonText: prettyJson({
            status: "success",
            capability_id: "c5s",
            action: "auto_init_stage_mappings",
            arena_id: state.activeArenaId,
            message: "No auto suggestions found. Use manual rows.",
          }),
          lastPayload: {
            status: "success",
            capability_id: "c5s",
            action: "auto_init_stage_mappings",
            arena_id: state.activeArenaId,
            suggested_total: 0,
          },
        }));
        return;
      }
      const response = await saveArenaEvaluationStageMappings(state.activeArenaId, suggestedMappings);
      const snapshot = {
        status: "success",
        capability_id: "c5s",
        action: "auto_init_stage_mappings",
        arena_id: state.activeArenaId,
        stage_mappings_total: (response.stage_mappings ?? []).length,
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageMappings: response.stage_mappings ?? prev.c4StageMappings,
        c4StageMappingCoverage: response.stage_mapping_coverage ?? prev.c4StageMappingCoverage,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationVersions: response.versions,
        budgetPercent: 100,
        budgetStage: "stage mapping initialized",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: запускает validate-проверку evaluation profile и показывает issues.
  async function handleValidateC4EvaluationProfile(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "validating evaluation profile", budgetPercent: 65 }));
    try {
      const response = await validateArenaEvaluationProfile(state.activeArenaId);
      const validationReport = response.validation_report;
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "validate_evaluation_profile",
        arena_id: state.activeArenaId,
        validation_status: validationReport?.status ?? "unknown",
        issues_total: validationReport?.issues.length ?? 0,
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageMappings: response.stage_mappings ?? prev.c4StageMappings,
        c4StageMappingCoverage: response.stage_mapping_coverage ?? prev.c4StageMappingCoverage,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationBudget: response.budget,
        c4EvaluationVersions: response.versions,
        c4EvaluationValidationStatus: validationReport?.status ?? "invalid",
        c4EvaluationValidationIssues: validationReport?.issues ?? [],
        budgetPercent: 100,
        budgetStage: "evaluation profile validated",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: сохраняет snapshot-версию evaluation profile.
  async function handleSaveC4EvaluationVersion(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    const label = `eval-${new Date().toISOString().slice(0, 19)}`;
    setState((prev) => ({ ...prev, budgetStage: "saving evaluation version", budgetPercent: 65 }));
    try {
      const response = await saveArenaEvaluationVersion(state.activeArenaId, label, "manual");
      const snapshot = {
        status: "success",
        capability_id: "c4",
        action: response.action ?? "save_evaluation_version",
        arena_id: state.activeArenaId,
        version_id: response.version?.version_id ?? "",
      };
      setState((prev) => ({
        ...prev,
        c4ComparativeMetrics: response.comparative_metrics,
        c4DiagnosticSignals: response.diagnostic_signals,
        c4Evaluators: response.evaluators,
        c4StageBindings: response.stage_bindings ?? prev.c4StageBindings,
        c4StageBindingCoverage: response.stage_binding_coverage ?? prev.c4StageBindingCoverage,
        c4EvaluatorMetricLinks: response.evaluator_metric_links,
        c4CandidateFeatures: response.candidate_features ?? prev.c4CandidateFeatures,
        c4EvaluationBudget: response.budget,
        c4EvaluationVersions: response.versions,
        budgetPercent: 100,
        budgetStage: "evaluation version saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: локально переключает optimizer method в C5 setup.
  function handleToggleC5Method(methodId: string): void {
    setState((prev) => ({
      ...prev,
      c5Methods: prev.c5Methods.map((method) => (method.method_id === methodId ? { ...method, enabled: !method.enabled } : method)),
    }));
  }

  // Русский комментарий: локально переключает optimizer control в C5 setup.
  function handleToggleC5Control(controlId: string): void {
    setState((prev) => ({
      ...prev,
      c5Controls: prev.c5Controls.map((control) => (control.control_id === controlId ? { ...control, enabled: !control.enabled } : control)),
    }));
  }

  // Русский комментарий: обновляет одно поле run_plan в C5 setup.
  function handleChangeC5RunPlanField(
    field: keyof C5OptimizerRunPlan,
    rawValue: string,
  ): void {
    const numericValue = Number(rawValue);
    setState((prev) => ({
      ...prev,
      c5RunPlan: {
        ...prev.c5RunPlan,
        [field]: Number.isFinite(numericValue) ? numericValue : 0,
      },
    }));
  }

  // Русский комментарий: обновляет одно поле budget в C5 setup.
  function handleChangeC5BudgetField(
    field: keyof C5OptimizerBudget,
    rawValue: string,
  ): void {
    const numericValue = Number(rawValue);
    setState((prev) => ({
      ...prev,
      c5Budget: {
        ...prev.c5Budget,
        [field]: Number.isFinite(numericValue) ? numericValue : 0,
      },
    }));
  }

  // Русский комментарий: сохраняет текущий C5 optimizer setup в backend.
  async function handleSaveC5OptimizerSetup(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "saving optimizer setup", budgetPercent: 60 }));
    try {
      const response = await saveArenaOptimizerSetup(state.activeArenaId, {
        methods: state.c5Methods,
        controls: state.c5Controls,
        run_plan: state.c5RunPlan,
        budget: state.c5Budget,
      });
      const snapshot = {
        status: "success",
        capability_id: "c5",
        action: response.action ?? "save_optimizer_setup",
        arena_id: state.activeArenaId,
        methods_total: response.methods.length,
        controls_total: response.controls.length,
      };
      setState((prev) => ({
        ...prev,
        c5Methods: response.methods,
        c5Controls: response.controls,
        c5RunPlan: response.run_plan,
        c5Budget: response.budget,
        c5Versions: response.versions,
        c5LaunchHistory: response.launch_history,
        budgetPercent: 100,
        budgetStage: "optimizer setup saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: запускает preflight-валидацию C5 setup и отображает issues.
  async function handleValidateC5OptimizerSetup(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "validating optimizer setup", budgetPercent: 65 }));
    try {
      const response = await validateArenaOptimizerSetup(state.activeArenaId);
      const validationReport = response.validation_report;
      const snapshot = {
        status: "success",
        capability_id: "c5",
        action: response.action ?? "validate_optimizer_setup",
        arena_id: state.activeArenaId,
        validation_status: validationReport?.status ?? "not_run",
        issues_total: validationReport?.issues.length ?? 0,
      };
      setState((prev) => ({
        ...prev,
        c5Methods: response.methods,
        c5Controls: response.controls,
        c5RunPlan: response.run_plan,
        c5Budget: response.budget,
        c5Versions: response.versions,
        c5LaunchHistory: response.launch_history,
        c5ValidationStatus: validationReport?.status ?? "not_run",
        c5ValidationIssues: validationReport?.issues ?? [],
        budgetPercent: 100,
        budgetStage: "optimizer setup validated",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: сохраняет snapshot-версию C5 setup.
  async function handleSaveC5OptimizerVersion(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "saving optimizer version", budgetPercent: 65 }));
    try {
      const response = await saveArenaOptimizerVersion(state.activeArenaId, "optimizer-v1", "manual");
      const snapshot = {
        status: "success",
        capability_id: "c5",
        action: response.action ?? "save_optimizer_version",
        arena_id: state.activeArenaId,
        version_id: response.version?.version_id ?? "",
      };
      setState((prev) => ({
        ...prev,
        c5Methods: response.methods,
        c5Controls: response.controls,
        c5RunPlan: response.run_plan,
        c5Budget: response.budget,
        c5Versions: response.versions,
        c5LaunchHistory: response.launch_history,
        budgetPercent: 100,
        budgetStage: "optimizer version saved",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: выполняет launch C5 optimizer после guardrail проверки на backend.
  async function handleLaunchC5Optimizer(): Promise<void> {
    if (!state.activeArenaId) {
      return;
    }
    setState((prev) => ({ ...prev, budgetStage: "launching optimizer", budgetPercent: 70 }));
    try {
      const response = await launchArenaOptimizer(state.activeArenaId, "manual");
      const snapshot = {
        status: response.status,
        capability_id: "c5",
        action: response.action ?? "launch_optimizer",
        arena_id: state.activeArenaId,
        run_id: response.run?.run_id ?? null,
        run_status: response.run?.status ?? null,
      };
      setState((prev) => ({
        ...prev,
        c5Methods: response.methods,
        c5Controls: response.controls,
        c5RunPlan: response.run_plan,
        c5Budget: response.budget,
        c5Versions: response.versions,
        c5LaunchHistory: response.launch_history,
        budgetPercent: 100,
        budgetStage: "optimizer launch accepted",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: переключение capability в workspace.
  async function handleSwitchCapability(capabilityId: string, item?: CapabilityWizardItem): Promise<void> {
    if (item && !item.isInteractive) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({
          status: "notice",
          capability_id: capabilityId,
          message: item.wizardReason || "This wizard step is locked.",
        }),
      }));
      return;
    }
    if (capabilityId === "c1") {
      navigateToBattlesHub();
      return;
    }
    setState((prev) => ({
      ...prev,
      activeCapabilityId: capabilityId,
      budgetPercent: capabilityId === "c2" ? prev.budgetPercent : 10,
      budgetStage: capabilityId === "c2" ? prev.budgetStage : "switch capability",
    }));
    if (capabilityId === "c2") {
      if (!state.activeArenaId) {
        setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "Select battle first, then use C2 chat." }) }));
        return;
      }
      await loadArenaContext(state.activeArenaId);
      return;
    }

    if (capabilityId === "c3") {
      if (!state.activeArenaId) {
        setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "Select battle first, then use C3 patterns." }) }));
        return;
      }
      try {
        await loadC3PatternState(state.activeArenaId, state.c3PatternQuery, true);
      } catch (error) {
        setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
      }
      return;
    }
    if (capabilityId === "c4") {
      if (!state.activeArenaId) {
        setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "Select battle first, then use C4 datasets." }) }));
        return;
      }
      try {
        await loadC4DatasetState(state.activeArenaId, true);
      } catch (error) {
        setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
      }
      return;
    }
    if (capabilityId === "c5" || capabilityId === "c5s" || capabilityId === "c6") {
      if (!state.activeArenaId) {
        setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "Select battle first, then configure evaluation profile." }) }));
        return;
      }
      try {
        await loadC4EvaluationState(state.activeArenaId, true);
      } catch (error) {
        setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
      }
      return;
    }
    if (capabilityId === "c7") {
      if (!state.activeArenaId) {
        setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "Select battle first, then use C7 optimizer setup." }) }));
        return;
      }
      try {
        await loadC5OptimizerState(state.activeArenaId, true);
      } catch (error) {
        setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
      }
      return;
    }
    try {
      const payload: StubPayload = await fetchStubCapability(capabilityId);
      setState((prev) => ({ ...prev, jsonText: prettyJson(payload) }));
    } catch (error) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: отправка сообщения в battle-чат с учетом активной capability-вкладки.
  async function handleSendC2Message(generateCandidates: boolean): Promise<void> {
    const arenaId = state.activeArenaId;
    if (!arenaId) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "Open battle before using C2 chat." }) }));
      return;
    }
    const capabilityId = state.activeCapabilityId;
    if (!CHAT_SUPPORTED_CAPABILITY_IDS.has(capabilityId)) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "Battle chat actions are not available for this step yet." }) }));
      return;
    }
    const message = state.c2ChatInput.trim();
    if (!message) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "Message is required." }) }));
      return;
    }
    if (capabilityId === "c2" && generateCandidates && state.c3SelectedPatternIds.length === 0) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "Select at least one pattern in C3 before generation." }) }));
      return;
    }

    const contextAction = capabilityId === "c2" ? "" : (generateCandidates ? (CHAT_DEFAULT_CONTEXT_ACTION_BY_CAPABILITY[capabilityId] ?? "") : "");
    setState((prev) => ({
      ...prev,
      budgetStage: generateCandidates
        ? capabilityId === "c2"
          ? "generating candidates"
          : "running contextual action"
        : "sending message",
      budgetPercent: 60,
    }));
    try {
      const response = await postArenaChatMessage(arenaId, message, {
        generateCandidates: capabilityId === "c2" ? generateCandidates : false,
        maxCandidates: 3,
        capabilityId,
        contextAction,
      });
      const isC2Chat = capabilityId === "c2";
      const resolvedAction = response.copilot_context?.resolved_action ?? (isC2Chat ? (generateCandidates ? "generate_candidates" : "append_message") : "append_message");
      const snapshot = {
        status: "success",
        capability_id: capabilityId,
        action: resolvedAction,
        arena_id: arenaId,
        messages_total: response.messages_total,
        candidate_set_id: response.candidate_set_draft?.candidate_set_id ?? state.c2CandidateSetDraft?.candidate_set_id ?? null,
        copilot_context: response.copilot_context ?? null,
      };
      setState((prev) => ({
        ...prev,
        ...(() => {
          if (!isC2Chat) {
            return {};
          }
          // Русский комментарий: сохраняем выбранного кандидата, если он остался в новом draft, иначе выбираем первый.
          const nextDraft = response.candidate_set_draft ?? prev.c2CandidateSetDraft;
          const canKeepSelected = nextDraft?.candidates.some((candidate) => candidate.candidate_id === prev.c2SelectedCandidateId) ?? false;
          const nextSelectedCandidateId = canKeepSelected ? prev.c2SelectedCandidateId : (nextDraft?.candidates[0]?.candidate_id ?? "");
          const canKeepExpanded = nextDraft?.candidates.some((candidate) => candidate.candidate_id === prev.c2ExpandedCandidateId) ?? false;
          const nextExpandedCandidateId = canKeepExpanded ? prev.c2ExpandedCandidateId : "";
          const nextSelectedForTestsIds =
            nextDraft?.candidates
              .filter((candidate) => Boolean(candidate.selected_for_tests))
              .map((candidate) => candidate.candidate_id) ?? [];
          return {
            c2CandidateSetDraft: nextDraft,
            c2SelectedCandidateId: nextSelectedCandidateId,
            c2SelectedForTestsIds: nextSelectedForTestsIds,
            c2ExpandedCandidateId: nextExpandedCandidateId,
          };
        })(),
        c2ChatInput: "",
        c2Messages: response.messages,
        c2CopilotResolvedAction: response.copilot_context?.resolved_action ?? "",
        c2CopilotAllowedActions: response.copilot_context?.allowed_actions ?? [],
        c2CopilotSummary: response.copilot_context?.summary ?? "",
        budgetStage: isC2Chat ? "c2 updated" : "contextual action applied",
        budgetPercent: 100,
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
      if (!isC2Chat) {
        if (capabilityId === "c4") {
          await loadC4DatasetState(arenaId, false);
        } else if (capabilityId === "c5" || capabilityId === "c5s" || capabilityId === "c6") {
          await loadC4EvaluationState(arenaId, false);
        } else if (capabilityId === "c7") {
          await loadC5OptimizerState(arenaId, false);
        }
      }
    } catch (error) {
      setState((prev) => ({ ...prev, budgetStage: "failed", budgetPercent: 100, jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: обработчик текста C2 input.
  function handleC2ChatInputChange(nextValue: string): void {
    setState((prev) => ({ ...prev, c2ChatInput: nextValue }));
  }

  // Русский комментарий: отправляет пользовательский выбор кандидатов в внутренний этап подготовки к тестам.
  async function handleSelectCandidatesForTests(): Promise<void> {
    if (!state.activeArenaId) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "Open battle before candidate selection." }) }));
      return;
    }
    if (!state.c2CandidateSetDraft) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "Generate candidates before test selection." }) }));
      return;
    }
    if (state.c2SelectedForTestsIds.length === 0) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "Choose at least one candidate for tests." }) }));
      return;
    }

    setState((prev) => ({ ...prev, budgetStage: "preparing selected candidates", budgetPercent: 70 }));
    try {
      const response = await selectArenaCandidatesForTests(state.activeArenaId, state.c2SelectedForTestsIds, 3);
      const snapshot = {
        status: "success",
        capability_id: "c2",
        action: "select_candidates_for_tests",
        arena_id: response.arena_id,
        compile_gate: response.compile_gate,
      };
      setState((prev) => ({
        ...prev,
        c2CandidateSetDraft: response.candidate_set_draft,
        c2SelectedForTestsIds:
          response.candidate_set_draft.candidates
            .filter((candidate) => Boolean(candidate.selected_for_tests))
            .map((candidate) => candidate.candidate_id),
        c2Messages: response.messages,
        budgetPercent: 100,
        budgetStage: "selected candidates prepared",
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
    } catch (error) {
      setState((prev) => ({ ...prev, budgetStage: "failed", budgetPercent: 100, jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: выделяет кандидата в таблице архитектур для минимальной интерактивности workspace.
  function handleSelectCandidate(candidateId: string): void {
    setState((prev) => ({ ...prev, c2SelectedCandidateId: candidateId }));
  }

  // Русский комментарий: добавляет/убирает кандидата из пользовательского набора для тестов.
  function handleToggleCandidateForTests(candidateId: string): void {
    setState((prev) => {
      const selectedSet = new Set(prev.c2SelectedForTestsIds);
      if (selectedSet.has(candidateId)) {
        selectedSet.delete(candidateId);
      } else {
        selectedSet.add(candidateId);
      }
      return { ...prev, c2SelectedForTestsIds: Array.from(selectedSet) };
    });
  }

  // Русский комментарий: раскрывает/сворачивает аккордеон деталей выбранной архитектуры-кандидата.
  function handleToggleCandidateDetails(candidateId: string): void {
    setState((prev) => ({
      ...prev,
      c2SelectedCandidateId: candidateId,
      c2ExpandedCandidateId: prev.c2ExpandedCandidateId === candidateId ? "" : candidateId,
    }));
  }

  // Русский комментарий: открывает/закрывает debug drawer с последним runtime snapshot.
  function handleToggleDebugDrawer(): void {
    setState((prev) => ({ ...prev, debugDrawerOpen: !prev.debugDrawerOpen }));
  }

  // Русский комментарий: отправляет сообщение по Enter (Shift+Enter оставляет перенос строки).
  function handleC2ChatKeyDown(event: ReactKeyboardEvent<HTMLTextAreaElement>): void {
    if (event.key !== "Enter" || event.shiftKey) {
      return;
    }
    event.preventDefault();
    void handleSendC2Message(false);
  }

  // Русский комментарий: открывает модалку создания арены.
  function openCreateArenaDialog(): void {
    setArenaDialogMode("create");
    setArenaDialogArenaId("");
    setArenaDialogName("");
    setArenaDialogDescription("");
  }

  // Русский комментарий: открывает модалку переименования арены.
  function openRenameArenaDialog(arena: ArenaRecord): void {
    setArenaDialogMode("rename");
    setArenaDialogArenaId(arena.workspace_id);
    setArenaDialogName(arena.name);
    setArenaDialogDescription(arena.description);
    setArenaMenuOpenId(null);
  }

  // Русский комментарий: закрывает модалку арены.
  function closeArenaDialog(): void {
    setArenaDialogMode(null);
    setArenaDialogArenaId("");
    setArenaDialogName("");
    setArenaDialogDescription("");
  }

  // Русский комментарий: submit логики модалки создания/переименования.
  async function handleSubmitArenaDialog(): Promise<void> {
    const name = arenaDialogName.trim();
    const description = arenaDialogDescription.trim();
    if (!name) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "Battle name is required." }) }));
      return;
    }

    if (arenaDialogMode === "create") {
      setState((prev) => ({ ...prev, budgetPercent: 40, budgetStage: "creating battle" }));
      try {
        const created = await createArena(name, description);
        await refreshArenas(created.arena.workspace_id);
        const snapshot = { status: "success", action: "create_arena", arena: created.arena };
        setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "battle created", jsonText: prettyJson(snapshot), lastPayload: snapshot }));
        closeArenaDialog();
      } catch (error) {
        setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
      }
      return;
    }

    if (arenaDialogMode === "rename" && arenaDialogArenaId) {
      setState((prev) => ({ ...prev, budgetPercent: 45, budgetStage: "renaming battle" }));
      try {
        const renamed = await renameArena(arenaDialogArenaId, name);
        await refreshArenas(renamed.arena.workspace_id);
        const snapshot = { status: "success", action: "rename_arena", arena: renamed.arena };
        setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "battle renamed", jsonText: prettyJson(snapshot), lastPayload: snapshot }));
        closeArenaDialog();
      } catch (error) {
        setState((prev) => ({ ...prev, budgetPercent: 100, budgetStage: "failed", jsonText: prettyJson({ status: "error", message: String(error) }) }));
      }
    }
  }

  // Русский комментарий: дублирует арену из меню карточки.
  async function handleDuplicateArena(arenaId: string): Promise<void> {
    setArenaMenuOpenId(null);
    try {
      const duplicated = await duplicateArena(arenaId);
      await refreshArenas(duplicated.arena.workspace_id);
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "success", action: "duplicate_arena", arena: duplicated.arena }) }));
    } catch (error) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: удаляет арену из меню карточки.
  async function handleDeleteArena(arenaId: string): Promise<void> {
    setArenaMenuOpenId(null);
    const confirmed = window.confirm("Delete this battle? This action cannot be undone.");
    if (!confirmed) {
      return;
    }
    try {
      await deleteArena(arenaId);
      await refreshArenas();
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "success", action: "delete_arena", arena_id: arenaId }) }));
      if (route.name === "battle_workspace" && route.arenaId === arenaId) {
        navigateToBattlesHub();
      }
    } catch (error) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: String(error) }) }));
    }
  }

  // Русский комментарий: открывает выбранную арену.
  async function handleOpenArena(arenaId: string): Promise<void> {
    navigateToArenaWorkspace(arenaId);
    await loadArenaContext(arenaId);
  }

  // Русский комментарий: локально выделяет карточку в hub.
  function handleSelectArenaCard(arenaId: string): void {
    setState((prev) => ({ ...prev, activeArenaId: arenaId, metricArenaStatus: "selected", budgetStage: "battle highlighted" }));
  }

  // Русский комментарий: экспортирует последний payload в файл.
  function handleExportPayload(): void {
    if (!state.lastPayload) {
      return;
    }
    const fileName = makeTimestampedFileName("battle_snapshot");
    exportJsonToFile(fileName, state.lastPayload);
    setState((prev) => ({ ...prev, exportMeta: `${fileName}.json exported` }));
  }

  // Русский комментарий: генерирует демонстрационные метрики для плитки арены.
  function buildArenaCardMetrics(arena: ArenaRecord, index: number): { agents: number; tests: number; dataRows: number } {
    const seed = hashString(arena.workspace_id) + index * 17;
    return { agents: (seed % 7) + 2, tests: (seed % 12) + 8, dataRows: (seed % 240) + 60 };
  }

  // Русский комментарий: строит компактные showcase-метрики кандидата для центрального списка архитектур.
  function buildCandidateMetrics(candidateId: string): { quality: string; cost: string; latency: string } {
    const seed = hashString(candidateId);
    const quality = (0.76 + (seed % 18) / 100).toFixed(3);
    const cost = (0.19 + (seed % 26) / 100).toFixed(2);
    const latency = (0.78 + (seed % 70) / 100).toFixed(2);
    return { quality, cost, latency };
  }

  // Русский комментарий: строит простую SVG-схему архитектуры кандидата для v0-визуализации в аккордеоне.
  function renderCandidateMiniGraphSvg(candidate: C2CandidateDraftItem): JSX.Element {
    const graphNodes = candidate.mini_graph?.nodes ?? [];
    if (graphNodes.length === 0) {
      return <div className="issue-row info">Mini-graph is not available for this candidate.</div>;
    }

    const edges = candidate.mini_graph?.edges ?? [];
    const nodeWidth = 120;
    const nodeHeight = 42;
    const gapX = 26;
    const paddingX = 18;
    const paddingY = 14;
    const viewWidth = paddingX * 2 + graphNodes.length * nodeWidth + (graphNodes.length - 1) * gapX;
    const viewHeight = paddingY * 2 + nodeHeight;
    const nodeIndexById = new Map(graphNodes.map((node, index) => [node.id, index]));

    return (
      <svg className="candidate-mini-graph-svg" aria-label="candidate-mini-graph-svg" viewBox={`0 0 ${viewWidth} ${viewHeight}`} role="img">
        <defs>
          <marker id={`arrow-${candidate.candidate_id}`} markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="currentColor" />
          </marker>
        </defs>
        {edges.map((edge, edgeIndex) => {
          const sourceIndex = nodeIndexById.get(edge.source);
          const targetIndex = nodeIndexById.get(edge.target);
          if (sourceIndex === undefined || targetIndex === undefined) {
            return null;
          }
          const sourceX = paddingX + sourceIndex * (nodeWidth + gapX) + nodeWidth;
          const sourceY = paddingY + nodeHeight / 2;
          const targetX = paddingX + targetIndex * (nodeWidth + gapX);
          const targetY = paddingY + nodeHeight / 2;
          return (
            <line
              key={`edge-${edgeIndex}-${edge.source}-${edge.target}`}
              className="candidate-mini-graph-edge"
              x1={sourceX}
              y1={sourceY}
              x2={targetX}
              y2={targetY}
              markerEnd={`url(#arrow-${candidate.candidate_id})`}
            />
          );
        })}
        {graphNodes.map((node, index) => {
          const x = paddingX + index * (nodeWidth + gapX);
          const y = paddingY;
          return (
            <g key={node.id} className={`candidate-mini-graph-node kind-${node.kind}`} transform={`translate(${x} ${y})`}>
              <rect className="candidate-mini-graph-node-rect" width={nodeWidth} height={nodeHeight} rx="10" ry="10" />
              <text className="candidate-mini-graph-node-kind" x={10} y={16}>{node.kind}</text>
              <text className="candidate-mini-graph-node-label" x={10} y={31}>{node.label}</text>
            </g>
          );
        })}
      </svg>
    );
  }

  // Русский комментарий: раскрывает/сворачивает аккордеон деталей паттерна C3.
  function handleToggleC3PatternDetails(patternId: string): void {
    setState((prev) => ({
      ...prev,
      c3ExpandedPatternId: prev.c3ExpandedPatternId === patternId ? "" : patternId,
    }));
  }

  // Русский комментарий: рисует SVG-lite схему типового агента для C3 паттерна.
  function renderPatternMiniGraphSvg(pattern: C3PatternItem): JSX.Element {
    const graphNodes = pattern.agent_template?.nodes ?? [];
    if (graphNodes.length === 0) {
      return <div className="issue-row info">Template graph is not available for this pattern.</div>;
    }

    const edges = pattern.agent_template?.edges ?? [];
    const nodeWidth = 120;
    const nodeHeight = 42;
    const gapX = 26;
    const paddingX = 18;
    const paddingY = 14;
    const viewWidth = paddingX * 2 + graphNodes.length * nodeWidth + (graphNodes.length - 1) * gapX;
    const viewHeight = paddingY * 2 + nodeHeight;
    const nodeIndexById = new Map(graphNodes.map((node, index) => [node.id, index]));

    return (
      <svg className="candidate-mini-graph-svg" aria-label="c3-pattern-mini-graph-svg" viewBox={`0 0 ${viewWidth} ${viewHeight}`} role="img">
        <defs>
          <marker id={`c3-arrow-${pattern.pattern_id}`} markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="currentColor" />
          </marker>
        </defs>
        {edges.map((edge, edgeIndex) => {
          const sourceIndex = nodeIndexById.get(edge.source);
          const targetIndex = nodeIndexById.get(edge.target);
          if (sourceIndex === undefined || targetIndex === undefined) {
            return null;
          }
          const sourceX = paddingX + sourceIndex * (nodeWidth + gapX) + nodeWidth;
          const sourceY = paddingY + nodeHeight / 2;
          const targetX = paddingX + targetIndex * (nodeWidth + gapX);
          const targetY = paddingY + nodeHeight / 2;
          return (
            <line
              key={`c3-edge-${edgeIndex}-${edge.source}-${edge.target}`}
              className="candidate-mini-graph-edge"
              x1={sourceX}
              y1={sourceY}
              x2={targetX}
              y2={targetY}
              markerEnd={`url(#c3-arrow-${pattern.pattern_id})`}
            />
          );
        })}
        {graphNodes.map((node, index) => {
          const x = paddingX + index * (nodeWidth + gapX);
          const y = paddingY;
          return (
            <g key={node.id} className={`candidate-mini-graph-node kind-${node.kind}`} transform={`translate(${x} ${y})`}>
              <rect className="candidate-mini-graph-node-rect" width={nodeWidth} height={nodeHeight} rx="10" ry="10" />
              <text className="candidate-mini-graph-node-kind" x={10} y={16}>{node.kind}</text>
              <text className="candidate-mini-graph-node-label" x={10} y={31}>{node.label}</text>
            </g>
          );
        })}
      </svg>
    );
  }

  const isBattleRoute = route.name === "battle_workspace";
  const isC2Enabled = activeCapability.id === "c2";
  const isChatCapabilitySupported = CHAT_SUPPORTED_CAPABILITY_IDS.has(activeCapability.id);
  const c2PatternGateLocked = state.c3SelectedPatternIds.length === 0;
  const isC2ChatBlocked = isC2Enabled && c2PatternGateLocked;
  const canUseBattleChat = Boolean(state.activeArenaId) && isChatCapabilitySupported && !isC2ChatBlocked;
  const chatActionLabel = isC2Enabled ? "Generate" : "Run action";
  const chatActionHint = (() => {
    if (isC2Enabled) {
      return "Generate candidates from selected patterns.";
    }
    if (activeCapability.id === "c4") {
      return "Default action: add dataset row.";
    }
    if (activeCapability.id === "c5") {
      return "Default action: suggest task-specific metrics.";
    }
    if (activeCapability.id === "c5s") {
      return "Default action: auto-map stage mappings.";
    }
    if (activeCapability.id === "c6") {
      return "Default action: autofill evaluator matrix links.";
    }
    if (activeCapability.id === "c7") {
      return "Default action: validate optimizer setup.";
    }
    return "Context actions are unavailable for this step.";
  })();
  const chatPlaceholder = isC2ChatBlocked
    ? "First select pattern(s) in C3 to unlock C2 generation..."
    : isChatCapabilitySupported
      ? `Ask copilot about ${activeCapability.name.toLowerCase()}...`
      : "Open C2, C4, C5, Stage Mapping, C6 or C7 to use contextual chat...";
  const isDatasetCapability = activeCapability.id === "c4";
  const isMetricsCapability = activeCapability.id === "c5";
  const isStageMappingCapability = activeCapability.id === "c5s";
  const isEvaluatorsCapability = activeCapability.id === "c6";
  const isOptimizerCapability = activeCapability.id === "c7";

  return (
    <div className={`app${isBattleRoute ? " app--workspace" : " app--hub"}`} id="app-root">
      <aside className="app-sidebar">
        <div className="app-sidebar-brand">
          <img src="/assets/logo-lockup.svg" alt="AutoAgent Optimizer" />
        </div>
        <div className="app-sidebar-section">
          <div className="app-side-label">Workspace</div>
          <button type="button" className="app-side-pick" onClick={navigateToBattlesHub}>
            <span className="ws-dot" />
            <span>Battles Hub</span>
            <i data-lucide="chevrons-up-down" />
          </button>
        </div>
        <nav className="app-side-nav">
          {isBattleRoute
            ? capabilityWizardItems.map((capability) => {
                const statusClass = `wizard-${capability.wizardStatus}`;
                const icon = CAPABILITY_ICONS[capability.id] ?? "dot";
                return (
                  <button
                    key={capability.id}
                    type="button"
                    className={`cap-link${state.activeCapabilityId === capability.id ? " active" : ""}${!capability.isInteractive ? " disabled" : ""}`}
                    title={capability.wizardReason}
                    disabled={!capability.isInteractive}
                    onClick={() => {
                      void handleSwitchCapability(capability.id, capability);
                    }}
                  >
                    <i data-lucide={icon} className="cap-icon" />
                    <span className="cap-name">{capability.name}</span>
                    <span className={`cap-badge ${statusClass}`}>{capability.wizardStatus.replace("_", " ")}</span>
                  </button>
                );
              })
            : <div className="issue-row info">Open a battle to access capability menu.</div>}
        </nav>
        <div className="app-sidebar-foot">
          <div className="app-side-user">
            <div className="avatar">EK</div>
            <div>
              <div className="user-name">Elena Kuznetsova</div>
              <div className="user-org">ctrl2go · operator</div>
            </div>
            <i data-lucide="settings-2" />
          </div>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-topbar">
          <div className="tb-left">
            {isBattleRoute
              ? <>
                  <span className="tb-crumb">Battles</span>
                  <span className="tb-sep">/</span>
                  <span className="tb-id">{activeArena?.name ?? route.arenaId}</span>
                  <span className="tb-pill">battle workspace</span>
                </>
              : <>
                  <span className="tb-crumb">Battles</span>
                  <span className="tb-sep">/</span>
                  <span className="tb-id">Hub</span>
                  <span className="tb-pill">registry</span>
                </>}
          </div>
          <div className="tb-budget">
            <div className="tb-budget-label">
              <i data-lucide="gauge" />
              <span>{isBattleRoute ? "Battle progress" : "Hub progress"}</span>
            </div>
            <div className="tb-budget-bar"><div className="tb-budget-fill" style={{ width: `${Math.max(0, Math.min(state.budgetPercent, 100))}%` }} /></div>
            <div className="tb-budget-vals">{state.budgetPercent}% <span className="muted">{state.budgetStage}</span></div>
          </div>
          <div className="tb-right">
            {isBattleRoute ? (
              <button
                type="button"
                className="tb-btn tb-btn-ghost"
                onClick={handleToggleDebugDrawer}
                aria-expanded={state.debugDrawerOpen}
                aria-controls="debug-drawer"
              >
                <i data-lucide="bug" />
                Debug
              </button>
            ) : null}
            <button type="button" className="tb-btn tb-btn-ghost" onClick={handleExportPayload}>
              <i data-lucide="download" />
              Export snapshot
            </button>
            <button type="button" className="tb-btn tb-btn-primary" disabled>
              <i data-lucide="rocket" />
              Promote champion
            </button>
          </div>
        </header>

        <div className={`app-content${isBattleRoute ? "" : " app-content--single"}`}>
          <main className={`app-center${isBattleRoute ? " app-center--workspace" : ""}`}>
            {!isBattleRoute ? (
              <>
                <section className="content-head">
                  <div>
                    <h1 className="ch-title">Battles Hub <span>- SaaS arena list</span></h1>
                    <p className="ch-sub">Manage customer battles and open a workspace for optimization lifecycle.</p>
                  </div>
                  <div className="hub-actions">
                    <button type="button" className="btn btn-primary" onClick={openCreateArenaDialog}>
                      <i data-lucide="plus" />
                      Add battle
                    </button>
                  </div>
                </section>

                <section className="workspace-board">
                  <header className="workspace-board-head">
                    <div className="workspace-board-label">Battles</div>
                    <div className="workspace-board-count">{state.arenas.length} total</div>
                  </header>
                  <div className="workspace-grid" id="workspace-grid">
                    {state.arenas.length === 0 ? (
                      <div className="workspace-card workspace-card--empty">No battle yet. Click <b>Add battle</b> to create the first one.</div>
                    ) : (
                      state.arenas.map((arena, index) => {
                        const metrics = buildArenaCardMetrics(arena, index);
                        const isChampionCard = index === 0;
                        const isActiveCard = state.activeArenaId ? state.activeArenaId === arena.workspace_id : index === 0;
                        const isCardMenuOpen = arenaMenuOpenId === arena.workspace_id;
                        return (
                          <article key={arena.workspace_id} className={`workspace-arch-card${isChampionCard ? " is-champion" : ""}${isActiveCard ? " is-active" : ""}`} onClick={() => { handleSelectArenaCard(arena.workspace_id); }}>
                            <div className="workspace-arch-head">
                              <div>
                                <div className="workspace-card-title">{arena.name}</div>
                                <div className="workspace-card-meta">{arena.workspace_id}</div>
                              </div>
                              <div className="workspace-head-actions">
                                <span className={`workspace-pill${isChampionCard ? " champ" : " base"}`}><span className="dot" />{isChampionCard ? "Champion" : "Baseline"}</span>
                                <div className="workspace-menu-wrap">
                                  <button type="button" className="workspace-menu-trigger" aria-label="Open battle menu" onClick={(event) => { event.stopPropagation(); setArenaMenuOpenId((prev) => (prev === arena.workspace_id ? null : arena.workspace_id)); }}>
                                    <i data-lucide="ellipsis" />
                                  </button>
                                  {isCardMenuOpen ? (
                                    <div className="workspace-menu">
                                      <button type="button" className="workspace-menu-item" onClick={() => { openRenameArenaDialog(arena); }}>Rename</button>
                                      <button type="button" className="workspace-menu-item" onClick={() => { void handleDuplicateArena(arena.workspace_id); }}>Duplicate</button>
                                      <button type="button" className="workspace-menu-item is-destructive" onClick={() => { void handleDeleteArena(arena.workspace_id); }}>Delete</button>
                                    </div>
                                  ) : null}
                                </div>
                              </div>
                            </div>
                            <div className="workspace-arch-metrics">
                              <div className="workspace-metric"><span className="m-val">{metrics.agents}</span><span className="m-lbl">agents</span></div>
                              <div className="workspace-metric"><span className="m-val">{metrics.tests}</span><span className="m-lbl">tests</span></div>
                              <div className="workspace-metric"><span className="m-val">{metrics.dataRows}</span><span className="m-lbl">data rows</span></div>
                            </div>
                            <div className="workspace-card-footer">
                              <div className="workspace-card-sub">{arena.description || "No description"}</div>
                              <button type="button" className="btn btn-secondary" onClick={(event) => { event.stopPropagation(); void handleOpenArena(arena.workspace_id); }}>Open battle</button>
                            </div>
                          </article>
                        );
                      })
                    )}
                  </div>
                </section>

                <section className="trace-view">
                  <header className="tv-head"><div className="tv-title"><i data-lucide="file-json-2" /><span>Last payload</span></div></header>
                  <div className="tv-body"><pre className="json-view">{state.jsonText}</pre></div>
                </section>
              </>
            ) : (
              <>
                <section className="content-head">
                  <div>
                    <h1 className="ch-title">{activeArena?.name ?? route.arenaId} <span>- battle workspace</span></h1>
                    <p className="ch-sub">Discuss task in chat and inspect generated candidate architectures.</p>
                  </div>
                </section>

                <section className="metric-strip" id="metric-strip-battle">
                  <article className="ms-cell"><div className="ms-lbl">Battle</div><div className="ms-row"><div className="ms-val">{activeArena?.name ?? "n/a"}</div></div><div className="ms-cap">Active arena context</div></article>
                  <article className="ms-cell"><div className="ms-lbl">Messages</div><div className="ms-row"><div className="ms-val">{state.c2Messages.length}</div></div><div className="ms-cap">C2 chat history</div></article>
                  <article className="ms-cell"><div className="ms-lbl">Candidates</div><div className="ms-row"><div className="ms-val">{state.c2CandidateSetDraft?.total ?? 0}</div></div><div className="ms-cap">Drafted architectures</div></article>
                  <article className="ms-cell"><div className="ms-lbl">Capability</div><div className="ms-row"><div className="ms-val">{activeCapability.id.toUpperCase()}</div></div><div className="ms-cap">{activeCapability.name}</div></article>
                </section>

                {activeCapability.id === "c3" ? (
                  <section className="trace-view trace-view--workspace">
                    <header className="tv-head">
                      <div className="tv-title">
                        <i data-lucide="library" />
                        <span>Pattern library + retrieval</span>
                        <span className="tv-arch">{state.c3Patterns.length} shown</span>
                      </div>
                    </header>
                    <div className="tv-body tv-body--workspace">
                      <section className="c3-panel">
                        <div className="c3-toolbar">
                          <input
                            id="c3-pattern-query"
                            type="text"
                            value={state.c3PatternQuery}
                            onChange={(event) => {
                              setState((prev) => ({ ...prev, c3PatternQuery: event.target.value }));
                            }}
                            onKeyDown={(event) => {
                              if (event.key === "Enter") {
                                event.preventDefault();
                                void handleC3Search();
                              }
                            }}
                            placeholder="Search patterns: rewrite, safety, rag..."
                            disabled={!state.activeArenaId}
                          />
                          <div className="c3-toolbar-actions">
                            <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleC3Search(); }} disabled={!state.activeArenaId}>
                              Search
                            </button>
                            <button
                              type="button"
                              className="tb-btn tb-btn-ghost"
                              onClick={() => { void handleSaveC3PatternSelection(); }}
                              disabled={!state.activeArenaId || !state.c3SelectionDirty}
                            >
                              Save
                            </button>
                          </div>
                          <div className="c3-meta">
                            <span>selected {state.c3SelectedPatternIds.length}</span>
                            <span>{state.c3SearchMeta}</span>
                          </div>
                        </div>
                        <div className="c3-list">
                          {state.c3Patterns.length === 0 ? (
                            <div className="issue-row info">No patterns yet. Run search or open C3 in selected arena.</div>
                          ) : state.c3Patterns.map((pattern) => {
                            const isSelected = state.c3SelectedPatternIds.includes(pattern.pattern_id);
                            const isExpanded = state.c3ExpandedPatternId === pattern.pattern_id;
                            return (
                              <Fragment key={pattern.pattern_id}>
                                <article className={`c3-pattern-row${isSelected ? " is-selected" : ""}`}>
                                  <div className="c3-pattern-select-col">
                                    <input
                                      type="checkbox"
                                      checked={isSelected}
                                      onChange={() => {
                                        handleToggleC3PatternSelection(pattern.pattern_id);
                                      }}
                                      aria-label={`select-${pattern.pattern_id}-for-generation`}
                                    />
                                  </div>
                                  <div className="c3-pattern-main">
                                    <div className="c3-pattern-title">
                                      <span>{pattern.title}</span>
                                      <span className="workspace-pill base">
                                        <span className="dot" />
                                        {pattern.complexity}
                                      </span>
                                    </div>
                                    <div className="c3-pattern-id">{pattern.pattern_id}</div>
                                    <div className="c3-pattern-summary">{pattern.summary}</div>
                                    <div className="c3-pattern-tags">
                                      {pattern.tags.map((tag) => (
                                        <span key={`${pattern.pattern_id}:${tag}`} className="c3-tag">{tag}</span>
                                      ))}
                                    </div>
                                  </div>
                                  <div className="c3-pattern-side">
                                    <div className="c3-pattern-score">{pattern.relevance.toFixed(3)}</div>
                                    <div className="c3-pattern-score-label">retrieval score</div>
                                    <div className="c3-pattern-trace">{pattern.retrieval_trace.join(" · ")}</div>
                                    <div className="c3-pattern-actions">
                                      <button
                                        type="button"
                                        className="tb-btn tb-btn-ghost"
                                        onClick={() => {
                                          handleToggleC3PatternDetails(pattern.pattern_id);
                                        }}
                                        aria-expanded={isExpanded}
                                        aria-controls={`c3-pattern-details-${pattern.pattern_id}`}
                                      >
                                        Details
                                      </button>
                                    </div>
                                  </div>
                                </article>
                                {isExpanded ? (
                                  <section id={`c3-pattern-details-${pattern.pattern_id}`} className="c3-pattern-details-panel" role="region" aria-label="c3 pattern details">
                                    <div className="candidate-details-head">
                                      <div className="candidate-details-logo" aria-label={`c3-logo-${pattern.pattern_id}`}>
                                        {pattern.logo?.label ?? "PT"}
                                      </div>
                                      <div>
                                        <div className="candidate-details-title">{pattern.title}</div>
                                        <div className="candidate-details-sub">Template schema and diagnostics for pattern selection.</div>
                                      </div>
                                    </div>
                                    <div className="candidate-config-grid">
                                      <div className="candidate-config-cell"><span>roles</span><b>{pattern.config_summary?.roles_total ?? 0}</b></div>
                                      <div className="candidate-config-cell"><span>llm calls</span><b>{pattern.config_summary?.llm_calls_max ?? 0}</b></div>
                                      <div className="candidate-config-cell"><span>guards</span><b>{pattern.config_summary?.deterministic_guards ?? 0}</b></div>
                                      <div className="candidate-config-cell"><span>hitl</span><b>{pattern.config_summary?.hitl_checkpoints ?? 0}</b></div>
                                    </div>
                                    <div className="candidate-mini-graph" aria-label="c3-pattern-mini-graph">
                                      {renderPatternMiniGraphSvg(pattern)}
                                    </div>
                                    <div className="c3-trace-block">
                                      <div className="c3-trace-title">Retrieval trace</div>
                                      <div className="c3-trace-list">
                                        {pattern.retrieval_trace.map((traceItem) => (
                                          <span key={`${pattern.pattern_id}:${traceItem}`} className="candidate-step-chip">{traceItem}</span>
                                        ))}
                                      </div>
                                    </div>
                                    <div className="candidate-steps-list">
                                      {(pattern.agent_template?.rationale_steps ?? []).map((step) => (
                                        <span key={`${pattern.pattern_id}:${step}`} className="candidate-step-chip">{step}</span>
                                      ))}
                                    </div>
                                  </section>
                                ) : null}
                              </Fragment>
                            );
                          })}
                        </div>
                      </section>
                    </div>
                  </section>
                ) : (isDatasetCapability || isMetricsCapability || isStageMappingCapability || isEvaluatorsCapability) ? (
                  <section className="trace-view trace-view--workspace">
                    <header className="tv-head">
                      <div className="tv-title">
                        <i data-lucide={isDatasetCapability ? "database" : isMetricsCapability ? "line-chart" : isStageMappingCapability ? "waypoints" : "shield-check"} />
                        <span>{isDatasetCapability ? "Datasets studio" : isMetricsCapability ? "Metrics studio" : isStageMappingCapability ? "Stage Mapping studio" : "Evaluators studio"}</span>
                        <span className="tv-arch">{isDatasetCapability ? `${state.c4Datasets.length} datasets` : isMetricsCapability ? `${state.c4ComparativeMetrics.length} metrics` : isStageMappingCapability ? `${state.c4StageMappings.length} mappings` : `${state.c4Evaluators.length} evaluators`}</span>
                      </div>
                    </header>
                    <div className="tv-body tv-body--workspace">
                      <section className="c4-panel">
                        {isDatasetCapability ? (
                          state.c4ViewMode === "list" ? (
                          <>
                            <div className="c4-create-row">
                              <input
                                type="text"
                                value={state.c4NewDatasetName}
                                onChange={(event) => {
                                  setState((prev) => ({ ...prev, c4NewDatasetName: event.target.value }));
                                }}
                                placeholder="Dataset name"
                                disabled={!state.activeArenaId}
                              />
                              <input
                                type="text"
                                value={state.c4NewDatasetDescription}
                                onChange={(event) => {
                                  setState((prev) => ({ ...prev, c4NewDatasetDescription: event.target.value }));
                                }}
                                placeholder="Description"
                                disabled={!state.activeArenaId}
                              />
                              <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleCreateC4Dataset(); }} disabled={!state.activeArenaId}>
                                Create dataset
                              </button>
                            </div>
                            <div className="candidate-list">
                              <div className="candidate-list-head">
                                <span>Datasets · sorted by update time</span>
                                <div className="candidate-list-head-right">
                                  <span className="muted">assigned {state.c4AssignedDatasetIds.length}</span>
                                  <button
                                    type="button"
                                    className="tb-btn tb-btn-ghost candidate-compile-action"
                                    onClick={() => {
                                      void handleSaveC4DatasetAssignment();
                                    }}
                                    disabled={!state.activeArenaId}
                                  >
                                    Save
                                  </button>
                                </div>
                              </div>
                              <div className="candidate-list-scroll">
                                <div className="candidate-table-head">
                                  <span className="candidate-col-check">use</span>
                                  <span className="candidate-col-title">Dataset</span>
                                  <span className="candidate-col-metric">rows</span>
                                  <span className="candidate-col-metric">versions</span>
                                  <span className="candidate-col-metric">updated</span>
                                  <span className="candidate-col-action">details</span>
                                </div>
                                {state.c4Datasets.length === 0 ? (
                                  <div className="issue-row info">No datasets yet. Create your first dataset above.</div>
                                ) : state.c4Datasets.map((dataset) => {
                                  const isSelected = state.c4SelectedDatasetIds.includes(dataset.dataset_id);
                                  const isAssigned = state.c4AssignedDatasetIds.includes(dataset.dataset_id);
                                  const isExpanded = state.c4ExpandedDatasetId === dataset.dataset_id;
                                  const updatedLabel = dataset.updated_at ? dataset.updated_at.slice(0, 16).replace("T", " ") : "n/a";
                                  return (
                                    <Fragment key={dataset.dataset_id}>
                                      <article
                                        className={`candidate-row${state.c4ActiveDatasetId === dataset.dataset_id ? " candidate-row--active" : ""}`}
                                        role="button"
                                        tabIndex={0}
                                        onClick={() => {
                                          void handleSelectC4Dataset(dataset.dataset_id);
                                        }}
                                        onKeyDown={(event) => {
                                          if (event.key === "Enter" || event.key === " ") {
                                            event.preventDefault();
                                            void handleSelectC4Dataset(dataset.dataset_id);
                                          }
                                        }}
                                      >
                                        <div className="candidate-col-check">
                                          <input
                                            type="checkbox"
                                            checked={isSelected}
                                            onChange={() => {
                                              handleToggleC4DatasetSelection(dataset.dataset_id);
                                            }}
                                            onClick={(event) => {
                                              event.stopPropagation();
                                            }}
                                            aria-label={`select-${dataset.dataset_id}-for-arena`}
                                          />
                                        </div>
                                        <div className="candidate-col-title">
                                          <div className="candidate-title-line">
                                            <b>{dataset.name}</b>
                                            <span className={`workspace-pill${isAssigned ? " champ" : " base"}`}>
                                              <span className="dot" />
                                              {isAssigned ? "Assigned" : "Available"}
                                            </span>
                                          </div>
                                          <div className="candidate-meta">{dataset.dataset_id}</div>
                                          <div className="row-sub">{dataset.description || "No description."}</div>
                                        </div>
                                        <div className="candidate-col-metric">
                                          <div className="candidate-metric-value">{dataset.rows_total}</div>
                                          <div className="candidate-metric-label">cases</div>
                                        </div>
                                        <div className="candidate-col-metric">
                                          <div className="candidate-metric-value">{dataset.versions_total}</div>
                                          <div className="candidate-metric-label">saved</div>
                                        </div>
                                        <div className="candidate-col-metric">
                                          <div className="candidate-metric-value c4-updated">{updatedLabel}</div>
                                          <div className="candidate-metric-label">utc</div>
                                        </div>
                                        <div className="candidate-col-action c4-actions">
                                          <button
                                            type="button"
                                            className="candidate-details-toggle"
                                            onClick={(event) => {
                                              event.stopPropagation();
                                              handleToggleC4DatasetDetails(dataset.dataset_id);
                                            }}
                                            aria-expanded={isExpanded}
                                            aria-controls={`c4-dataset-details-${dataset.dataset_id}`}
                                          >
                                            Details
                                          </button>
                                          <button
                                            type="button"
                                            className="candidate-details-toggle"
                                            onClick={(event) => {
                                              event.stopPropagation();
                                              void handleOpenC4DatasetEditor(dataset.dataset_id);
                                            }}
                                          >
                                            Edit
                                          </button>
                                        </div>
                                      </article>
                                      {isExpanded ? (
                                        <section id={`c4-dataset-details-${dataset.dataset_id}`} className="c4-dataset-details-panel" role="region" aria-label="c4 dataset details">
                                          <div className="c4-details-title">Preview first 5 rows</div>
                                          {dataset.preview_rows.length === 0 ? (
                                            <div className="issue-row info">Dataset has no rows yet.</div>
                                          ) : (
                                            <div className="c4-preview-list">
                                              {dataset.preview_rows.map((row, rowIndex) => (
                                                <div key={`${dataset.dataset_id}:preview:${row.case_id}:${rowIndex}`} className="c4-preview-row">
                                                  <span className="c4-preview-case">{row.case_id}</span>
                                                  <span className="c4-preview-text">{row.input || "input is empty"}</span>
                                                </div>
                                              ))}
                                            </div>
                                          )}
                                        </section>
                                      ) : null}
                                    </Fragment>
                                  );
                                })}
                              </div>
                            </div>
                          </>
                        ) : (
                          <div className="c4-editor-screen">
                            <div className="c4-breadcrumbs">
                              <button type="button" className="c4-breadcrumb-link" onClick={handleBackToC4DatasetList}>Datasets</button>
                              <span>/</span>
                              <span>{state.c4ActiveDataset?.name ?? state.c4EditorDatasetId}</span>
                              <span>/</span>
                              <span>Edit</span>
                            </div>
                            <div className="c4-toolbar c4-toolbar--editor">
                              <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC4EditorChanges(); }}>
                                Save changes
                              </button>
                              <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleValidateC4Dataset(); }}>
                                Validate
                              </button>
                              <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC4DatasetVersion(); }}>
                                Save version
                              </button>
                              <button type="button" className="tb-btn tb-btn-ghost" onClick={handleBackToC4DatasetList}>
                                Back
                              </button>
                            </div>
                            <div className="c4-row-editor c4-row-editor--list">
                              <button type="button" className="tb-btn tb-btn-ghost" onClick={handleAddC4EditorRow}>Add row</button>
                            </div>
                            <div className="c4-table-wrap">
                              <table className="c4-table c4-table--editor">
                                <thead>
                                  <tr>
                                    <th>case_id</th>
                                    <th>input</th>
                                    <th>target_stage</th>
                                    <th>expected</th>
                                    <th>notes</th>
                                    <th />
                                  </tr>
                                </thead>
                                <tbody>
                                  {state.c4EditorRows.length === 0 ? (
                                    <tr>
                                      <td colSpan={6}>No rows yet.</td>
                                    </tr>
                                  ) : state.c4EditorRows.map((row, rowIndex) => (
                                    <tr key={`${state.c4EditorDatasetId}:${rowIndex}`}>
                                      <td><input value={row.case_id} onChange={(event) => { handleUpdateC4EditorRowField(rowIndex, "case_id", event.target.value); }} /></td>
                                      <td><input value={row.input} onChange={(event) => { handleUpdateC4EditorRowField(rowIndex, "input", event.target.value); }} /></td>
                                      <td>
                                        <select value={row.target_stage} onChange={(event) => { handleUpdateC4EditorRowField(rowIndex, "target_stage", event.target.value); }}>
                                          <option value="final">final</option>
                                          <option value="synthesis">synthesis</option>
                                          <option value="rerank">rerank</option>
                                          <option value="retrieval">retrieval</option>
                                        </select>
                                      </td>
                                      <td><input value={row.expected} onChange={(event) => { handleUpdateC4EditorRowField(rowIndex, "expected", event.target.value); }} /></td>
                                      <td><input value={row.notes} onChange={(event) => { handleUpdateC4EditorRowField(rowIndex, "notes", event.target.value); }} /></td>
                                      <td>
                                        <button type="button" className="candidate-details-toggle" onClick={() => { handleDeleteC4EditorRow(rowIndex); }}>
                                          Delete
                                        </button>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                            <div className="c4-import-block">
                              <textarea
                                value={state.c4EditorImportJsonl}
                                onChange={(event) => {
                                  setState((prev) => ({ ...prev, c4EditorImportJsonl: event.target.value }));
                                }}
                                placeholder='JSONL import, one row per line: {"case_id":"case_1","input":"...","target_stage":"retrieval|rerank|synthesis|final","expected_payload":{...},"expected":"...","notes":"..."}'
                              />
                              <button type="button" className="tb-btn tb-btn-ghost" onClick={handleImportC4EditorJsonl}>
                                Import JSONL (replace in editor)
                              </button>
                            </div>
                            {state.c4ValidationStatus !== "not_run" ? (
                              <div className="issues-box">
                                <div className={`issue-row ${state.c4ValidationStatus === "ok" ? "info" : "warning"}`}>
                                  Validation status: {state.c4ValidationStatus}
                                </div>
                                {state.c4ValidationIssues.map((issue, issueIndex) => (
                                  <div key={`${issue.code}:${issueIndex}`} className={`issue-row ${issue.severity === "error" ? "error" : "warning"}`}>
                                    [{issue.code}] {issue.message}
                                  </div>
                                ))}
                              </div>
                            ) : null}
                          </div>
                        )) : null}
                        {!isDatasetCapability ? (
                          <div className="c4-eval-panel">
                          <div className="candidate-list-head">
                            <span>{isMetricsCapability ? "Metrics profile" : isStageMappingCapability ? "Stage mapping profile" : "Evaluators profile"}</span>
                            <div className="candidate-list-head-right">
                              <span className="muted">{isMetricsCapability ? `comparative ${state.c4ComparativeMetrics.length}` : isStageMappingCapability ? `rows ${state.c4StageMappings.length}` : `evaluators ${state.c4Evaluators.length}`}</span>
                              <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleValidateC4EvaluationProfile(); }} disabled={!state.activeArenaId}>
                                Validate profile
                              </button>
                              {isMetricsCapability ? (
                                <button type="button" className="tb-btn tb-btn-primary" onClick={() => { void handleSuggestC4EvaluationMetrics(); }} disabled={!state.activeArenaId}>
                                  Suggest metrics
                                </button>
                              ) : null}
                              {isEvaluatorsCapability ? (
                                <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC4EvaluationVersion(); }} disabled={!state.activeArenaId}>
                                  Save version
                                </button>
                              ) : null}
                            </div>
                          </div>
                          {isMetricsCapability ? (
                            <div className="issue-row info c4-feature-summary">
                              Candidate features: {formatCandidateFeatureSummary(state.c4CandidateFeatures)}
                            </div>
                          ) : null}
                          <div className="c4-eval-grid">
                            {isMetricsCapability ? (
                              <>
                                <section className="c4-eval-card c4-eval-card--full c4-proposal-card">
                                  <div className="c4-eval-card-title">
                                    AI metric proposal
                                    {state.c4MetricProposal ? <span className="c4-eval-kind-chip">{state.c4MetricProposal.status}</span> : null}
                                  </div>
                                  {!state.c4MetricProposal ? (
                                    <div className="issue-row info">No metric proposal yet. Use Suggest metrics or ask the Metrics copilot to suggest metrics.</div>
                                  ) : (
                                    <>
                                      <div className="c4-proposal-summary">
                                        <b>{state.c4MetricProposal.summary}</b>
                                        <span>{state.c4MetricProposal.source} · {state.c4MetricProposal.created_at}</span>
                                      </div>
                                      <div className="c4-proposal-list">
                                        {state.c4MetricProposal.items.map((item) => {
                                          const isReviewOnly = item.compatibility_status === "review_only";
                                          const isSelected = state.c4SelectedMetricProposalItemIds.includes(item.proposal_item_id);
                                          return (
                                            <label key={item.proposal_item_id} className={`c4-proposal-item${isReviewOnly ? " c4-proposal-item--disabled" : ""}`}>
                                              <input
                                                type="checkbox"
                                                checked={isSelected}
                                                onChange={() => {
                                                  handleToggleC4MetricProposalItem(item.proposal_item_id);
                                                }}
                                                aria-label={`toggle-proposal-item-${item.metric_id}`}
                                                disabled={isReviewOnly || state.c4MetricProposal?.status === "applied"}
                                              />
                                              <div className="c4-proposal-item-body">
                                                <div className="c4-proposal-item-title">
                                                  {item.title}
                                                  <span className="candidate-step-chip">{item.metric_kind}</span>
                                                  <span className="candidate-step-chip">{item.target_stage}</span>
                                                </div>
                                                <div className="c4-eval-item-sub">{item.description}</div>
                                                <div className="c4-proposal-rationale">{item.rationale}</div>
                                                <div className="c4-eval-requirements">
                                                  {item.recommended_evaluators.length > 0 ? item.recommended_evaluators.map((evaluatorId) => (
                                                    <span key={`${item.proposal_item_id}:${evaluatorId}`} className="candidate-step-chip">eval: {evaluatorId}</span>
                                                  )) : <span className="candidate-step-chip">eval: manual</span>}
                                                </div>
                                                {item.compatibility_reason ? <div className="c4-eval-item-hint">{item.compatibility_reason}</div> : null}
                                              </div>
                                              {item.metric_kind === "comparative" ? <span className="c4-proposal-weight">w {item.weight}</span> : null}
                                            </label>
                                          );
                                        })}
                                      </div>
                                      <button
                                        type="button"
                                        className="tb-btn tb-btn-ghost"
                                        onClick={() => { void handleApplyC4MetricProposal(); }}
                                        disabled={
                                          !state.activeArenaId ||
                                          state.c4MetricProposal.status === "applied" ||
                                          state.c4SelectedMetricProposalItemIds.length <= 0
                                        }
                                      >
                                        Apply selected
                                      </button>
                                    </>
                                  )}
                                </section>
                                <section className="c4-eval-card">
                                  <div className="c4-eval-card-title">Comparative metrics</div>
                                  <div className="c4-eval-list">
                                    {state.c4ComparativeMetrics.map((metric) => {
                                      const metricAvailable = isAvailabilityEnabled(metric.availability_status);
                                      return (
                                      <label key={metric.metric_id} className={`c4-eval-item${metricAvailable ? "" : " c4-eval-item--disabled"}`}>
                                        <input
                                          type="checkbox"
                                          checked={metric.enabled}
                                          onChange={() => {
                                            handleToggleC4ComparativeMetric(metric.metric_id);
                                          }}
                                          aria-label={`toggle-metric-${metric.metric_id}`}
                                          disabled={!metricAvailable}
                                        />
                                        <div className="c4-eval-item-body">
                                          <div className="c4-eval-item-title">{metric.title}</div>
                                          <div className="c4-eval-item-sub">{metric.description}</div>
                                          {!metricAvailable ? <div className="c4-eval-item-hint">{metric.availability_reason || "Unavailable for selected candidate structures."}</div> : null}
                                        </div>
                                        <input
                                          className="c4-weight-input"
                                          type="number"
                                          step="0.05"
                                          value={metric.weight}
                                          onChange={(event) => {
                                            handleChangeC4ComparativeMetricWeight(metric.metric_id, event.target.value);
                                          }}
                                          disabled={!metricAvailable}
                                        />
                                      </label>
                                    );})}
                                  </div>
                                  <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC4EvaluationMetrics(); }} disabled={!state.activeArenaId}>
                                    Save metrics
                                  </button>
                                </section>
                                <section className="c4-eval-card">
                                  <div className="c4-eval-card-title">Diagnostic signals</div>
                                  <div className="c4-eval-list">
                                    {state.c4DiagnosticSignals.map((signal) => {
                                      const signalAvailable = isAvailabilityEnabled(signal.availability_status);
                                      return (
                                      <label key={signal.signal_id} className={`c4-eval-item${signalAvailable ? "" : " c4-eval-item--disabled"}`}>
                                        <input
                                          type="checkbox"
                                          checked={signal.enabled}
                                          onChange={() => {
                                            handleToggleC4DiagnosticSignal(signal.signal_id);
                                          }}
                                          aria-label={`toggle-signal-${signal.signal_id}`}
                                          disabled={!signalAvailable}
                                        />
                                        <div className="c4-eval-item-body">
                                          <div className="c4-eval-item-title">{signal.title}</div>
                                          <div className="c4-eval-item-sub">{signal.description}</div>
                                          {!signalAvailable ? <div className="c4-eval-item-hint">{signal.availability_reason || "Unavailable for selected candidate structures."}</div> : null}
                                        </div>
                                      </label>
                                    );})}
                                  </div>
                                  <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC4EvaluationMetrics(); }} disabled={!state.activeArenaId}>
                                    Save diagnostics
                                  </button>
                                </section>
                              </>
                            ) : null}
                            {isStageMappingCapability ? (
                              <section className="c4-eval-card c4-eval-card--full">
                                <div className="c4-eval-card-title">Stage mapping (target_stage {"->"} candidate nodes)</div>
                                <div className="c4-stage-binding-grid">
                                  <div className="c4-stage-binding-head">
                                    <span>Enabled</span>
                                    <span>Stage</span>
                                    <span>Candidate</span>
                                    <span>Node ids</span>
                                    <span>Status</span>
                                    <span>Notes</span>
                                    <span>Row</span>
                                  </div>
                                  {state.c4StageMappings.length <= 0 ? (
                                    <div className="issue-row info">No stage mapping rows yet. Add one manually or use auto-init suggestions.</div>
                                  ) : state.c4StageMappings.map((mapping) => {
                                    const coverage = c4StageCoverageByMappingId.get(mapping.mapping_id);
                                    const status = mapping.source === "manual" ? mapping.status : coverage?.status ?? mapping.status;
                                    const confidence = mapping.source === "manual" ? mapping.confidence : coverage?.confidence ?? mapping.confidence;
                                    const statusText = status === "ambiguous" ? "needs confirmation" : status;
                                    const statusLabel = `${statusText} · conf ${Number(confidence || 0).toFixed(2)}`;
                                    return (
                                      <div key={mapping.mapping_id} className="c4-stage-binding-row">
                                        <input
                                          type="checkbox"
                                          checked={mapping.enabled}
                                          onChange={(event) => {
                                            handleUpdateC4StageMappingField(mapping.mapping_id, "enabled", event.target.checked);
                                          }}
                                          aria-label={`toggle-stage-mapping-${mapping.mapping_id}`}
                                        />
                                        <select
                                          value={mapping.target_stage}
                                          onChange={(event) => {
                                            handleUpdateC4StageMappingField(mapping.mapping_id, "target_stage", event.target.value);
                                          }}
                                          aria-label={`stage-mapping-target-${mapping.mapping_id}`}
                                        >
                                          <option value="retrieval">retrieval</option>
                                          <option value="rerank">rerank</option>
                                          <option value="synthesis">synthesis</option>
                                          <option value="final">final</option>
                                        </select>
                                        <select
                                          value={mapping.candidate_id}
                                          onChange={(event) => {
                                            handleUpdateC4StageMappingField(mapping.mapping_id, "candidate_id", event.target.value);
                                          }}
                                          aria-label={`stage-mapping-candidate-${mapping.mapping_id}`}
                                        >
                                          <option value="">Select candidate</option>
                                          {(state.c2CandidateSetDraft?.candidates ?? []).map((candidate) => (
                                            <option key={`stage-map-candidate:${mapping.mapping_id}:${candidate.candidate_id}`} value={candidate.candidate_id}>
                                              {candidate.title}
                                            </option>
                                          ))}
                                        </select>
                                        <input
                                          value={mapping.selected_node_ids.join(", ")}
                                          onChange={(event) => {
                                            handleUpdateC4StageMappingField(mapping.mapping_id, "selected_node_ids", event.target.value);
                                          }}
                                          placeholder="node_a, node_b"
                                        />
                                        <div className="c4-stage-coverage-label">{statusLabel}</div>
                                        <input
                                          value={mapping.notes}
                                          onChange={(event) => {
                                            handleUpdateC4StageMappingField(mapping.mapping_id, "notes", event.target.value);
                                          }}
                                          placeholder="optional notes"
                                        />
                                        <button
                                          type="button"
                                          className="candidate-details-toggle"
                                          onClick={() => {
                                            handleDeleteC4StageMappingRow(mapping.mapping_id);
                                          }}
                                        >
                                          Delete
                                        </button>
                                      </div>
                                    );
                                  })}
                                </div>
                                <div className="c4-stage-binding-actions">
                                  <button type="button" className="tb-btn tb-btn-ghost" onClick={handleAddC4StageMappingRow} disabled={!state.activeArenaId}>
                                    Add row
                                  </button>
                                  <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleAutoMapC4StageMappings(); }} disabled={!state.activeArenaId}>
                                    Refresh auto-map
                                  </button>
                                  <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC4StageMappings(); }} disabled={!state.activeArenaId}>
                                    Save mapping
                                  </button>
                                </div>
                              </section>
                            ) : null}
                            {isEvaluatorsCapability ? (
                              <>
                                <section className="c4-eval-card">
                                  <div className="c4-eval-card-title">Evaluators</div>
                                  <div className="c4-eval-list">
                                    {state.c4Evaluators.map((evaluator) => (
                                      <label key={evaluator.evaluator_id} className={`c4-eval-item${evaluator.adapter_status === "planned" ? " c4-eval-item--disabled" : ""}`}>
                                        <input
                                          type="checkbox"
                                          checked={evaluator.enabled}
                                          onChange={() => {
                                            handleToggleC4Evaluator(evaluator.evaluator_id);
                                          }}
                                          aria-label={`toggle-evaluator-${evaluator.evaluator_id}`}
                                        />
                                        <div className="c4-eval-item-body">
                                          <div className="c4-eval-item-title">
                                            {evaluator.title}
                                            <span className="c4-eval-kind-chip">{evaluator.adapter_kind ?? "custom"}</span>
                                          </div>
                                          <div className="c4-eval-item-sub">{evaluator.description}</div>
                                          <div className="c4-eval-requirements">
                                            {buildEvaluatorRequirementLabels(evaluator).map((label) => (
                                              <span key={`${evaluator.evaluator_id}:${label}`} className="candidate-step-chip">{label}</span>
                                            ))}
                                          </div>
                                          {evaluator.adapter_status && evaluator.adapter_status !== "available" ? (
                                            <div className="c4-eval-item-hint">{evaluator.adapter_status}: {evaluator.adapter_status_reason}</div>
                                          ) : null}
                                        </div>
                                      </label>
                                    ))}
                                  </div>
                                  <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC4EvaluationEvaluators(); }} disabled={!state.activeArenaId}>
                                    Save evaluators
                                  </button>
                                </section>
                                <section className="c4-eval-card">
                                  <div className="c4-eval-card-title">Evaluator x Metric matrix</div>
                                  <div className="c4-matrix-wrap">
                                    <table className="c4-matrix-table">
                                      <thead>
                                        <tr>
                                          <th>Metric</th>
                                          {enabledC4Evaluators.map((evaluator) => (
                                            <th key={`matrix-head:${evaluator.evaluator_id}`}>
                                              {evaluator.title}
                                              <span className="c4-matrix-row-meta">{evaluator.adapter_kind ?? "custom"}</span>
                                            </th>
                                          ))}
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {[
                                          ...state.c4ComparativeMetrics.map((metric) => ({
                                            metric_kind: "comparative" as const,
                                            metric_id: metric.metric_id,
                                            title: metric.title,
                                            enabled: metric.enabled,
                                            availability_status: metric.availability_status,
                                          })),
                                          ...state.c4DiagnosticSignals.map((signal) => ({
                                            metric_kind: "diagnostic" as const,
                                            metric_id: signal.signal_id,
                                            title: signal.title,
                                            enabled: signal.enabled,
                                            availability_status: signal.availability_status,
                                          })),
                                        ].map((metricTarget) => {
                                          const metricAvailable = isAvailabilityEnabled(metricTarget.availability_status);
                                          const metricIsActive = metricTarget.enabled && metricAvailable;
                                          return (
                                            <tr key={`matrix-row:${metricTarget.metric_kind}:${metricTarget.metric_id}`} className={metricIsActive ? "" : "is-muted"}>
                                              <td>
                                                {metricTarget.title}
                                                <span className="c4-matrix-row-meta">{metricTarget.metric_kind}</span>
                                              </td>
                                              {enabledC4Evaluators.map((evaluator) => {
                                                const link = state.c4EvaluatorMetricLinks.find(
                                                  (item) =>
                                                    item.evaluator_id === evaluator.evaluator_id &&
                                                    item.metric_kind === metricTarget.metric_kind &&
                                                    item.metric_id === metricTarget.metric_id
                                                );
                                                const compatibility = resolveEvaluatorMetricCompatibility(
                                                  evaluator,
                                                  metricTarget.metric_kind,
                                                  metricTarget.metric_id,
                                                  link
                                                );
                                                const compatibilityBlocked = compatibility.status === "incompatible";
                                                const cellDisabled = !metricAvailable || (compatibilityBlocked && !link?.enabled);
                                                return (
                                                  <td
                                                    key={`matrix-cell:${evaluator.evaluator_id}:${metricTarget.metric_kind}:${metricTarget.metric_id}`}
                                                    title={compatibility.reason}
                                                  >
                                                    <input
                                                      type="checkbox"
                                                      checked={Boolean(link?.enabled) && !compatibilityBlocked}
                                                      onChange={() => {
                                                        handleToggleC4EvaluatorMetricLink(
                                                          evaluator.evaluator_id,
                                                          metricTarget.metric_kind,
                                                          metricTarget.metric_id
                                                        );
                                                      }}
                                                      aria-label={`toggle-matrix-${evaluator.evaluator_id}-${metricTarget.metric_kind}-${metricTarget.metric_id}`}
                                                      disabled={cellDisabled || compatibilityBlocked}
                                                    />
                                                    {compatibilityBlocked ? <span className="c4-matrix-cell-hint">not supported</span> : null}
                                                  </td>
                                                );
                                              })}
                                            </tr>
                                          );
                                        })}
                                        {enabledC4Evaluators.length <= 0 ? (
                                          <tr>
                                            <td colSpan={2}>Enable at least one evaluator to configure matrix coverage.</td>
                                          </tr>
                                        ) : null}
                                      </tbody>
                                    </table>
                                  </div>
                                  <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC4EvaluationMatrix(); }} disabled={!state.activeArenaId}>
                                    Save matrix
                                  </button>
                                </section>
                              </>
                            ) : null}
                          </div>
                          {state.c4EvaluationValidationStatus !== "not_run" ? (
                            <div className="issues-box">
                              <div className={`issue-row ${state.c4EvaluationValidationStatus === "ready" ? "info" : "warning"}`}>
                                Evaluation profile status: {state.c4EvaluationValidationStatus}
                              </div>
                              {state.c4EvaluationValidationIssues.map((issue, issueIndex) => (
                                <div key={`${issue.code}:${issueIndex}`} className={`issue-row ${issue.severity === "error" ? "error" : "warning"}`}>
                                  [{issue.code}] {issue.message}
                                </div>
                              ))}
                            </div>
                          ) : null}
                          <div className="c4-version-list">
                            {state.c4EvaluationVersions.length === 0 ? (
                              <span className="candidate-step-chip">No evaluation versions yet.</span>
                            ) : state.c4EvaluationVersions.map((version) => (
                              <span key={version.version_id} className="candidate-step-chip">
                                {version.label} · cmp {version.enabled_comparative_total} · diag {version.enabled_diagnostic_total} · eval {version.enabled_evaluators_total}
                              </span>
                            ))}
                          </div>
                          </div>
                        ) : null}
                      </section>
                    </div>
                  </section>
                ) : isOptimizerCapability ? (
                  <section className="trace-view trace-view--workspace">
                    <header className="tv-head">
                      <div className="tv-title">
                        <i data-lucide="activity" />
                        <span>Optimizer setup + launch guardrails</span>
                        <span className="tv-arch">{state.c5LaunchHistory.length} launches</span>
                      </div>
                    </header>
                    <div className="tv-body tv-body--workspace">
                      <section className="c4-panel">
                        <div className="candidate-list-head">
                          <span>Optimizer profile · methods / controls / budget</span>
                          <div className="candidate-list-head-right">
                            <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC5OptimizerSetup(); }} disabled={!state.activeArenaId}>
                              Save setup
                            </button>
                            <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleValidateC5OptimizerSetup(); }} disabled={!state.activeArenaId}>
                              Validate
                            </button>
                            <button type="button" className="tb-btn tb-btn-primary" onClick={() => { void handleLaunchC5Optimizer(); }} disabled={!state.activeArenaId}>
                              Launch
                            </button>
                          </div>
                        </div>
                        <div className="c5-eval-panel">
                          <div className="c5-eval-grid">
                            <section className="c5-eval-card">
                              <div className="c5-eval-card-title">Methods</div>
                              <div className="c5-eval-list">
                                {state.c5Methods.map((method) => (
                                  <label key={method.method_id} className="c5-eval-item">
                                    <input
                                      type="checkbox"
                                      checked={method.enabled}
                                      onChange={() => {
                                        handleToggleC5Method(method.method_id);
                                      }}
                                      aria-label={`toggle-method-${method.method_id}`}
                                    />
                                    <div className="c5-eval-item-body">
                                      <div className="c5-eval-item-title">{method.title}</div>
                                      <div className="c5-eval-item-sub">{method.description}</div>
                                    </div>
                                  </label>
                                ))}
                              </div>
                            </section>
                            <section className="c5-eval-card">
                              <div className="c5-eval-card-title">Optimization controls</div>
                              <div className="c5-eval-list">
                                {state.c5Controls.map((control) => (
                                  <label key={control.control_id} className="c5-eval-item">
                                    <input
                                      type="checkbox"
                                      checked={control.enabled}
                                      onChange={() => {
                                        handleToggleC5Control(control.control_id);
                                      }}
                                      aria-label={`toggle-control-${control.control_id}`}
                                    />
                                    <div className="c5-eval-item-body">
                                      <div className="c5-eval-item-title">{control.title}</div>
                                      <div className="c5-eval-item-sub">{control.description}</div>
                                    </div>
                                  </label>
                                ))}
                              </div>
                            </section>
                            <section className="c5-eval-card">
                              <div className="c5-eval-card-title">Run plan</div>
                              <div className="c5-budget-fields">
                                <label>
                                  <span>epochs total</span>
                                  <input
                                    type="number"
                                    value={state.c5RunPlan.epochs_total}
                                    onChange={(event) => {
                                      handleChangeC5RunPlanField("epochs_total", event.target.value);
                                    }}
                                  />
                                </label>
                                <label>
                                  <span>candidates / epoch</span>
                                  <input
                                    type="number"
                                    value={state.c5RunPlan.candidates_per_epoch}
                                    onChange={(event) => {
                                      handleChangeC5RunPlanField("candidates_per_epoch", event.target.value);
                                    }}
                                  />
                                </label>
                                <label>
                                  <span>parallel trials</span>
                                  <input
                                    type="number"
                                    value={state.c5RunPlan.max_parallel_trials}
                                    onChange={(event) => {
                                      handleChangeC5RunPlanField("max_parallel_trials", event.target.value);
                                    }}
                                  />
                                </label>
                                <label>
                                  <span>early stop patience</span>
                                  <input
                                    type="number"
                                    value={state.c5RunPlan.early_stop_patience}
                                    onChange={(event) => {
                                      handleChangeC5RunPlanField("early_stop_patience", event.target.value);
                                    }}
                                  />
                                </label>
                              </div>
                            </section>
                            <section className="c5-eval-card">
                              <div className="c5-eval-card-title">Budget limits</div>
                              <div className="c5-budget-fields">
                                <label>
                                  <span>max cases</span>
                                  <input
                                    type="number"
                                    value={state.c5Budget.max_cases}
                                    onChange={(event) => {
                                      handleChangeC5BudgetField("max_cases", event.target.value);
                                    }}
                                  />
                                </label>
                                <label>
                                  <span>max llm calls</span>
                                  <input
                                    type="number"
                                    value={state.c5Budget.max_llm_calls}
                                    onChange={(event) => {
                                      handleChangeC5BudgetField("max_llm_calls", event.target.value);
                                    }}
                                  />
                                </label>
                                <label>
                                  <span>max cost usd</span>
                                  <input
                                    type="number"
                                    step="0.1"
                                    value={state.c5Budget.max_cost_usd}
                                    onChange={(event) => {
                                      handleChangeC5BudgetField("max_cost_usd", event.target.value);
                                    }}
                                  />
                                </label>
                                <label>
                                  <span>max runtime min</span>
                                  <input
                                    type="number"
                                    value={state.c5Budget.max_runtime_minutes}
                                    onChange={(event) => {
                                      handleChangeC5BudgetField("max_runtime_minutes", event.target.value);
                                    }}
                                  />
                                </label>
                              </div>
                            </section>
                          </div>
                          {state.c5ValidationStatus !== "not_run" ? (
                            <div className="issues-box">
                              <div className={`issue-row ${state.c5ValidationStatus === "ready" ? "info" : "warning"}`}>
                                Optimizer preflight status: {state.c5ValidationStatus}
                              </div>
                              {state.c5ValidationIssues.map((issue, issueIndex) => (
                                <div key={`${issue.code}:${issueIndex}`} className={`issue-row ${issue.severity === "error" ? "error" : "warning"}`}>
                                  [{issue.code}] {issue.message}
                                </div>
                              ))}
                            </div>
                          ) : null}
                          <div className="c5-actions-row">
                            <button type="button" className="tb-btn tb-btn-ghost" onClick={() => { void handleSaveC5OptimizerVersion(); }} disabled={!state.activeArenaId}>
                              Save profile version
                            </button>
                          </div>
                          <div className="c5-version-list">
                            {state.c5Versions.length === 0 ? (
                              <span className="candidate-step-chip">No optimizer versions yet.</span>
                            ) : state.c5Versions.map((version) => (
                              <span key={version.version_id} className="candidate-step-chip">
                                {version.label} · methods {version.enabled_methods_total} · controls {version.enabled_controls_total} · epochs {version.epochs_total}
                              </span>
                            ))}
                          </div>
                          <div className="c5-launch-list">
                            <div className="c5-eval-card-title">Launch queue (latest)</div>
                            {state.c5LaunchHistory.length === 0 ? (
                              <div className="issue-row info">No optimizer launches yet.</div>
                            ) : (
                              state.c5LaunchHistory.map((entry) => (
                                <div key={entry.run_id} className="candidate-step-chip">
                                  {entry.run_id} · {entry.status} · {entry.method_id} · epochs {entry.epochs_total} · cand {entry.selected_candidates_total}
                                </div>
                              ))
                            )}
                          </div>
                        </div>
                      </section>
                    </div>
                  </section>
                ) : (
                  <section className="trace-view trace-view--workspace">
                    <header className="tv-head"><div className="tv-title"><i data-lucide="network" /><span>Candidate architectures</span><span className="tv-arch">{state.c2CandidateSetDraft?.total ?? 0} total</span></div></header>
                    <div className="tv-body tv-body--workspace">
                      <div className="candidate-list">
                        <div className="candidate-list-head">
                          <span>Architectures · sorted by quality</span>
                          <div className="candidate-list-head-right">
                            <span className="muted">{state.c2CandidateSetDraft?.candidate_set_id ?? "not generated"}</span>
                            <button
                              type="button"
                              className="tb-btn tb-btn-ghost candidate-compile-action"
                              onClick={() => {
                                void handleSelectCandidatesForTests();
                              }}
                              disabled={!state.activeArenaId || !state.c2CandidateSetDraft}
                            >
                              Select for tests
                            </button>
                          </div>
                        </div>
                        <div className="candidate-list-scroll">
                          <div className="candidate-table-head">
                            <span className="candidate-col-check">test</span>
                            <span className="candidate-col-title">Candidate</span>
                            <span className="candidate-col-metric">quality</span>
                            <span className="candidate-col-metric">cost/case</span>
                            <span className="candidate-col-metric">p95 latency</span>
                            <span className="candidate-col-action">details</span>
                          </div>
                          {state.c2CandidateSetDraft ? state.c2CandidateSetDraft.candidates.map((candidate, index) => {
                            const metrics = buildCandidateMetrics(candidate.candidate_id);
                            const graphNodes = candidate.mini_graph?.nodes ?? [];
                            const isExpanded = state.c2ExpandedCandidateId === candidate.candidate_id;
                            return (
                              <Fragment key={candidate.candidate_id}>
                                <article
                                  className={`candidate-row${index === 0 ? " candidate-row--champion" : ""}${state.c2SelectedCandidateId === candidate.candidate_id ? " candidate-row--active" : ""}`}
                                  role="button"
                                  tabIndex={0}
                                  onClick={() => { handleSelectCandidate(candidate.candidate_id); }}
                                  onKeyDown={(event) => {
                                    if (event.key === "Enter" || event.key === " ") {
                                      event.preventDefault();
                                      handleSelectCandidate(candidate.candidate_id);
                                    }
                                  }}
                                >
                                  <div className="candidate-col-check">
                                    <input
                                      type="checkbox"
                                      checked={state.c2SelectedForTestsIds.includes(candidate.candidate_id)}
                                      onChange={() => {
                                        handleToggleCandidateForTests(candidate.candidate_id);
                                      }}
                                      onClick={(event) => {
                                        event.stopPropagation();
                                      }}
                                      aria-label={`select-${candidate.candidate_id}-for-tests`}
                                    />
                                  </div>
                                  <div className="candidate-col-title">
                                    <div className="candidate-title-line">
                                      <b>{candidate.title}</b>
                                      <span className={`workspace-pill${index === 0 ? " champ" : " base"}`}>
                                        <span className="dot" />
                                        {index === 0 ? "Champion" : "Candidate"}
                                      </span>
                                    </div>
                                    <div className="candidate-meta">{candidate.pattern_ref}</div>
                                    <div className="row-sub">{candidate.summary}</div>
                                    {candidate.selected_for_tests ? <div className="candidate-selected-hint">selected for tests</div> : null}
                                  </div>
                                  <div className="candidate-col-metric">
                                    <div className="candidate-metric-value">{metrics.quality}</div>
                                    <div className="candidate-metric-label">f1@k</div>
                                  </div>
                                  <div className="candidate-col-metric">
                                    <div className="candidate-metric-value">${metrics.cost}</div>
                                    <div className="candidate-metric-label">usd</div>
                                  </div>
                                  <div className="candidate-col-metric">
                                    <div className="candidate-metric-value">{metrics.latency}s</div>
                                    <div className="candidate-metric-label">runtime</div>
                                  </div>
                                  <div className="candidate-col-action">
                                    <button
                                      type="button"
                                      className="candidate-details-toggle"
                                      onClick={(event) => {
                                        event.stopPropagation();
                                        handleToggleCandidateDetails(candidate.candidate_id);
                                      }}
                                      aria-expanded={isExpanded}
                                      aria-controls={`candidate-details-${candidate.candidate_id}`}
                                    >
                                      <span>Details</span>
                                      <i data-lucide={isExpanded ? "chevron-up" : "chevron-down"} />
                                    </button>
                                  </div>
                                </article>
                                {isExpanded ? (
                                  <section
                                    id={`candidate-details-${candidate.candidate_id}`}
                                    className="candidate-details-panel"
                                    role="region"
                                    aria-label="candidate details"
                                  >
                                    <div className="candidate-details-head">
                                      <div className="candidate-details-logo" aria-label={`logo-${candidate.candidate_id}`}>
                                        {candidate.logo?.label ?? "AG"}
                                      </div>
                                      <div>
                                        <div className="candidate-details-title">{candidate.title}</div>
                                        <div className="candidate-details-sub">{candidate.rationale}</div>
                                      </div>
                                    </div>
                                    <div className="candidate-config-grid">
                                      <div className="candidate-config-cell"><span>roles</span><b>{candidate.config_summary?.roles_total ?? 0}</b></div>
                                      <div className="candidate-config-cell"><span>llm calls</span><b>{candidate.config_summary?.llm_calls_max ?? 0}</b></div>
                                      <div className="candidate-config-cell"><span>guards</span><b>{candidate.config_summary?.deterministic_guards ?? 0}</b></div>
                                      <div className="candidate-config-cell"><span>hitl</span><b>{candidate.config_summary?.hitl_checkpoints ?? 0}</b></div>
                                    </div>
                                    <div className="candidate-mini-graph" aria-label="candidate-mini-graph">
                                      {renderCandidateMiniGraphSvg(candidate)}
                                      {graphNodes.length > 0 ? (
                                        <div className="candidate-mini-graph-legend">
                                          {graphNodes.map((node) => (
                                            <div key={node.id} className="mini-graph-node">
                                              <span className={`mini-node-kind kind-${node.kind}`}>{node.kind}</span>
                                              <span className="mini-node-label">{node.label}</span>
                                            </div>
                                          ))}
                                        </div>
                                      ) : null}
                                    </div>
                                    {candidate.compile_readiness?.status === "failed" ? (
                                      <div className="issues-box">
                                        <div className="issue-row error">
                                          Candidate preparation failed after internal retries ({candidate.compile_readiness.attempts_used ?? "n/a"} attempts).
                                        </div>
                                        {(candidate.compile_readiness?.issues ?? []).map((issue, issueIndex) => (
                                          <div key={`${candidate.candidate_id}:issue:${issueIndex}`} className={`issue-row ${issue.severity === "error" ? "error" : "warning"}`}>
                                            {issue.message}
                                          </div>
                                        ))}
                                      </div>
                                    ) : null}
                                    <div className="candidate-steps-list">
                                      {(candidate.architecture_steps ?? []).map((step) => (
                                        <span key={step} className="candidate-step-chip">{step}</span>
                                      ))}
                                    </div>
                                  </section>
                                ) : null}
                              </Fragment>
                            );
                          }) : (
                            <div className="issue-row warning">
                              {c2PatternGateLocked
                                ? "Select at least one pattern in C3, then open C2 and generate candidates."
                                : "No candidate draft yet. Use chat action \"Generate candidates\"."}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </section>
                )}
              </>
            )}
          </main>

          {isBattleRoute ? (
            <aside className="rail">
              <section className="chat-shell">
                <header className="chat-shell-head">
                  <div className="rail-label">Battle chat</div>
                  <div className="chat-status">{state.activeArenaId ? "online" : "offline"}</div>
                </header>
                <div className="chat-messages" ref={chatMessagesRef}>
                  {state.c2Messages.length === 0 ? (
                    <div className="chat-empty">Send first message to start architecture discussion.</div>
                  ) : state.c2Messages.map((message) => (
                    <article
                      key={message.message_id}
                      className={`chat-message${message.role === "user" ? " chat-message--user" : " chat-message--assistant"}`}
                    >
                      <div className="chat-message-role">{message.role}</div>
                      <div className="chat-message-text">{message.content}</div>
                    </article>
                  ))}
                </div>
                <div className="chat-composer">
                  <label className="c1-field-label" htmlFor="c2-chat-input">Message ({state.activeArenaId || "no battle selected"})</label>
                  {isC2ChatBlocked ? (
                    <div className="issue-row info">Before chat generation, select at least one architecture pattern in C3.</div>
                  ) : null}
                  {!isChatCapabilitySupported ? (
                    <div className="issue-row info">Contextual chat is available in C2/C4/C5/Stage Mapping/C6/C7.</div>
                  ) : null}
                  {state.c2CopilotSummary ? (
                    <div className="issue-row info">
                      {state.c2CopilotSummary}
                      {state.c2CopilotResolvedAction ? ` · action: ${state.c2CopilotResolvedAction}` : ""}
                    </div>
                  ) : null}
                  {isChatCapabilitySupported && !isC2Enabled ? (
                    <div className="issue-row info">{chatActionHint}</div>
                  ) : null}
                  <textarea
                    id="c2-chat-input"
                    value={state.c2ChatInput}
                    onChange={(event) => {
                      handleC2ChatInputChange(event.target.value);
                    }}
                    onKeyDown={handleC2ChatKeyDown}
                    placeholder={chatPlaceholder}
                    disabled={!canUseBattleChat}
                  />
                  <div className="c2-chat-actions">
                    <button
                      type="button"
                      className="tb-btn tb-btn-ghost"
                      onClick={() => {
                        void handleSendC2Message(false);
                      }}
                      disabled={!canUseBattleChat}
                    >
                      Send
                    </button>
                    <button
                      type="button"
                      className="tb-btn tb-btn-primary"
                      onClick={() => {
                        void handleSendC2Message(true);
                      }}
                      disabled={!canUseBattleChat}
                    >
                      {chatActionLabel}
                    </button>
                  </div>
                </div>
              </section>

            </aside>
          ) : null}
        </div>
      </div>

      {isBattleRoute && state.debugDrawerOpen ? (
        <aside id="debug-drawer" className="debug-drawer" aria-label="Debug drawer">
          <header className="debug-drawer-head">
            <div>
              <div className="debug-drawer-title">Debug snapshot</div>
              <div className="debug-drawer-sub">{activeCapability.id.toUpperCase()} · {state.budgetStage}</div>
            </div>
            <button type="button" className="debug-drawer-close" onClick={handleToggleDebugDrawer} aria-label="Close debug drawer">
              <i data-lucide="x" />
            </button>
          </header>
          <div className="debug-drawer-meta">
            <div><span>progress</span><b>{state.budgetPercent}%</b></div>
            <div><span>payload</span><b>{state.lastPayload ? "available" : "empty"}</b></div>
            <div><span>battle</span><b>{state.activeArenaId || "none"}</b></div>
          </div>
          <pre className="json-view debug-drawer-json">{state.jsonText}</pre>
        </aside>
      ) : null}

      {arenaDialogMode ? (
        <div className="workspace-modal-overlay" onClick={closeArenaDialog}>
          <div className="workspace-modal-card" onClick={(event) => { event.stopPropagation(); }}>
            <div className="workspace-modal-title">{arenaDialogMode === "create" ? "Create battle" : "Rename battle"}</div>
            <div className="workspace-modal-subtitle">{arenaDialogMode === "create" ? "Add a new battle for a separate optimization challenge." : "Update battle display name."}</div>
            <div className="workspace-modal-form">
              <label htmlFor="arena-dialog-name">Name</label>
              <input id="arena-dialog-name" type="text" value={arenaDialogName} onChange={(event) => { setArenaDialogName(event.target.value); }} placeholder="support-qa" />
              {arenaDialogMode === "create" ? (
                <>
                  <label htmlFor="arena-dialog-description">Description</label>
                  <textarea id="arena-dialog-description" value={arenaDialogDescription} onChange={(event) => { setArenaDialogDescription(event.target.value); }} placeholder="Optional battle description" />
                </>
              ) : null}
            </div>
            <div className="workspace-modal-actions">
              <button type="button" className="btn btn-secondary" onClick={closeArenaDialog}>Cancel</button>
              <button type="button" className="btn btn-primary" onClick={() => { void handleSubmitArenaDialog(); }}>
                {arenaDialogMode === "create" ? "Create battle" : "Save name"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

// Русский комментарий: вычисляет wizard-статусы capability-меню на основе текущего прогресса battle.
function buildCapabilityWizardItems(capabilities: Capability[], state: UiState, isBattleRoute: boolean): CapabilityWizardItem[] {
  if (!isBattleRoute) {
    return capabilities.map((capability) => ({
      ...capability,
      wizardStatus: "available",
      wizardReason: "Open battle workspace to start the wizard flow.",
      isInteractive: true,
    }));
  }

  const hasBattle = Boolean(state.activeArenaId);
  const candidateTotal = state.c2CandidateSetDraft?.total ?? 0;
  const hasCandidates = candidateTotal > 0;
  const hasSelectedCandidates = state.c2SelectedForTestsIds.length > 0;
  const hasAssignedDatasets = state.c4AssignedDatasetIds.length > 0;
  const hasEnabledComparativeMetrics = state.c4ComparativeMetrics.some(
    (item) => item.enabled && isAvailabilityEnabled(item.availability_status)
  );
  const enabledNonFinalDiagnosticStages = state.c4DiagnosticSignals
    .filter((item) => item.enabled && isAvailabilityEnabled(item.availability_status))
    .map((item) => mapDiagnosticSignalToStage(item.signal_id))
    .filter((stage): stage is "retrieval" | "rerank" | "synthesis" => stage !== null);
  const requiredStageTargets = Array.from(new Set(enabledNonFinalDiagnosticStages));
  const stageMappingRequired = requiredStageTargets.length > 0;
  const hasReadyStageMappingCoverage = requiredStageTargets.every((targetStage) =>
    state.c4StageMappingCoverage.some(
      (row) =>
        row.enabled &&
        row.target_stage === targetStage &&
        (row.status === "bound" || row.status === "ambiguous")
    )
  );
  const hasEnabledEvaluators = state.c4Evaluators.some((item) => item.enabled);
  const hasOptimizerRuns = state.c5LaunchHistory.length > 0;
  const optimizerPreflightBlocked = state.c5ValidationStatus === "invalid";
  const compileGateBlocked = state.c2CandidateSetDraft?.compile_gate?.status === "failed";

  return capabilities.map((capability) => {
    if (capability.id === "c1") {
      return {
        ...capability,
        wizardStatus: "completed",
        wizardReason: "Battle is already selected. Return to registry if you need another battle.",
        isInteractive: true,
      };
    }

    if (!hasBattle) {
      return {
        ...capability,
        wizardStatus: "locked",
        wizardReason: "Select a battle first.",
        isInteractive: false,
      };
    }

    if (capability.status === "planned" || capability.status === "disabled") {
      return {
        ...capability,
        wizardStatus: "locked",
        wizardReason: "This capability is not implemented yet in the current build.",
        isInteractive: false,
      };
    }

    if (capability.id === "c3") {
      if (state.c3SelectedPatternIds.length > 0) {
        return {
          ...capability,
          wizardStatus: "completed",
          wizardReason: "Pattern selection is saved.",
          isInteractive: true,
        };
      }
      return {
        ...capability,
        wizardStatus: state.activeCapabilityId === "c3" ? "in_progress" : "available",
        wizardReason: "Review pattern library and pick seed architectures.",
        isInteractive: true,
      };
    }

    if (capability.id === "c2") {
      if (state.c3SelectedPatternIds.length === 0) {
        return {
          ...capability,
          wizardStatus: "locked",
          wizardReason: "Select at least one pattern in C3 before candidate generation.",
          isInteractive: false,
        };
      }
      if (compileGateBlocked) {
        return {
          ...capability,
          wizardStatus: "blocked",
          wizardReason: "Candidate preparation failed. Fix C2 compile issues first.",
          isInteractive: false,
        };
      }
      if (hasSelectedCandidates) {
        return {
          ...capability,
          wizardStatus: "completed",
          wizardReason: "Candidates are selected for tests.",
          isInteractive: true,
        };
      }
      return {
        ...capability,
        wizardStatus: state.activeCapabilityId === "c2" ? "in_progress" : "available",
        wizardReason: hasCandidates ? "Candidate draft is ready. Select candidates for tests." : "Generate candidate draft from selected patterns.",
        isInteractive: true,
      };
    }

    if (capability.id === "c4") {
      if (!hasCandidates) {
        return {
          ...capability,
          wizardStatus: "locked",
          wizardReason: "Generate candidates in C2 before dataset setup.",
          isInteractive: false,
        };
      }
      if (hasAssignedDatasets) {
        return {
          ...capability,
          wizardStatus: "completed",
          wizardReason: "Datasets are assigned for arena tests.",
          isInteractive: true,
        };
      }
      return {
        ...capability,
        wizardStatus: state.activeCapabilityId === "c4" ? "in_progress" : "available",
        wizardReason: "Configure dataset assignment.",
        isInteractive: true,
      };
    }

    if (capability.id === "c5") {
      if (!hasSelectedCandidates) {
        return {
          ...capability,
          wizardStatus: "locked",
          wizardReason: "Select candidates for tests in C2 first.",
          isInteractive: false,
        };
      }
      if (hasEnabledComparativeMetrics) {
        return {
          ...capability,
          wizardStatus: "completed",
          wizardReason: "Comparative metrics are configured.",
          isInteractive: true,
        };
      }
      return {
        ...capability,
        wizardStatus: state.activeCapabilityId === "c5" ? "in_progress" : "available",
        wizardReason: "Configure comparative and diagnostic metrics.",
        isInteractive: true,
      };
    }

    if (capability.id === "c5s") {
      if (!hasEnabledComparativeMetrics) {
        return {
          ...capability,
          wizardStatus: "locked",
          wizardReason: "Configure metrics in C5 first.",
          isInteractive: false,
        };
      }
      if (!stageMappingRequired) {
        return {
          ...capability,
          wizardStatus: "completed",
          wizardReason: "No non-final diagnostics enabled. Stage mapping is optional.",
          isInteractive: true,
        };
      }
      if (hasReadyStageMappingCoverage) {
        return {
          ...capability,
          wizardStatus: "completed",
          wizardReason: "Stage mapping coverage is ready for enabled non-final diagnostics.",
          isInteractive: true,
        };
      }
      return {
        ...capability,
        wizardStatus: state.activeCapabilityId === "c5s" ? "in_progress" : "blocked",
        wizardReason: "Complete stage mapping coverage before opening Evaluators.",
        isInteractive: true,
      };
    }

    if (capability.id === "c6") {
      if (!hasEnabledComparativeMetrics) {
        return {
          ...capability,
          wizardStatus: "locked",
          wizardReason: "Configure metrics in C5 first.",
          isInteractive: false,
        };
      }
      if (stageMappingRequired && !hasReadyStageMappingCoverage) {
        return {
          ...capability,
          wizardStatus: "locked",
          wizardReason: "Complete Stage Mapping step first.",
          isInteractive: false,
        };
      }
      if (hasEnabledEvaluators) {
        return {
          ...capability,
          wizardStatus: "completed",
          wizardReason: "Evaluators are configured.",
          isInteractive: true,
        };
      }
      return {
        ...capability,
        wizardStatus: state.activeCapabilityId === "c6" ? "in_progress" : "available",
        wizardReason: "Configure evaluator adapters and matrix coverage.",
        isInteractive: true,
      };
    }

    if (capability.id === "c7") {
      if (!hasAssignedDatasets || !hasEnabledComparativeMetrics || !hasEnabledEvaluators || (stageMappingRequired && !hasReadyStageMappingCoverage)) {
        return {
          ...capability,
          wizardStatus: "locked",
          wizardReason: "Complete C4/C5/Stage Mapping/C6 setup before optimizer launch.",
          isInteractive: false,
        };
      }
      if (optimizerPreflightBlocked) {
        return {
          ...capability,
          wizardStatus: "blocked",
          wizardReason: "Optimizer preflight is invalid. Fix issues before launch.",
          isInteractive: false,
        };
      }
      if (hasOptimizerRuns) {
        return {
          ...capability,
          wizardStatus: "completed",
          wizardReason: "Optimizer run history is available.",
          isInteractive: true,
        };
      }
      return {
        ...capability,
        wizardStatus: state.activeCapabilityId === "c7" ? "in_progress" : "available",
        wizardReason: "Validate optimizer setup and launch benchmark run.",
        isInteractive: true,
      };
    }

    if (capability.id === "c8") {
      if (!hasOptimizerRuns) {
        return {
          ...capability,
          wizardStatus: "locked",
          wizardReason: "Run optimizer in C7 before opening reports/champion export.",
          isInteractive: false,
        };
      }
      return {
        ...capability,
        wizardStatus: state.activeCapabilityId === "c8" ? "in_progress" : "available",
        wizardReason: "Review report and export champion artifacts.",
        isInteractive: true,
      };
    }

    return {
      ...capability,
      wizardStatus: "available",
      wizardReason: "Capability is available.",
      isInteractive: true,
    };
  });
}

// Русский комментарий: проверяет, доступен ли metric/signal для текущей структуры кандидатов.
function isAvailabilityEnabled(availabilityStatus: string | undefined): boolean {
  return availabilityStatus !== "unavailable";
}

// Русский комментарий: строит читабельные requirement chips для карточки evaluator adapter.
function buildEvaluatorRequirementLabels(evaluator: C4Evaluator): string[] {
  const labels: string[] = [];
  if (evaluator.requires_dataset) {
    labels.push("dataset");
  }
  if (evaluator.requires_llm) {
    labels.push("llm");
  }
  if (evaluator.requires_stage_mapping) {
    labels.push("stage mapping");
  }
  if (labels.length === 0) {
    labels.push("no extra requirements");
  }
  if (evaluator.budget_cost_model) {
    labels.push(`budget: ${evaluator.budget_cost_model}`);
  }
  return labels;
}

// Русский комментарий: вычисляет compatibility fallback для UI, если backend link еще не пришел.
function resolveEvaluatorMetricCompatibility(
  evaluator: C4Evaluator | undefined,
  metricKind: "comparative" | "diagnostic" | string,
  metricId: string,
  link?: C4EvaluatorMetricLink,
): { status: "compatible" | "incompatible"; reason: string } {
  if (link?.compatibility_status === "incompatible") {
    return { status: "incompatible", reason: link.compatibility_reason ?? "This evaluator cannot evaluate this metric." };
  }
  if (link?.compatibility_status === "compatible") {
    return { status: "compatible", reason: "" };
  }
  const supportedMetricRefs = evaluator?.supported_metric_refs ?? [];
  if (supportedMetricRefs.length === 0) {
    return { status: "compatible", reason: "" };
  }
  const metricRef = `${String(metricKind).toLowerCase()}:${metricId}`.toLowerCase();
  if (!supportedMetricRefs.map((item) => item.toLowerCase()).includes(metricRef)) {
    return {
      status: "incompatible",
      reason: `${evaluator?.title ?? "Evaluator"} does not support ${metricRef}.`,
    };
  }
  return { status: "compatible", reason: "" };
}

// Русский комментарий: строит компактную строку фичей для панели Metrics.
function formatCandidateFeatureSummary(featureFlags: Record<string, boolean>): string {
  const labels: Array<[string, string]> = [
    ["llm", "LLM"],
    ["retrieval", "Retrieval"],
    ["rerank", "Rerank"],
    ["tool", "Tool"],
    ["hitl", "HITL"],
  ];
  const present = labels.filter(([key]) => Boolean(featureFlags[key])).map(([, label]) => label);
  return present.length > 0 ? present.join(", ") : "No candidate features detected yet";
}

// Русский комментарий: маппит diagnostic signal id к non-final target stage для wizard-gating.
function mapDiagnosticSignalToStage(signalId: string): "retrieval" | "rerank" | "synthesis" | null {
  if (signalId === "retrieval_coverage") {
    return "retrieval";
  }
  if (signalId === "rerank_gain") {
    return "rerank";
  }
  if (
    signalId === "synthesis_drift" ||
    signalId === "pattern_cleanup_effectiveness" ||
    signalId === "proof_context_preservation" ||
    signalId === "over_sanitization_risk"
  ) {
    return "synthesis";
  }
  return null;
}

// Русский комментарий: выбирает применимые proposal items по умолчанию, но не применяет их без Apply.
function buildDefaultMetricProposalSelection(proposal: C4MetricProposal | null): string[] {
  if (!proposal) {
    return [];
  }
  return proposal.items
    .filter((item) => item.selected && item.compatibility_status !== "review_only")
    .map((item) => item.proposal_item_id);
}

// Русский комментарий: гарантирует присутствие Stage Mapping шага в capability-меню даже при старом backend-каталоге.
function ensureStageMappingCapability(capabilities: Capability[]): Capability[] {
  const hasStageMapping = capabilities.some((item) => item.id === "c5s");
  if (hasStageMapping) {
    return capabilities;
  }
  const metricsIndex = capabilities.findIndex((item) => item.id === "c5");
  const stageMappingCapability: Capability = {
    id: "c5s",
    name: "Stage Mapping",
    description: "Map target stages to candidate runtime nodes.",
    status: "enabled",
    badge_count: 1,
  };
  if (metricsIndex < 0) {
    return [...capabilities, stageMappingCapability];
  }
  return [
    ...capabilities.slice(0, metricsIndex + 1),
    stageMappingCapability,
    ...capabilities.slice(metricsIndex + 1),
  ];
}

// Русский комментарий: нормализует stage-id dataset строки для editor/API payload.
function normalizeDatasetTargetStage(rawValue: unknown): C4DatasetTargetStage {
  const stage = String(rawValue ?? "final").trim().toLowerCase();
  if (stage === "retrieval" || stage === "rerank" || stage === "synthesis" || stage === "final") {
    return stage;
  }
  return "final";
}

// Русский комментарий: преобразует expected/expected_payload в stage-aware объект перед сохранением.
function normalizeExpectedPayloadFromEditorInput(args: {
  targetStage: C4DatasetTargetStage;
  expected: unknown;
  expectedPayload: unknown;
}): Record<string, unknown> {
  const { targetStage, expected, expectedPayload } = args;
  const base = typeof expectedPayload === "object" && expectedPayload && !Array.isArray(expectedPayload)
    ? { ...(expectedPayload as Record<string, unknown>) }
    : {};
  const expectedText = String(expected ?? "").trim();
  if (expectedText) {
    try {
      const parsed = JSON.parse(expectedText) as unknown;
      if (typeof parsed === "object" && parsed && !Array.isArray(parsed)) {
        Object.assign(base, parsed as Record<string, unknown>);
      } else if (targetStage === "final") {
        base.answer = expectedText;
      } else {
        base.text = expectedText;
      }
    } catch {
      if (targetStage === "final") {
        base.answer = expectedText;
      } else {
        base.text = expectedText;
      }
    }
  }
  if (targetStage === "retrieval") {
    base.evidence_ids = Array.isArray(base.evidence_ids) ? base.evidence_ids : [];
    base.must_include = Array.isArray(base.must_include) ? base.must_include : [];
  } else if (targetStage === "rerank") {
    base.ranked_ids = Array.isArray(base.ranked_ids) ? base.ranked_ids : [];
  } else if (targetStage === "synthesis") {
    base.must_include = Array.isArray(base.must_include) ? base.must_include : [];
    base.forbidden = Array.isArray(base.forbidden) ? base.forbidden : [];
  } else {
    base.answer = String(base.answer ?? base.final_answer ?? base.text ?? "").trim();
  }
  return base;
}

// Русский комментарий: готовит ожидаемый результат для строкового поля expected в editor-таблице.
function stringifyExpectedPayloadForEditor(targetStage: C4DatasetTargetStage, payload: Record<string, unknown>): string {
  if (targetStage === "final") {
    return String(payload.answer ?? "").trim();
  }
  try {
    return JSON.stringify(payload, null, 0);
  } catch {
    return "";
  }
}

// Русский комментарий: определяет экран по текущему URL.
function parseRoute(pathname: string): ScreenRoute {
  const battleMatch = pathname.match(/^\/battles\/([^/]+)\/?$/);
  if (battleMatch && battleMatch[1]) {
    return { name: "battle_workspace", arenaId: decodeURIComponent(battleMatch[1]) };
  }
  return { name: "battles_hub" };
}

// Русский комментарий: стабильный hash для генерации демонстрационных чисел в карточках.
function hashString(value: string): number {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 31 + value.charCodeAt(index)) >>> 0;
  }
  return hash;
}
