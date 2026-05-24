// Русский комментарий: тип capability, приходящий из backend capability-каталога.
export type Capability = {
  id: string;
  name: string;
  description: string;
  status: "enabled" | "planned" | "beta" | "disabled" | string;
  route?: string;
  badge_count?: number;
};

// Русский комментарий: тип ответа capability-каталога.
export type CapabilityCatalogResponse = {
  version: string;
  ux_reference?: string;
  capabilities: Capability[];
};

// Русский комментарий: тип записи battle-арены в C1 API.
export type ArenaRecord = {
  workspace_id: string;
  name: string;
  description: string;
  created_at: string;
  tenant_id: string;
  owner_user_id: string;
};

// Русский комментарий: ответ списка арен.
export type ArenasListResponse = {
  status: "success";
  arenas: ArenaRecord[];
  total: number;
};

// Русский комментарий: ответ создания/обновления/дублирования арены.
export type ArenaMutationResponse = {
  status: "success";
  arena: ArenaRecord;
};

// Русский комментарий: ответ удаления арены.
export type ArenaDeleteResponse = {
  status: "success";
  arena_id: string;
};

// Русский комментарий: ответ получения арены по id.
export type ArenaGetResponse = {
  status: "success";
  arena: ArenaRecord;
};

// Русский комментарий: тип error payload от backend.
export type ErrorPayload = {
  status: "error";
  message: string;
  code?: string;
  [key: string]: unknown;
};

// Русский комментарий: тип payload planned capability для C2..C6.
export type StubPayload = {
  status: "stub_success";
  capability_id: string;
  capability_name: string;
  capability_status: string;
  summary: string;
  next_step: string;
};

// Русский комментарий: тип chat-сообщения C2 для brief-to-candidates UI.
export type C2ChatMessage = {
  message_id: string;
  role: "user" | "assistant" | "system" | string;
  content: string;
  created_at: string;
};

// Русский комментарий: тип одного кандидата из C2 candidate draft.
export type C2CandidateDraftItem = {
  candidate_id: string;
  title: string;
  pattern_ref: string;
  summary: string;
  rationale: string;
  dsl_stub_ref: string;
  estimated_complexity: string;
  logo?: {
    key: string;
    label: string;
  };
  config_summary?: {
    roles_total: number;
    llm_calls_max: number;
    deterministic_guards: number;
    hitl_checkpoints: number;
  };
  architecture_steps?: string[];
  mini_graph?: {
    nodes: Array<{
      id: string;
      label: string;
      kind: string;
    }>;
    edges: Array<{
      source: string;
      target: string;
    }>;
  };
};

// Русский комментарий: тип candidate set draft, сформированного на основе chat brief.
export type C2CandidateSetDraft = {
  candidate_set_id: string;
  source: string;
  task_brief: string;
  generation_mode: string;
  arena_id: string;
  candidates: C2CandidateDraftItem[];
  total: number;
};

// Русский комментарий: ответ чтения текущего C2 chat state для арены.
export type C2ChatStateResponse = {
  status: "success";
  capability_id: "c2";
  arena_id: string;
  arena_name: string;
  messages: C2ChatMessage[];
  messages_total: number;
  candidate_set_draft: C2CandidateSetDraft | null;
};

// Русский комментарий: ответ отправки сообщения в C2 чат.
export type C2ChatPostMessageResponse = {
  status: "success";
  capability_id: "c2";
  arena_id: string;
  message: C2ChatMessage;
  assistant_message: C2ChatMessage | null;
  messages: C2ChatMessage[];
  messages_total: number;
  candidate_set_draft: C2CandidateSetDraft | null;
};

// Русский комментарий: элемент C3 pattern search выдачи для библиотеки паттернов.
export type C3PatternItem = {
  pattern_id: string;
  title: string;
  summary: string;
  tags: string[];
  complexity: string;
  relevance: number;
  selection_state: "include" | "exclude" | "neutral" | string;
  retrieval_trace: string[];
};

// Русский комментарий: состояние include/exclude выбора паттернов в C3.
export type C3PatternSelection = {
  include_pattern_ids: string[];
  exclude_pattern_ids: string[];
  updated_at: string;
};

// Русский комментарий: ответ чтения C3 pattern selection.
export type C3PatternSelectionResponse = {
  status: "success";
  capability_id: "c3";
  arena_id: string;
  selection: C3PatternSelection;
};

// Русский комментарий: ответ поиска C3 паттернов с retrieval trace.
export type C3PatternSearchResponse = {
  status: "success";
  capability_id: "c3";
  arena_id: string;
  query: string;
  query_tokens: string[];
  total_candidates: number;
  returned: number;
  selection: C3PatternSelection;
  patterns: C3PatternItem[];
};

// Русский комментарий: тип issue в compile report legacy debug endpoint.
export type CompileIssue = {
  severity: "warning" | "error" | string;
  message: string;
};

// Русский комментарий: тип compile summary для legacy debug endpoint.
export type CompileSummary = {
  status: string;
  source: string;
  node_mappings: number;
  warnings: number;
  errors: number;
};

// Русский комментарий: тип graph IR summary для legacy debug endpoint.
export type GraphIrSummary = {
  available: boolean;
  entry_node?: string;
  nodes_total?: number;
  edges_total?: number;
  terminal_nodes?: string[];
};

// Русский комментарий: тип ответа успешного legacy C1 validate/compile.
export type C1SuccessPayload = {
  status: "success";
  capability_id: "c1";
  dsl_file: string;
  dsl_summary: Record<string, unknown>;
  compile_summary: CompileSummary;
  compile_report: {
    status: string;
    source: string;
    node_mappings: Array<Record<string, unknown>>;
    issues: CompileIssue[];
  };
  graph_ir_summary: GraphIrSummary;
};
