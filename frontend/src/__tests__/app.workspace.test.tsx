import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../App";
import type { ArenaRecord, C2CandidateSetDraft, Capability } from "../types";

// Русский комментарий: мокируем API-слой, чтобы UI-тесты были детерминированными и не зависели от backend-сервера.
vi.mock("../api", () => ({
  createArena: vi.fn(),
  deleteArena: vi.fn(),
  duplicateArena: vi.fn(),
  fetchCapabilityCatalog: vi.fn(),
  fetchArenaPatternSelection: vi.fn(),
  fetchStubCapability: vi.fn(),
  getArena: vi.fn(),
  getArenaChatState: vi.fn(),
  listArenas: vi.fn(),
  postArenaChatMessage: vi.fn(),
  renameArena: vi.fn(),
  saveArenaPatternSelection: vi.fn(),
  searchArenaPatterns: vi.fn(),
  selectArenaCandidatesForTests: vi.fn(),
}));

import {
  createArena,
  deleteArena,
  duplicateArena,
  fetchCapabilityCatalog,
  fetchArenaPatternSelection,
  fetchStubCapability,
  getArena,
  getArenaChatState,
  listArenas,
  postArenaChatMessage,
  renameArena,
  saveArenaPatternSelection,
  searchArenaPatterns,
  selectArenaCandidatesForTests,
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
  { id: "c2", name: "Task Chat + Candidates", description: "Generate candidates from chat.", status: "enabled", badge_count: 1 },
  { id: "c3", name: "Pattern Library + RAG", description: "Planned", status: "planned", badge_count: 0 },
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

    vi.mocked(postArenaChatMessage).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(selectArenaCandidatesForTests).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(createArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(renameArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(duplicateArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(deleteArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(fetchStubCapability).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(saveArenaPatternSelection).mockRejectedValue(new Error("not used in this test"));
  });

  it("renders candidates list and allows selecting candidate row", async () => {
    const user = userEvent.setup();
    renderWorkspace();

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
});
