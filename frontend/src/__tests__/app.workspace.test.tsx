import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../App";
import type { ArenaRecord, C2CandidateSetDraft, Capability } from "../types";

// Русский комментарий: мокируем API-слой, чтобы UI-тесты были детерминированными и не зависели от backend-сервера.
vi.mock("../api", () => ({
  assignArenaDatasets: vi.fn(),
  createArenaDataset: vi.fn(),
  createArena: vi.fn(),
  deleteArena: vi.fn(),
  fetchArenaDatasetState: vi.fn(),
  fetchArenaEvaluationState: vi.fn(),
  fetchArenaOptimizerState: vi.fn(),
  duplicateArena: vi.fn(),
  fetchCapabilityCatalog: vi.fn(),
  fetchArenaPatternSelection: vi.fn(),
  fetchStubCapability: vi.fn(),
  getArena: vi.fn(),
  getArenaChatState: vi.fn(),
  listArenas: vi.fn(),
  postArenaChatMessage: vi.fn(),
  replaceArenaDatasetRows: vi.fn(),
  renameArena: vi.fn(),
  saveArenaEvaluationBudget: vi.fn(),
  saveArenaEvaluationEvaluators: vi.fn(),
  saveArenaEvaluationMatrix: vi.fn(),
  saveArenaEvaluationStageMappings: vi.fn(),
  autoMapArenaEvaluationStageMappings: vi.fn(),
  saveArenaEvaluationStageBindings: vi.fn(),
  suggestArenaEvaluationStageBindings: vi.fn(),
  saveArenaEvaluationMetrics: vi.fn(),
  saveArenaEvaluationVersion: vi.fn(),
  saveArenaOptimizerSetup: vi.fn(),
  saveArenaOptimizerVersion: vi.fn(),
  saveArenaPatternSelection: vi.fn(),
  saveArenaDatasetVersion: vi.fn(),
  searchArenaPatterns: vi.fn(),
  selectArenaDataset: vi.fn(),
  selectArenaCandidatesForTests: vi.fn(),
  launchArenaOptimizer: vi.fn(),
  validateArenaDataset: vi.fn(),
  validateArenaEvaluationProfile: vi.fn(),
  validateArenaOptimizerSetup: vi.fn(),
}));

import {
  assignArenaDatasets,
  createArenaDataset,
  createArena,
  deleteArena,
  fetchArenaDatasetState,
  fetchArenaEvaluationState,
  fetchArenaOptimizerState,
  duplicateArena,
  fetchCapabilityCatalog,
  fetchArenaPatternSelection,
  fetchStubCapability,
  getArena,
  getArenaChatState,
  listArenas,
  postArenaChatMessage,
  replaceArenaDatasetRows,
  renameArena,
  saveArenaEvaluationBudget,
  saveArenaEvaluationEvaluators,
  saveArenaEvaluationMatrix,
  saveArenaEvaluationStageMappings,
  autoMapArenaEvaluationStageMappings,
  saveArenaEvaluationStageBindings,
  suggestArenaEvaluationStageBindings,
  saveArenaEvaluationMetrics,
  saveArenaEvaluationVersion,
  saveArenaOptimizerSetup,
  saveArenaOptimizerVersion,
  saveArenaPatternSelection,
  saveArenaDatasetVersion,
  searchArenaPatterns,
  selectArenaDataset,
  selectArenaCandidatesForTests,
  launchArenaOptimizer,
  validateArenaDataset,
  validateArenaEvaluationProfile,
  validateArenaOptimizerSetup,
} from "../api";

// Русский комментарий: фикстура battle-арены для режима workspace.
const ARENA: ArenaRecord = {
  workspace_id: "ws_demo_1",
  name: "test1 copy",
  description: "test",
  created_at: "2026-05-23T11:02:18+00:00",
  tenant_id: "tenant_demo_1",
  owner_user_id: "user_demo_1",
};

// Русский комментарий: фикстура capability-каталога, где C2 активен и доступен.
const CAPABILITIES: Capability[] = [
  { id: "c1", name: "Battle Registry", description: "Manage battle arenas.", status: "enabled", badge_count: 1 },
  { id: "c3", name: "Pattern Library + RAG", description: "Pattern retrieval", status: "enabled", badge_count: 1 },
  { id: "c2", name: "Task Chat + Candidates", description: "Generate candidates from chat.", status: "enabled", badge_count: 1 },
  { id: "c4", name: "Datasets", description: "Dataset controls", status: "enabled", badge_count: 1 },
  { id: "c5", name: "Metrics", description: "Metrics controls", status: "enabled", badge_count: 1 },
  { id: "c6", name: "Evaluators", description: "Evaluators controls", status: "enabled", badge_count: 1 },
  { id: "c7", name: "Optimizer Run Monitor", description: "Optimizer setup", status: "enabled", badge_count: 1 },
  { id: "c8", name: "Report + Champion Export/Import", description: "planned", status: "planned", badge_count: 0 },
];

// Русский комментарий: фикстура набора кандидатов для проверки рендера, фокуса и accordion-деталей.
const CANDIDATE_SET: C2CandidateSetDraft = {
  candidate_set_id: "cset_de5694fa",
  source: "mock",
  task_brief: "rewrite post",
  generation_mode: "chat",
  arena_id: ARENA.workspace_id,
  total: 3,
  candidates: [
    {
      candidate_id: "cand_direct",
      title: "Direct LLM Rewriter",
      pattern_ref: "style.direct_llm",
      summary: "Single-agent rewrite path with compact prompt and deterministic post-check.",
      rationale: "fast",
      dsl_stub_ref: "stub://direct",
      estimated_complexity: "low",
      logo: { key: "direct", label: "DL" },
      config_summary: { roles_total: 1, llm_calls_max: 1, deterministic_guards: 1, hitl_checkpoints: 0 },
      architecture_steps: ["accept_input", "rewrite_llm", "style_guard", "return_output"],
      mini_graph: {
        nodes: [
          { id: "accept_input", label: "input", kind: "input" },
          { id: "rewrite_llm", label: "llm.rewrite", kind: "llm" },
          { id: "style_guard", label: "style.guard", kind: "validator" },
          { id: "return_output", label: "output", kind: "output" },
        ],
        edges: [
          { source: "accept_input", target: "rewrite_llm" },
          { source: "rewrite_llm", target: "style_guard" },
          { source: "style_guard", target: "return_output" },
        ],
      },
    },
    {
      candidate_id: "cand_cleaner",
      title: "Pattern Cleaner",
      pattern_ref: "style.pattern_cleaner",
      summary: "Two-step rewrite with anti-pattern cleanup pass before final output.",
      rationale: "balanced",
      dsl_stub_ref: "stub://cleaner",
      estimated_complexity: "medium",
      logo: { key: "cleaner", label: "PC" },
      config_summary: { roles_total: 2, llm_calls_max: 2, deterministic_guards: 1, hitl_checkpoints: 0 },
      architecture_steps: ["accept_input", "rewrite_draft", "cleanup_pass", "style_guard", "return_output"],
      mini_graph: {
        nodes: [
          { id: "accept_input", label: "input", kind: "input" },
          { id: "rewrite_draft", label: "llm.rewrite", kind: "llm" },
          { id: "cleanup_pass", label: "llm.cleanup", kind: "llm" },
          { id: "style_guard", label: "style.guard", kind: "validator" },
          { id: "return_output", label: "output", kind: "output" },
        ],
        edges: [
          { source: "accept_input", target: "rewrite_draft" },
          { source: "rewrite_draft", target: "cleanup_pass" },
          { source: "cleanup_pass", target: "style_guard" },
          { source: "style_guard", target: "return_output" },
        ],
      },
    },
    {
      candidate_id: "cand_hitl",
      title: "HITL Reviewer Gate",
      pattern_ref: "style.hitl_gate",
      summary: "Route borderline cases to reviewer with explicit guardrail policy.",
      rationale: "safe",
      dsl_stub_ref: "stub://hitl",
      estimated_complexity: "medium",
    },
  ],
};

// Русский комментарий: helper поднимает UI сразу в battle-workspace роуте.
function renderWorkspace(): void {
  window.history.pushState({}, "", `/battles/${ARENA.workspace_id}`);
  render(<App />);
}

describe("Battle workspace candidates", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(fetchCapabilityCatalog).mockResolvedValue({
      version: "v1",
      capabilities: CAPABILITIES,
    });
    vi.mocked(listArenas).mockResolvedValue({
      status: "success",
      arenas: [ARENA],
      total: 1,
    });
    vi.mocked(getArena).mockResolvedValue({
      status: "success",
      arena: ARENA,
    });
    vi.mocked(getArenaChatState).mockResolvedValue({
      status: "success",
      capability_id: "c2",
      arena_id: ARENA.workspace_id,
      arena_name: ARENA.name,
      messages: [],
      messages_total: 0,
      candidate_set_draft: CANDIDATE_SET,
    });
    vi.mocked(fetchArenaPatternSelection).mockResolvedValue({
      status: "success",
      capability_id: "c3",
      arena_id: ARENA.workspace_id,
      selection: {
        include_pattern_ids: [],
        exclude_pattern_ids: [],
        updated_at: "2026-05-24T00:00:00+00:00",
      },
    });
    vi.mocked(searchArenaPatterns).mockResolvedValue({
      status: "success",
      capability_id: "c3",
      arena_id: ARENA.workspace_id,
      query: "",
      query_tokens: [],
      total_candidates: 2,
      returned: 2,
      selection: {
        include_pattern_ids: [],
        exclude_pattern_ids: [],
        updated_at: "2026-05-24T00:00:00+00:00",
      },
      patterns: [
        {
          pattern_id: "style.direct_llm",
          title: "Direct LLM Rewrite",
          summary: "Fast baseline.",
          tags: ["rewrite"],
          complexity: "low",
          relevance: 0.4,
          selection_state: "neutral",
          retrieval_trace: ["query:empty"],
          logo: { key: "direct", label: "DL" },
          config_summary: { roles_total: 1, llm_calls_max: 1, deterministic_guards: 1, hitl_checkpoints: 0 },
          agent_template: {
            nodes: [
              { id: "input", label: "input", kind: "input" },
              { id: "rewrite", label: "llm.rewrite", kind: "llm" },
              { id: "guard", label: "style.guard", kind: "validator" },
              { id: "output", label: "output", kind: "output" },
            ],
            edges: [
              { source: "input", target: "rewrite" },
              { source: "rewrite", target: "guard" },
              { source: "guard", target: "output" },
            ],
            rationale_steps: ["accept_input", "rewrite_llm", "style_guard", "return_output"],
          },
        },
        {
          pattern_id: "style.pattern_cleaner",
          title: "Pattern Cleaner",
          summary: "Cleanup pass.",
          tags: ["cleanup"],
          complexity: "medium",
          relevance: 0.33,
          selection_state: "neutral",
          retrieval_trace: ["query:empty"],
          logo: { key: "cleaner", label: "PC" },
          config_summary: { roles_total: 2, llm_calls_max: 2, deterministic_guards: 1, hitl_checkpoints: 0 },
          agent_template: {
            nodes: [
              { id: "input", label: "input", kind: "input" },
              { id: "draft", label: "llm.rewrite", kind: "llm" },
              { id: "cleanup", label: "llm.cleanup", kind: "llm" },
              { id: "guard", label: "style.guard", kind: "validator" },
              { id: "output", label: "output", kind: "output" },
            ],
            edges: [
              { source: "input", target: "draft" },
              { source: "draft", target: "cleanup" },
              { source: "cleanup", target: "guard" },
              { source: "guard", target: "output" },
            ],
            rationale_steps: ["accept_input", "rewrite_draft", "cleanup_pass", "style_guard", "return_output"],
          },
        },
      ],
    });
    vi.mocked(fetchArenaDatasetState).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      active_dataset_id: "dset_demo_1",
      assigned_dataset_ids: [],
      datasets: [
        {
          dataset_id: "dset_demo_1",
          name: "LinkedIn Golden",
          description: "demo dataset",
          rows_total: 2,
          versions_total: 1,
          updated_at: "2026-05-26T00:00:00+00:00",
          last_version_id: "dsv_demo_1",
          preview_rows: [
            { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
            { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
          ],
        },
      ],
      active_dataset: {
        dataset_id: "dset_demo_1",
        name: "LinkedIn Golden",
        description: "demo dataset",
        rows_total: 2,
        versions_total: 1,
        updated_at: "2026-05-26T00:00:00+00:00",
        last_version_id: "dsv_demo_1",
        created_at: "2026-05-26T00:00:00+00:00",
        rows: [
          { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
          { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
        ],
        versions: [{ version_id: "dsv_demo_1", label: "v1", created_at: "2026-05-26T00:00:00+00:00", rows_total: 2, source: "manual" }],
      },
    });
    vi.mocked(saveArenaPatternSelection).mockResolvedValue({
      status: "success",
      capability_id: "c3",
      arena_id: ARENA.workspace_id,
      selection: {
        include_pattern_ids: ["style.direct_llm"],
        exclude_pattern_ids: [],
        updated_at: "2026-05-24T00:00:00+00:00",
      },
    });
    vi.mocked(fetchArenaEvaluationState).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      comparative_metrics: [
        { metric_id: "quality_f1", title: "Quality F1@K", description: "quality", enabled: true, weight: 0.6 },
        { metric_id: "cost_per_case", title: "Cost / case", description: "cost", enabled: true, weight: 0.2 },
      ],
      diagnostic_signals: [
        { signal_id: "retrieval_coverage", title: "Retrieval coverage", description: "retrieval", enabled: true },
      ],
      evaluators: [
        { evaluator_id: "golden_oracle", title: "Golden dataset oracle", description: "deterministic", enabled: true },
      ],
      evaluator_metric_links: [
        { evaluator_id: "golden_oracle", metric_kind: "comparative", metric_id: "quality_f1", enabled: true },
        { evaluator_id: "golden_oracle", metric_kind: "comparative", metric_id: "cost_per_case", enabled: true },
        { evaluator_id: "golden_oracle", metric_kind: "diagnostic", metric_id: "retrieval_coverage", enabled: true },
      ],
      budget: { max_cases: 20, max_llm_calls: 100, max_cost_usd: 5.0 },
      versions: [],
      updated_at: "2026-05-26T00:00:00+00:00",
    });
    vi.mocked(fetchArenaOptimizerState).mockResolvedValue({
      status: "success",
      capability_id: "c5",
      arena_id: ARENA.workspace_id,
      methods: [
        { method_id: "random_search", title: "Random search", description: "baseline", enabled: true },
        { method_id: "grid_search", title: "Grid search", description: "deterministic", enabled: false },
      ],
      controls: [
        { control_id: "tune_prompts", title: "Tune prompts", description: "prompt scope", enabled: true },
        { control_id: "tune_pattern_mix", title: "Tune pattern mix", description: "pattern scope", enabled: true },
      ],
      run_plan: { epochs_total: 3, candidates_per_epoch: 4, max_parallel_trials: 2, early_stop_patience: 1 },
      budget: { max_cases: 24, max_llm_calls: 200, max_cost_usd: 8, max_runtime_minutes: 30 },
      versions: [],
      launch_history: [],
      updated_at: "2026-05-26T00:00:00+00:00",
    });

    vi.mocked(postArenaChatMessage).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(selectArenaCandidatesForTests).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(createArenaDataset).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(assignArenaDatasets).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(selectArenaDataset).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(replaceArenaDatasetRows).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(validateArenaDataset).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaDatasetVersion).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaEvaluationMetrics).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaEvaluationEvaluators).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaEvaluationMatrix).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaEvaluationStageMappings).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(autoMapArenaEvaluationStageMappings).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaEvaluationBudget).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaEvaluationStageBindings).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(suggestArenaEvaluationStageBindings).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(validateArenaEvaluationProfile).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaEvaluationVersion).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaOptimizerSetup).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(validateArenaOptimizerSetup).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaOptimizerVersion).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(launchArenaOptimizer).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(createArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(renameArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(duplicateArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(deleteArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(fetchStubCapability).mockRejectedValue(new Error("not used in this test"));
  });

  it("renders candidates list and allows selecting candidate row", async () => {
    const user = userEvent.setup();
    renderWorkspace();
    await user.click(await screen.findByLabelText("select-style.direct_llm-for-generation"));
    await user.click(await screen.findByRole("button", { name: "Save" }));
    await user.click(await screen.findByRole("button", { name: /Task Chat \+ Candidates/i }));

    const firstCandidate = await screen.findByText("Direct LLM Rewriter");
    const secondCandidateButton = await screen.findByRole("button", { name: /Pattern Cleaner/i });

    expect(firstCandidate).toBeInTheDocument();
    expect(await screen.findByText("HITL Reviewer Gate")).toBeInTheDocument();

    await user.click(secondCandidateButton);
    expect(secondCandidateButton).toHaveClass("candidate-row--active");
  });

  it("collapses and expands workspace JSON panel", async () => {
    const user = userEvent.setup();
    renderWorkspace();

    const toggle = await screen.findByRole("button", { name: /Runtime snapshot/i });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByText(/"status": "success"/i)).not.toBeInTheDocument();

    await user.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");
    expect(await screen.findByText(/"status": "success"/i)).toBeInTheDocument();
  });

  it("expands candidate details accordion and renders mini graph", async () => {
    const user = userEvent.setup();
    renderWorkspace();
    await user.click(await screen.findByLabelText("select-style.direct_llm-for-generation"));
    await user.click(await screen.findByRole("button", { name: "Save" }));
    await user.click(await screen.findByRole("button", { name: /Task Chat \+ Candidates/i }));

    await waitFor(() => {
      expect(document.querySelectorAll(".candidate-details-toggle").length).toBeGreaterThan(0);
    });
    const detailsButtons = Array.from(document.querySelectorAll<HTMLButtonElement>(".candidate-details-toggle"));
    expect(detailsButtons[0]?.getAttribute("aria-expanded")).toBe("false");

    await user.click(detailsButtons[0]);
    await waitFor(() => {
      expect(detailsButtons[0]?.getAttribute("aria-expanded")).toBe("true");
    });
    expect(await screen.findByLabelText("candidate-mini-graph-svg")).toBeInTheDocument();
  });

  it("selects candidates for tests and triggers internal preparation", async () => {
    const user = userEvent.setup();
    vi.mocked(selectArenaCandidatesForTests).mockResolvedValue({
      status: "success",
      capability_id: "c2",
      action: "select_candidates_for_tests",
      arena_id: ARENA.workspace_id,
      assistant_message: null,
      messages: [],
      messages_total: 0,
      compile_gate: {
        status: "ready",
        compiled_candidates: 3,
        ready_candidates: 3,
        failed_candidates: 0,
        total_candidates: 3,
        processed_at: "2026-05-25T10:00:00+00:00",
      },
      candidate_set_draft: {
        ...CANDIDATE_SET,
        compile_gate: {
          status: "ready",
          compiled_candidates: 3,
          ready_candidates: 3,
          failed_candidates: 0,
          selected_candidates: 3,
          total_candidates: 3,
          processed_at: "2026-05-25T10:00:00+00:00",
          max_compile_attempts: 3,
        },
        candidates: CANDIDATE_SET.candidates.map((candidate) => ({
          ...candidate,
          selected_for_tests: true,
          compile_readiness: {
            status: "ready",
            dsl_file: candidate.dsl_stub_ref,
            compile_summary: {
              status: "success",
              source: candidate.dsl_stub_ref,
              node_mappings: 4,
              warnings: 0,
              errors: 0,
            },
            issues: [],
            graph_ir_summary: {
              available: true,
              entry_node: "input",
              nodes_total: 4,
              edges_total: 3,
              terminal_nodes: ["output"],
            },
            compiled_at: "2026-05-25T10:00:00+00:00",
            attempts_used: 1,
            user_visible_issue: false,
          },
        })),
      },
    });

    renderWorkspace();
    await user.click(await screen.findByLabelText("select-style.direct_llm-for-generation"));
    await user.click(await screen.findByRole("button", { name: "Save" }));
    await user.click(await screen.findByRole("button", { name: /Task Chat \+ Candidates/i }));
    const firstCheckbox = await screen.findByLabelText("select-cand_direct-for-tests");
    const secondCheckbox = await screen.findByLabelText("select-cand_cleaner-for-tests");
    await user.click(firstCheckbox);
    await user.click(secondCheckbox);

    const selectButton = await screen.findByRole("button", { name: /Select for tests/i });
    await user.click(selectButton);
    expect(vi.mocked(selectArenaCandidatesForTests)).toHaveBeenCalledWith(ARENA.workspace_id, ["cand_direct", "cand_cleaner"], 3);
    expect(await screen.findAllByText("selected for tests")).toHaveLength(3);
  });

  it("switches to C3 and renders pattern library search results", async () => {
    const user = userEvent.setup();
    renderWorkspace();

    const c3Button = await screen.findByRole("button", { name: /Pattern Library \+ RAG/i });
    await user.click(c3Button);

    expect(await screen.findByText("Pattern library + retrieval")).toBeInTheDocument();
    expect(await screen.findByText("Direct LLM Rewrite")).toBeInTheDocument();
    expect(await screen.findByText("Pattern Cleaner")).toBeInTheDocument();
  });

  it("locks C4 wizard step when candidate draft is not generated yet", async () => {
    vi.mocked(getArenaChatState).mockResolvedValue({
      status: "success",
      capability_id: "c2",
      arena_id: ARENA.workspace_id,
      arena_name: ARENA.name,
      messages: [],
      messages_total: 0,
      candidate_set_draft: null,
    });

    renderWorkspace();
    const c4Button = await screen.findByRole("button", { name: /Datasets/i });
    expect(c4Button).toBeDisabled();
    expect(c4Button).toHaveAttribute("title", expect.stringContaining("Generate candidates in C2"));
  });

  it("uses C3 single checkbox selection and saves by explicit action", async () => {
    const user = userEvent.setup();
    vi.mocked(saveArenaPatternSelection).mockResolvedValue({
      status: "success",
      capability_id: "c3",
      arena_id: ARENA.workspace_id,
      selection: {
        include_pattern_ids: ["style.direct_llm"],
        exclude_pattern_ids: [],
        updated_at: "2026-05-26T00:00:00+00:00",
      },
    });
    vi.mocked(searchArenaPatterns).mockResolvedValue({
      status: "success",
      capability_id: "c3",
      arena_id: ARENA.workspace_id,
      query: "",
      query_tokens: [],
      total_candidates: 2,
      returned: 2,
      selection: {
        include_pattern_ids: ["style.direct_llm"],
        exclude_pattern_ids: [],
        updated_at: "2026-05-26T00:00:00+00:00",
      },
      patterns: [
        {
          pattern_id: "style.direct_llm",
          title: "Direct LLM Rewrite",
          summary: "Fast baseline.",
          tags: ["rewrite"],
          complexity: "low",
          relevance: 0.4,
          selection_state: "include",
          retrieval_trace: ["query:empty"],
          logo: { key: "direct", label: "DL" },
          config_summary: { roles_total: 1, llm_calls_max: 1, deterministic_guards: 1, hitl_checkpoints: 0 },
          agent_template: {
            nodes: [
              { id: "input", label: "input", kind: "input" },
              { id: "rewrite", label: "llm.rewrite", kind: "llm" },
              { id: "guard", label: "style.guard", kind: "validator" },
              { id: "output", label: "output", kind: "output" },
            ],
            edges: [
              { source: "input", target: "rewrite" },
              { source: "rewrite", target: "guard" },
              { source: "guard", target: "output" },
            ],
            rationale_steps: ["accept_input", "rewrite_llm", "style_guard", "return_output"],
          },
        },
        {
          pattern_id: "style.pattern_cleaner",
          title: "Pattern Cleaner",
          summary: "Cleanup pass.",
          tags: ["cleanup"],
          complexity: "medium",
          relevance: 0.33,
          selection_state: "neutral",
          retrieval_trace: ["query:empty"],
          logo: { key: "cleaner", label: "PC" },
          config_summary: { roles_total: 2, llm_calls_max: 2, deterministic_guards: 1, hitl_checkpoints: 0 },
          agent_template: {
            nodes: [
              { id: "input", label: "input", kind: "input" },
              { id: "draft", label: "llm.rewrite", kind: "llm" },
              { id: "cleanup", label: "llm.cleanup", kind: "llm" },
              { id: "guard", label: "style.guard", kind: "validator" },
              { id: "output", label: "output", kind: "output" },
            ],
            edges: [
              { source: "input", target: "draft" },
              { source: "draft", target: "cleanup" },
              { source: "cleanup", target: "guard" },
              { source: "guard", target: "output" },
            ],
            rationale_steps: ["accept_input", "rewrite_draft", "cleanup_pass", "style_guard", "return_output"],
          },
        },
      ],
    });

    renderWorkspace();
    const c3Button = await screen.findByRole("button", { name: /Pattern Library \+ RAG/i });
    await user.click(c3Button);
    const patternCheckbox = await screen.findByLabelText("select-style.direct_llm-for-generation");
    const saveButton = await screen.findByRole("button", { name: "Save" });
    expect(saveButton).toBeDisabled();

    await user.click(patternCheckbox);
    expect(saveButton).toBeEnabled();
    expect(vi.mocked(saveArenaPatternSelection)).not.toHaveBeenCalled();

    await user.click(saveButton);

    expect(vi.mocked(saveArenaPatternSelection)).toHaveBeenCalledWith(ARENA.workspace_id, ["style.direct_llm"], []);
  });

  it("expands C3 pattern details accordion and renders template graph", async () => {
    const user = userEvent.setup();
    renderWorkspace();

    const c3Button = await screen.findByRole("button", { name: /Pattern Library \+ RAG/i });
    await user.click(c3Button);

    const detailsButtons = await screen.findAllByRole("button", { name: "Details" });
    await user.click(detailsButtons[0]);
    expect(await screen.findByLabelText("c3-pattern-mini-graph-svg")).toBeInTheDocument();
    expect(await screen.findByRole("region", { name: "c3 pattern details" })).toBeInTheDocument();
  });

  it("switches to C4, saves assignment and edits dataset rows", async () => {
    const user = userEvent.setup();
    vi.mocked(assignArenaDatasets).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      action: "assign_datasets",
      active_dataset_id: "dset_demo_1",
      assigned_dataset_ids: ["dset_demo_1"],
      datasets: [
        {
          dataset_id: "dset_demo_1",
          name: "LinkedIn Golden",
          description: "demo dataset",
          rows_total: 2,
          versions_total: 1,
          updated_at: "2026-05-26T00:10:00+00:00",
          last_version_id: "dsv_demo_1",
          preview_rows: [
            { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
            { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
          ],
        },
      ],
      active_dataset: {
        dataset_id: "dset_demo_1",
        name: "LinkedIn Golden",
        description: "demo dataset",
        rows_total: 2,
        versions_total: 1,
        updated_at: "2026-05-26T00:10:00+00:00",
        last_version_id: "dsv_demo_1",
        created_at: "2026-05-26T00:00:00+00:00",
        rows: [
          { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
          { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
        ],
        versions: [{ version_id: "dsv_demo_1", label: "v1", created_at: "2026-05-26T00:00:00+00:00", rows_total: 2, source: "manual" }],
      },
    });
    vi.mocked(selectArenaDataset).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      action: "select_dataset",
      active_dataset_id: "dset_demo_1",
      assigned_dataset_ids: ["dset_demo_1"],
      datasets: [
        {
          dataset_id: "dset_demo_1",
          name: "LinkedIn Golden",
          description: "demo dataset",
          rows_total: 2,
          versions_total: 1,
          updated_at: "2026-05-26T00:10:00+00:00",
          last_version_id: "dsv_demo_1",
          preview_rows: [
            { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
            { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
          ],
        },
      ],
      active_dataset: {
        dataset_id: "dset_demo_1",
        name: "LinkedIn Golden",
        description: "demo dataset",
        rows_total: 2,
        versions_total: 1,
        updated_at: "2026-05-26T00:10:00+00:00",
        last_version_id: "dsv_demo_1",
        created_at: "2026-05-26T00:00:00+00:00",
        rows: [
          { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
          { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
        ],
        versions: [{ version_id: "dsv_demo_1", label: "v1", created_at: "2026-05-26T00:00:00+00:00", rows_total: 2, source: "manual" }],
      },
    });
    vi.mocked(replaceArenaDatasetRows).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      action: "replace_rows",
      active_dataset_id: "dset_demo_1",
      assigned_dataset_ids: ["dset_demo_1"],
      datasets: [
        {
          dataset_id: "dset_demo_1",
          name: "LinkedIn Golden",
          description: "demo dataset",
          rows_total: 3,
          versions_total: 1,
          updated_at: "2026-05-26T00:12:00+00:00",
          last_version_id: "dsv_demo_1",
          preview_rows: [
            { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
            { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
            { case_id: "case_3", input: "input 3", expected: "expected 3", notes: "" },
          ],
        },
      ],
      active_dataset: {
        dataset_id: "dset_demo_1",
        name: "LinkedIn Golden",
        description: "demo dataset",
        rows_total: 3,
        versions_total: 1,
        updated_at: "2026-05-26T00:12:00+00:00",
        last_version_id: "dsv_demo_1",
        created_at: "2026-05-26T00:00:00+00:00",
        rows: [
          { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
          { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
          { case_id: "case_3", input: "input 3", expected: "expected 3", notes: "" },
        ],
        versions: [{ version_id: "dsv_demo_1", label: "v1", created_at: "2026-05-26T00:00:00+00:00", rows_total: 2, source: "manual" }],
      },
    });

    renderWorkspace();
    const c4Button = await screen.findByRole("button", { name: /Datasets/i });
    await user.click(c4Button);
    expect(await screen.findByText("Datasets studio")).toBeInTheDocument();
    await user.click(await screen.findByLabelText("select-dset_demo_1-for-arena"));
    await user.click(await screen.findByRole("button", { name: "Save" }));
    expect(vi.mocked(assignArenaDatasets)).toHaveBeenCalledWith(ARENA.workspace_id, ["dset_demo_1"]);

    const detailsButtons = await screen.findAllByRole("button", { name: "Details" });
    await user.click(detailsButtons[0]);
    expect(await screen.findByText("Preview first 5 rows")).toBeInTheDocument();

    await user.click(await screen.findByRole("button", { name: "Edit" }));
    expect(await screen.findByText("Edit")).toBeInTheDocument();
    await user.click(await screen.findByRole("button", { name: "Add row" }));
    const caseInputs = await screen.findAllByDisplayValue("");
    await user.type(caseInputs[0], "case_3");
    await user.click(await screen.findByRole("button", { name: "Save changes" }));
    expect(vi.mocked(replaceArenaDatasetRows)).toHaveBeenCalled();
  });

  it("updates C4 evaluation profile and validates it", async () => {
    const user = userEvent.setup();
    vi.mocked(getArenaChatState).mockResolvedValue({
      status: "success",
      capability_id: "c2",
      arena_id: ARENA.workspace_id,
      arena_name: ARENA.name,
      messages: [],
      messages_total: 0,
      candidate_set_draft: {
        ...CANDIDATE_SET,
        candidates: CANDIDATE_SET.candidates.map((candidate, index) => ({
          ...candidate,
          selected_for_tests: index < 2,
        })),
      },
    });
    vi.mocked(saveArenaEvaluationMetrics).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      action: "save_evaluation_metrics",
      comparative_metrics: [
        { metric_id: "quality_f1", title: "Quality F1@K", description: "quality", enabled: true, weight: 0.7 },
        { metric_id: "cost_per_case", title: "Cost / case", description: "cost", enabled: true, weight: 0.3 },
      ],
      diagnostic_signals: [{ signal_id: "retrieval_coverage", title: "Retrieval coverage", description: "retrieval", enabled: true }],
      evaluators: [{ evaluator_id: "golden_oracle", title: "Golden dataset oracle", description: "deterministic", enabled: true }],
      evaluator_metric_links: [],
      budget: { max_cases: 20, max_llm_calls: 100, max_cost_usd: 5.0 },
      versions: [],
      updated_at: "2026-05-26T00:00:00+00:00",
    });
    vi.mocked(validateArenaEvaluationProfile).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      action: "validate_evaluation_profile",
      comparative_metrics: [
        { metric_id: "quality_f1", title: "Quality F1@K", description: "quality", enabled: true, weight: 0.7 },
        { metric_id: "cost_per_case", title: "Cost / case", description: "cost", enabled: true, weight: 0.3 },
      ],
      diagnostic_signals: [{ signal_id: "retrieval_coverage", title: "Retrieval coverage", description: "retrieval", enabled: true }],
      evaluators: [{ evaluator_id: "golden_oracle", title: "Golden dataset oracle", description: "deterministic", enabled: true }],
      evaluator_metric_links: [],
      budget: { max_cases: 20, max_llm_calls: 100, max_cost_usd: 5.0 },
      versions: [],
      updated_at: "2026-05-26T00:00:00+00:00",
      validation_report: {
        status: "ready",
        updated_at: "2026-05-26T00:00:00+00:00",
        issues: [],
      },
    });

    renderWorkspace();
    const c5Button = await screen.findByRole("button", { name: /Metrics/i });
    await user.click(c5Button);

    const metricToggle = await screen.findByLabelText("toggle-metric-cost_per_case");
    await user.click(metricToggle);
    await user.click(await screen.findByRole("button", { name: "Save metrics" }));
    expect(vi.mocked(saveArenaEvaluationMetrics)).toHaveBeenCalled();

    await user.click(await screen.findByRole("button", { name: "Validate profile" }));
    expect(vi.mocked(validateArenaEvaluationProfile)).toHaveBeenCalledWith(ARENA.workspace_id);
    expect(await screen.findByText("Evaluation profile status: ready")).toBeInTheDocument();
  });

  it("saves evaluator-metric matrix from C6 screen", async () => {
    const user = userEvent.setup();
    vi.mocked(saveArenaEvaluationMatrix).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      action: "save_evaluation_matrix",
      comparative_metrics: [
        { metric_id: "quality_f1", title: "Quality F1@K", description: "quality", enabled: true, weight: 0.6 },
      ],
      diagnostic_signals: [
        { signal_id: "retrieval_coverage", title: "Retrieval coverage", description: "retrieval", enabled: true },
      ],
      evaluators: [
        { evaluator_id: "golden_oracle", title: "Golden dataset oracle", description: "deterministic", enabled: true },
      ],
      evaluator_metric_links: [
        { evaluator_id: "golden_oracle", metric_kind: "comparative", metric_id: "quality_f1", enabled: false },
        { evaluator_id: "golden_oracle", metric_kind: "diagnostic", metric_id: "retrieval_coverage", enabled: true },
      ],
      budget: { max_cases: 20, max_llm_calls: 100, max_cost_usd: 5.0 },
      versions: [],
      updated_at: "2026-05-26T00:00:00+00:00",
    });

    renderWorkspace();
    const c6Button = await screen.findByRole("button", { name: /Evaluators/i });
    await user.click(c6Button);

    const matrixToggle = await screen.findByLabelText("toggle-matrix-golden_oracle-comparative-quality_f1");
    await user.click(matrixToggle);
    await user.click(await screen.findByRole("button", { name: "Save matrix" }));
    expect(vi.mocked(saveArenaEvaluationMatrix)).toHaveBeenCalled();
  });

  it("updates matrix columns immediately when evaluator is toggled", async () => {
    const user = userEvent.setup();
    vi.mocked(fetchArenaEvaluationState).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      comparative_metrics: [
        { metric_id: "quality_f1", title: "Quality F1@K", description: "quality", enabled: true, weight: 0.6 },
      ],
      diagnostic_signals: [],
      evaluators: [
        { evaluator_id: "golden_oracle", title: "Golden dataset oracle", description: "deterministic", enabled: true },
        { evaluator_id: "llm_judge", title: "LLM as a judge", description: "semantic", enabled: false },
      ],
      evaluator_metric_links: [
        { evaluator_id: "golden_oracle", metric_kind: "comparative", metric_id: "quality_f1", enabled: true },
        { evaluator_id: "llm_judge", metric_kind: "comparative", metric_id: "quality_f1", enabled: false },
      ],
      candidate_features: { core: true, llm: true, retrieval: false, rerank: false, tool: true, hitl: false },
      budget: { max_cases: 20, max_llm_calls: 100, max_cost_usd: 5.0 },
      versions: [],
      updated_at: "2026-05-26T00:00:00+00:00",
    });

    renderWorkspace();
    const c6Button = await screen.findByRole("button", { name: /Evaluators/i });
    await user.click(c6Button);

    expect(await screen.findByLabelText("toggle-matrix-golden_oracle-comparative-quality_f1")).toBeInTheDocument();
    expect(screen.queryByLabelText("toggle-matrix-llm_judge-comparative-quality_f1")).not.toBeInTheDocument();

    await user.click(await screen.findByLabelText("toggle-evaluator-llm_judge"));
    expect(await screen.findByLabelText("toggle-matrix-llm_judge-comparative-quality_f1")).toBeInTheDocument();

    await user.click(await screen.findByLabelText("toggle-evaluator-golden_oracle"));
    await waitFor(() => {
      expect(screen.queryByLabelText("toggle-matrix-golden_oracle-comparative-quality_f1")).not.toBeInTheDocument();
    });
  });

  it("auto-maps and saves stage mappings from C6 screen", async () => {
    const user = userEvent.setup();
    vi.mocked(autoMapArenaEvaluationStageMappings).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      action: "auto_map_stage_mappings",
      comparative_metrics: [{ metric_id: "quality_f1", title: "Quality F1@K", description: "quality", enabled: true, weight: 0.6 }],
      diagnostic_signals: [{ signal_id: "retrieval_coverage", title: "Retrieval coverage", description: "retrieval", enabled: true }],
      evaluators: [{ evaluator_id: "golden_oracle", title: "Golden dataset oracle", description: "deterministic", enabled: true }],
      evaluator_metric_links: [{ evaluator_id: "golden_oracle", metric_kind: "diagnostic", metric_id: "retrieval_coverage", enabled: true }],
      stage_mappings: [],
      stage_mapping_coverage: [],
      suggested_stage_mappings: [
        {
          mapping_id: "smap_1",
          target_stage: "retrieval",
          candidate_id: "cand_direct",
          candidate_title: "Direct LLM Rewriter",
          selected_node_ids: ["retrieve_main"],
          suggested_node_ids: ["retrieve_main"],
          status: "bound",
          confidence: 0.95,
          reason: "single stage node",
          enabled: true,
          notes: "auto",
          source: "auto",
        },
      ],
      suggested_stage_mapping_coverage: [
        {
          mapping_id: "smap_1",
          target_stage: "retrieval",
          candidate_id: "cand_direct",
          candidate_title: "Direct LLM Rewriter",
          selected_node_ids: ["retrieve_main"],
          selected_nodes_total: 1,
          status: "bound",
          confidence: 0.95,
          reason: "single stage node",
          enabled: true,
          source: "auto",
        },
      ],
      candidate_features: { core: true, llm: true, retrieval: true, rerank: false, tool: true, hitl: false },
      budget: { max_cases: 20, max_llm_calls: 100, max_cost_usd: 5 },
      versions: [],
      updated_at: "2026-05-28T00:00:00+00:00",
    });
    vi.mocked(saveArenaEvaluationStageMappings).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      action: "save_stage_mappings",
      comparative_metrics: [{ metric_id: "quality_f1", title: "Quality F1@K", description: "quality", enabled: true, weight: 0.6 }],
      diagnostic_signals: [{ signal_id: "retrieval_coverage", title: "Retrieval coverage", description: "retrieval", enabled: true }],
      evaluators: [{ evaluator_id: "golden_oracle", title: "Golden dataset oracle", description: "deterministic", enabled: true }],
      evaluator_metric_links: [{ evaluator_id: "golden_oracle", metric_kind: "diagnostic", metric_id: "retrieval_coverage", enabled: true }],
      stage_mappings: [
        {
          mapping_id: "smap_1",
          target_stage: "retrieval",
          candidate_id: "cand_direct",
          candidate_title: "Direct LLM Rewriter",
          selected_node_ids: ["retrieve_main"],
          suggested_node_ids: ["retrieve_main"],
          status: "bound",
          confidence: 0.95,
          reason: "single stage node",
          enabled: true,
          notes: "auto",
          source: "auto",
        },
      ],
      stage_mapping_coverage: [
        {
          mapping_id: "smap_1",
          target_stage: "retrieval",
          candidate_id: "cand_direct",
          candidate_title: "Direct LLM Rewriter",
          selected_node_ids: ["retrieve_main"],
          selected_nodes_total: 1,
          status: "bound",
          confidence: 0.95,
          reason: "single stage node",
          enabled: true,
          source: "auto",
        },
      ],
      candidate_features: { core: true, llm: true, retrieval: true, rerank: false, tool: true, hitl: false },
      budget: { max_cases: 20, max_llm_calls: 100, max_cost_usd: 5 },
      versions: [],
      updated_at: "2026-05-28T00:00:00+00:00",
    });

    renderWorkspace();
    const c6Button = await screen.findByRole("button", { name: /Evaluators/i });
    await user.click(c6Button);

    await user.click(await screen.findByRole("button", { name: "Auto-map stages" }));
    expect(vi.mocked(autoMapArenaEvaluationStageMappings)).toHaveBeenCalledWith(ARENA.workspace_id);
    expect(await screen.findByDisplayValue("retrieve_main")).toBeInTheDocument();

    await user.click(await screen.findByRole("button", { name: "Save mapping" }));
    expect(vi.mocked(saveArenaEvaluationStageMappings)).toHaveBeenCalled();
  });

  it("locks unavailable diagnostics based on candidate features", async () => {
    const user = userEvent.setup();
    vi.mocked(getArenaChatState).mockResolvedValue({
      status: "success",
      capability_id: "c2",
      arena_id: ARENA.workspace_id,
      arena_name: ARENA.name,
      messages: [],
      messages_total: 0,
      candidate_set_draft: {
        ...CANDIDATE_SET,
        candidates: CANDIDATE_SET.candidates.map((candidate, index) => ({
          ...candidate,
          selected_for_tests: index < 1,
        })),
      },
    });
    vi.mocked(fetchArenaEvaluationState).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      comparative_metrics: [
        { metric_id: "quality_f1", title: "Quality F1@K", description: "quality", enabled: true, weight: 0.6, availability_status: "available" },
      ],
      diagnostic_signals: [
        {
          signal_id: "retrieval_coverage",
          title: "Retrieval coverage",
          description: "retrieval",
          enabled: false,
          availability_status: "unavailable",
          availability_reason: "Requires features not found in selected candidates: retrieval.",
        },
      ],
      evaluators: [
        { evaluator_id: "golden_oracle", title: "Golden dataset oracle", description: "deterministic", enabled: true },
      ],
      evaluator_metric_links: [],
      candidate_features: { core: true, llm: true, retrieval: false, rerank: false, tool: true, hitl: false },
      budget: { max_cases: 20, max_llm_calls: 100, max_cost_usd: 5.0 },
      versions: [],
      updated_at: "2026-05-26T00:00:00+00:00",
    });

    renderWorkspace();
    const c5Button = await screen.findByRole("button", { name: /Metrics/i });
    await user.click(c5Button);

    const signalToggle = await screen.findByLabelText("toggle-signal-retrieval_coverage");
    expect(signalToggle).toBeDisabled();
    expect(await screen.findByText(/Candidate features:/i)).toBeInTheDocument();
    expect(await screen.findByText(/Requires features not found in selected candidates/i)).toBeInTheDocument();
  });

  it("saves and validates C5 optimizer setup, then launches queued run", async () => {
    const user = userEvent.setup();
    vi.mocked(getArenaChatState).mockResolvedValue({
      status: "success",
      capability_id: "c2",
      arena_id: ARENA.workspace_id,
      arena_name: ARENA.name,
      messages: [],
      messages_total: 0,
      candidate_set_draft: {
        ...CANDIDATE_SET,
        candidates: CANDIDATE_SET.candidates.map((candidate, index) => ({
          ...candidate,
          selected_for_tests: index < 2,
        })),
      },
    });
    vi.mocked(fetchArenaDatasetState).mockResolvedValue({
      status: "success",
      capability_id: "c4",
      arena_id: ARENA.workspace_id,
      active_dataset_id: "dset_demo_1",
      assigned_dataset_ids: ["dset_demo_1"],
      datasets: [
        {
          dataset_id: "dset_demo_1",
          name: "LinkedIn Golden",
          description: "demo dataset",
          rows_total: 2,
          versions_total: 1,
          updated_at: "2026-05-26T00:00:00+00:00",
          last_version_id: "dsv_demo_1",
          preview_rows: [
            { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
            { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
          ],
        },
      ],
      active_dataset: {
        dataset_id: "dset_demo_1",
        name: "LinkedIn Golden",
        description: "demo dataset",
        rows_total: 2,
        versions_total: 1,
        updated_at: "2026-05-26T00:00:00+00:00",
        last_version_id: "dsv_demo_1",
        preview_rows: [
          { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
          { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
        ],
        created_at: "2026-05-26T00:00:00+00:00",
        rows: [
          { case_id: "case_1", input: "input 1", expected: "expected 1", notes: "" },
          { case_id: "case_2", input: "input 2", expected: "expected 2", notes: "" },
        ],
        versions: [{ version_id: "dsv_demo_1", label: "v1", created_at: "2026-05-26T00:00:00+00:00", rows_total: 2, source: "manual" }],
      },
    });
    vi.mocked(saveArenaOptimizerSetup).mockResolvedValue({
      status: "success",
      capability_id: "c5",
      arena_id: ARENA.workspace_id,
      action: "save_optimizer_setup",
      methods: [
        { method_id: "random_search", title: "Random search", description: "baseline", enabled: true },
        { method_id: "grid_search", title: "Grid search", description: "deterministic", enabled: true },
      ],
      controls: [
        { control_id: "tune_prompts", title: "Tune prompts", description: "prompt scope", enabled: true },
        { control_id: "tune_pattern_mix", title: "Tune pattern mix", description: "pattern scope", enabled: true },
      ],
      run_plan: { epochs_total: 3, candidates_per_epoch: 4, max_parallel_trials: 2, early_stop_patience: 1 },
      budget: { max_cases: 24, max_llm_calls: 200, max_cost_usd: 8, max_runtime_minutes: 30 },
      versions: [],
      launch_history: [],
      updated_at: "2026-05-26T00:00:00+00:00",
    });
    vi.mocked(validateArenaOptimizerSetup).mockResolvedValue({
      status: "success",
      capability_id: "c5",
      arena_id: ARENA.workspace_id,
      action: "validate_optimizer_setup",
      methods: [
        { method_id: "random_search", title: "Random search", description: "baseline", enabled: true },
      ],
      controls: [
        { control_id: "tune_prompts", title: "Tune prompts", description: "prompt scope", enabled: true },
      ],
      run_plan: { epochs_total: 3, candidates_per_epoch: 4, max_parallel_trials: 2, early_stop_patience: 1 },
      budget: { max_cases: 24, max_llm_calls: 200, max_cost_usd: 8, max_runtime_minutes: 30 },
      versions: [],
      launch_history: [],
      updated_at: "2026-05-26T00:00:00+00:00",
      validation_report: { status: "ready", updated_at: "2026-05-26T00:00:00+00:00", issues: [] },
    });
    vi.mocked(launchArenaOptimizer).mockResolvedValue({
      status: "success",
      capability_id: "c5",
      arena_id: ARENA.workspace_id,
      action: "launch_optimizer",
      methods: [{ method_id: "random_search", title: "Random search", description: "baseline", enabled: true }],
      controls: [{ control_id: "tune_prompts", title: "Tune prompts", description: "prompt scope", enabled: true }],
      run_plan: { epochs_total: 3, candidates_per_epoch: 4, max_parallel_trials: 2, early_stop_patience: 1 },
      budget: { max_cases: 24, max_llm_calls: 200, max_cost_usd: 8, max_runtime_minutes: 30 },
      versions: [],
      launch_history: [
        {
          run_id: "run_demo_1",
          created_at: "2026-05-26T00:00:00+00:00",
          status: "queued",
          method_id: "random_search",
          epochs_total: 3,
          selected_candidates_total: 2,
          assigned_datasets_total: 1,
          triggered_by: "manual",
        },
      ],
      updated_at: "2026-05-26T00:00:00+00:00",
      run: {
        run_id: "run_demo_1",
        created_at: "2026-05-26T00:00:00+00:00",
        status: "queued",
        method_id: "random_search",
        epochs_total: 3,
        selected_candidates_total: 2,
        assigned_datasets_total: 1,
        triggered_by: "manual",
      },
    });

    renderWorkspace();
    const c7Button = await screen.findByRole("button", { name: /Optimizer Run Monitor/i });
    await user.click(c7Button);

    expect(await screen.findByText("Optimizer setup + launch guardrails")).toBeInTheDocument();
    await user.click(await screen.findByLabelText("toggle-method-grid_search"));
    await user.click(await screen.findByRole("button", { name: "Save setup" }));
    expect(vi.mocked(saveArenaOptimizerSetup)).toHaveBeenCalled();

    await user.click(await screen.findByRole("button", { name: "Validate" }));
    expect(vi.mocked(validateArenaOptimizerSetup)).toHaveBeenCalledWith(ARENA.workspace_id);
    expect(await screen.findByText("Optimizer preflight status: ready")).toBeInTheDocument();

    await user.click(await screen.findByRole("button", { name: "Launch" }));
    expect(vi.mocked(launchArenaOptimizer)).toHaveBeenCalledWith(ARENA.workspace_id, "manual");
    expect(await screen.findByText(/run_demo_1/i)).toBeInTheDocument();
  });
});
