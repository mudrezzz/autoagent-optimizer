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
  fetchStubCapability: vi.fn(),
  getArena: vi.fn(),
  getArenaChatState: vi.fn(),
  listArenas: vi.fn(),
  postArenaChatMessage: vi.fn(),
  renameArena: vi.fn(),
}));

import {
  createArena,
  deleteArena,
  duplicateArena,
  fetchCapabilityCatalog,
  fetchStubCapability,
  getArena,
  getArenaChatState,
  listArenas,
  postArenaChatMessage,
  renameArena,
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

    vi.mocked(postArenaChatMessage).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(createArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(renameArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(duplicateArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(deleteArena).mockRejectedValue(new Error("not used in this test"));
    vi.mocked(fetchStubCapability).mockRejectedValue(new Error("not used in this test"));
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
});
