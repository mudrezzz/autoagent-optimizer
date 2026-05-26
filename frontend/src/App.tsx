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
  searchArenaPatterns,
  selectArenaDataset,
  selectArenaCandidatesForTests,
  validateArenaDataset,
} from "./api";
import type {
  ArenaRecord,
  C2CandidateDraftItem,
  C2CandidateSetDraft,
  C2ChatMessage,
  C4DatasetDetail,
  C4DatasetSummary,
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
  {
    id: "c2",
    name: "Task Chat + Candidates",
    description: "Chat-driven task brief and candidate draft generation.",
    status: "enabled",
    badge_count: 1,
  },
  { id: "c3", name: "Pattern Library + RAG", description: "Pattern retrieval controls for candidate generation.", status: "enabled", badge_count: 1 },
  { id: "c4", name: "Dataset & Metrics Studio", description: "Manage dataset lifecycle for benchmark runs.", status: "enabled", badge_count: 1 },
  { id: "c5", name: "Optimizer Run Monitor", description: "Planned slice for run timeline and metrics monitor.", status: "planned", badge_count: 0 },
  { id: "c6", name: "Report + Champion Export/Import", description: "Planned slice for reports and native loop.", status: "planned", badge_count: 0 },
];

// Русский комментарий: иконки capability для меню рабочего экрана battle.
const CAPABILITY_ICONS: Record<string, string> = {
  c1: "swords",
  c2: "messages-square",
  c3: "library",
  c4: "database",
  c5: "activity",
  c6: "package-check",
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
  c2CandidateSetDraft: C2CandidateSetDraft | null;
  c2SelectedCandidateId: string;
  c2SelectedForTestsIds: string[];
  c2ExpandedCandidateId: string;
  c2JsonCollapsed: boolean;
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
  c4ViewMode: "list" | "edit";
  c4EditorDatasetId: string;
  c4EditorRows: Array<{ case_id: string; input: string; expected: string; notes: string }>;
  c4EditorImportJsonl: string;
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

// Русский комментарий: корневой компонент frontend shell.
export function App(): JSX.Element {
  const [route, setRoute] = useState<ScreenRoute>(() => parseRoute(window.location.pathname));
  const [state, setState] = useState<UiState>({
    capabilities: FALLBACK_CAPABILITIES,
    activeCapabilityId: "c2",
    arenas: [],
    activeArenaId: "",
    c2ChatInput: "",
    c2Messages: [],
    c2CandidateSetDraft: null,
    c2SelectedCandidateId: "",
    c2SelectedForTestsIds: [],
    c2ExpandedCandidateId: "",
    c2JsonCollapsed: true,
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
    c4ViewMode: "list",
    c4EditorDatasetId: "",
    c4EditorRows: [],
    c4EditorImportJsonl: "",
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

  // Русский комментарий: загрузка capability-каталога.
  useEffect(() => {
    void (async () => {
      try {
        const catalog = await fetchCapabilityCatalog();
        setState((prev) => ({ ...prev, capabilities: catalog.capabilities }));
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

  // Русский комментарий: переход на hub.
  function navigateToBattlesHub(): void {
    window.history.pushState({}, "", "/battles");
    setRoute({ name: "battles_hub" });
    setState((prev) => ({
      ...prev,
      activeArenaId: "",
      c2ChatInput: "",
      c2Messages: [],
      c2CandidateSetDraft: null,
      c2SelectedCandidateId: "",
      c2SelectedForTestsIds: [],
      c2ExpandedCandidateId: "",
      c2JsonCollapsed: true,
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
      c4ViewMode: "list",
      c4EditorDatasetId: "",
      c4EditorRows: [],
      c4EditorImportJsonl: "",
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
    } catch (error) {
      setState((prev) => ({
        ...prev,
        c2Messages: [],
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
        c4ViewMode: "list",
        c4EditorDatasetId: "",
        c4EditorRows: [],
        c4EditorImportJsonl: "",
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
  function handleUpdateC4EditorRowField(rowIndex: number, field: "case_id" | "input" | "expected" | "notes", value: string): void {
    setState((prev) => ({
      ...prev,
      c4EditorRows: prev.c4EditorRows.map((row, index) => (index === rowIndex ? { ...row, [field]: value } : row)),
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
    const parsedRows: Array<{ case_id: string; input: string; expected: string; notes: string }> = [];
    try {
      for (const line of lines) {
        const parsed = JSON.parse(line) as Record<string, unknown>;
        parsedRows.push({
          case_id: String(parsed.case_id ?? ""),
          input: String(parsed.input ?? parsed.query ?? ""),
          expected: String(parsed.expected ?? parsed.answer ?? ""),
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
      const response = await replaceArenaDatasetRows(state.activeArenaId, state.c4EditorDatasetId, state.c4EditorRows);
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

  // Русский комментарий: переключение capability в workspace.
  async function handleSwitchCapability(capabilityId: string): Promise<void> {
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
        setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "Select battle first, then use C4 dataset studio." }) }));
        return;
      }
      try {
        await loadC4DatasetState(state.activeArenaId, true);
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

  // Русский комментарий: отправка сообщения в C2 чат.
  async function handleSendC2Message(generateCandidates: boolean): Promise<void> {
    const arenaId = state.activeArenaId;
    if (!arenaId) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "Open battle before using C2 chat." }) }));
      return;
    }
    if (state.activeCapabilityId !== "c2") {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "Switch to C2 before sending chat messages." }) }));
      return;
    }
    const message = state.c2ChatInput.trim();
    if (!message) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "error", message: "C2 brief message is required." }) }));
      return;
    }

    setState((prev) => ({ ...prev, budgetStage: generateCandidates ? "generating candidates" : "sending message", budgetPercent: 60 }));
    try {
      const response = await postArenaChatMessage(arenaId, message, { generateCandidates, maxCandidates: 3 });
      const snapshot = {
        status: "success",
        capability_id: "c2",
        action: generateCandidates ? "generate_candidates" : "append_message",
        arena_id: arenaId,
        messages_total: response.messages_total,
        candidate_set_id: response.candidate_set_draft?.candidate_set_id ?? null,
      };
      setState((prev) => ({
        // Русский комментарий: сохраняем выбранного кандидата, если он остался в новом draft, иначе выбираем первый.
        ...prev,
        ...(() => {
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
        budgetStage: "c2 updated",
        budgetPercent: 100,
        jsonText: prettyJson(snapshot),
        lastPayload: snapshot,
      }));
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

  // Русский комментарий: сворачивает/разворачивает JSON-панель workspace, чтобы освободить место под список кандидатов.
  function handleToggleWorkspaceJson(): void {
    setState((prev) => ({ ...prev, c2JsonCollapsed: !prev.c2JsonCollapsed }));
  }

  // Русский комментарий: отправляет C2-сообщение по Enter, сохраняя перенос строки через Shift+Enter.
  function handleC2ChatKeyDown(event: ReactKeyboardEvent<HTMLTextAreaElement>): void {
    if (event.key !== "Enter" || event.shiftKey) {
      return;
    }
    event.preventDefault();
    void handleSendC2Message(true);
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
            ? state.capabilities.map((capability) => {
                const statusClass = capability.status === "enabled" ? "enabled" : "planned";
                const icon = CAPABILITY_ICONS[capability.id] ?? "dot";
                return (
                  <button
                    key={capability.id}
                    type="button"
                    className={`cap-link${state.activeCapabilityId === capability.id ? " active" : ""}${capability.status === "planned" ? " disabled" : ""}`}
                    onClick={() => {
                      void handleSwitchCapability(capability.id);
                    }}
                  >
                    <i data-lucide={icon} className="cap-icon" />
                    <span className="cap-name">{capability.name}</span>
                    <span className={`cap-badge ${statusClass}`}>{capability.status}</span>
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
                      <section className={`workspace-json-panel${state.c2JsonCollapsed ? " is-collapsed" : ""}`}>
                        <button
                          type="button"
                          className="workspace-json-toggle"
                          onClick={handleToggleWorkspaceJson}
                          aria-expanded={!state.c2JsonCollapsed}
                          aria-controls="workspace-json-panel-body"
                        >
                          <span>Runtime snapshot</span>
                          <i data-lucide={state.c2JsonCollapsed ? "chevron-down" : "chevron-up"} />
                        </button>
                        {!state.c2JsonCollapsed ? (
                          <pre id="workspace-json-panel-body" className="json-view json-view--workspace">{state.jsonText}</pre>
                        ) : null}
                      </section>
                    </div>
                  </section>
                ) : activeCapability.id === "c4" ? (
                  <section className="trace-view trace-view--workspace">
                    <header className="tv-head">
                      <div className="tv-title">
                        <i data-lucide="database" />
                        <span>Dataset studio</span>
                        <span className="tv-arch">{state.c4Datasets.length} datasets</span>
                      </div>
                    </header>
                    <div className="tv-body tv-body--workspace">
                      <section className="c4-panel">
                        {state.c4ViewMode === "list" ? (
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
                                    <th>expected</th>
                                    <th>notes</th>
                                    <th />
                                  </tr>
                                </thead>
                                <tbody>
                                  {state.c4EditorRows.length === 0 ? (
                                    <tr>
                                      <td colSpan={5}>No rows yet.</td>
                                    </tr>
                                  ) : state.c4EditorRows.map((row, rowIndex) => (
                                    <tr key={`${state.c4EditorDatasetId}:${rowIndex}`}>
                                      <td><input value={row.case_id} onChange={(event) => { handleUpdateC4EditorRowField(rowIndex, "case_id", event.target.value); }} /></td>
                                      <td><input value={row.input} onChange={(event) => { handleUpdateC4EditorRowField(rowIndex, "input", event.target.value); }} /></td>
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
                                placeholder='JSONL import, one row per line: {"case_id":"case_1","input":"...","expected":"...","notes":"..."}'
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
                        )}
                      </section>
                      <section className={`workspace-json-panel${state.c2JsonCollapsed ? " is-collapsed" : ""}`}>
                        <button
                          type="button"
                          className="workspace-json-toggle"
                          onClick={handleToggleWorkspaceJson}
                          aria-expanded={!state.c2JsonCollapsed}
                          aria-controls="workspace-json-panel-body"
                        >
                          <span>Runtime snapshot</span>
                          <i data-lucide={state.c2JsonCollapsed ? "chevron-down" : "chevron-up"} />
                        </button>
                        {!state.c2JsonCollapsed ? (
                          <pre id="workspace-json-panel-body" className="json-view json-view--workspace">{state.jsonText}</pre>
                        ) : null}
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
                              disabled={!isC2Enabled || !state.activeArenaId || !state.c2CandidateSetDraft}
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
                          {isC2Enabled && state.c2CandidateSetDraft ? state.c2CandidateSetDraft.candidates.map((candidate, index) => {
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
                          }) : <div className="issue-row warning">No candidate draft yet. Use chat action "Generate candidates".</div>}
                        </div>
                      </div>
                      <section className={`workspace-json-panel${state.c2JsonCollapsed ? " is-collapsed" : ""}`}>
                        <button
                          type="button"
                          className="workspace-json-toggle"
                          onClick={handleToggleWorkspaceJson}
                          aria-expanded={!state.c2JsonCollapsed}
                          aria-controls="workspace-json-panel-body"
                        >
                          <span>Runtime snapshot</span>
                          <i data-lucide={state.c2JsonCollapsed ? "chevron-down" : "chevron-up"} />
                        </button>
                        {!state.c2JsonCollapsed ? (
                          <pre id="workspace-json-panel-body" className="json-view json-view--workspace">{state.jsonText}</pre>
                        ) : null}
                      </section>
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
                  <textarea
                    id="c2-chat-input"
                    value={state.c2ChatInput}
                    onChange={(event) => {
                      handleC2ChatInputChange(event.target.value);
                    }}
                    onKeyDown={handleC2ChatKeyDown}
                    placeholder="Describe the optimization task in plain language..."
                    disabled={!state.activeArenaId || !isC2Enabled}
                  />
                  <div className="c2-chat-actions">
                    <button
                      type="button"
                      className="tb-btn tb-btn-ghost"
                      onClick={() => {
                        void handleSendC2Message(false);
                      }}
                      disabled={!state.activeArenaId || !isC2Enabled}
                    >
                      Send
                    </button>
                    <button
                      type="button"
                      className="tb-btn tb-btn-primary"
                      onClick={() => {
                        void handleSendC2Message(true);
                      }}
                      disabled={!state.activeArenaId || !isC2Enabled}
                    >
                      Generate
                    </button>
                  </div>
                </div>
              </section>

            </aside>
          ) : null}
        </div>
      </div>

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
