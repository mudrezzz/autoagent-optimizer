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
  selected_for_tests?: boolean;
  compile_readiness?: C2CandidateCompileReadiness;
};

// Русский комментарий: compile-readiness отчет по конкретному кандидату после C2 compile gate.
export type C2CandidateCompileReadiness = {
  status: "draft" | "ready" | "failed" | string;
  dsl_file: string;
  compile_summary: {
    status: string;
    source: string;
    node_mappings: number;
    warnings: number;
    errors: number;
  } | null;
  issues: Array<{
    severity: string;
    message: string;
    context?: Record<string, unknown>;
  }>;
  graph_ir_summary: {
    available: boolean;
    entry_node?: string | null;
    nodes_total?: number;
    edges_total?: number;
    terminal_nodes?: string[];
  };
  compiled_at: string | null;
  attempts_used?: number;
  user_visible_issue?: boolean;
};

// Русский комментарий: compile gate агрегат по candidate set для состояния готовности.
export type C2CompileGateSummary = {
  status: "draft" | "ready" | "failed" | string;
  compiled_candidates: number;
  ready_candidates: number;
  failed_candidates: number;
  selected_candidates?: number;
  total_candidates: number;
  processed_at: string | null;
  max_compile_attempts?: number | null;
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
  compile_gate?: C2CompileGateSummary;
};

// Русский комментарий: ответ чтения текущего C2 chat state для арены.
export type C2ChatStateResponse = {
  status: "success";
  capability_id: "c2";
  arena_id: string;
  arena_name: string;
  messages: C2ChatMessage[];
  messages_total: number;
  candidate_set_draft?: C2CandidateSetDraft | null;
};

// Русский комментарий: ответ отправки сообщения в C2 чат.
export type C2ChatPostMessageResponse = {
  status: "success";
  capability_id: string;
  arena_id: string;
  message: C2ChatMessage;
  assistant_message: C2ChatMessage | null;
  messages: C2ChatMessage[];
  messages_total: number;
  candidate_set_draft: C2CandidateSetDraft | null;
  copilot_context?: {
    resolved_action: string;
    allowed_actions: string[];
    summary: string;
  };
};

// Русский комментарий: ответ C2 endpoint выбора кандидатов и внутренней подготовки к тестам.
export type C2SelectForTestsResponse = {
  status: "success";
  capability_id: "c2";
  action: "select_candidates_for_tests";
  arena_id: string;
  assistant_message: C2ChatMessage | null;
  messages: C2ChatMessage[];
  messages_total: number;
  candidate_set_draft: C2CandidateSetDraft;
  compile_gate: C2CompileGateSummary;
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
  agent_template?: {
    nodes: Array<{
      id: string;
      label: string;
      kind: string;
    }>;
    edges: Array<{
      source: string;
      target: string;
    }>;
    rationale_steps: string[];
  };
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

// Русский комментарий: строка dataset для C4 Dataset Studio.
export type C4DatasetTargetStage = "retrieval" | "rerank" | "synthesis" | "final";

// Русский комментарий: структура expected-пейлоада для stage-aware dataset строки.
export type C4DatasetRow = {
  case_id: string;
  input: string;
  target_stage: C4DatasetTargetStage | string;
  expected_payload: Record<string, unknown>;
  expected: string;
  notes: string;
};

// Русский комментарий: version snapshot metadata для dataset.
export type C4DatasetVersion = {
  version_id: string;
  label: string;
  created_at: string;
  rows_total: number;
  source: string;
};

// Русский комментарий: summary dataset для списка в C4 Studio.
export type C4DatasetSummary = {
  dataset_id: string;
  name: string;
  description: string;
  rows_total: number;
  versions_total: number;
  updated_at: string;
  last_version_id: string;
  preview_rows: C4DatasetRow[];
};

// Русский комментарий: detail активного dataset в C4 Studio.
export type C4DatasetDetail = C4DatasetSummary & {
  created_at: string;
  rows: C4DatasetRow[];
  versions: C4DatasetVersion[];
};

// Русский комментарий: ответ состояния C4 Dataset Studio.
export type C4DatasetStateResponse = {
  status: "success";
  capability_id: "c4";
  arena_id: string;
  active_dataset_id: string;
  assigned_dataset_ids: string[];
  datasets: C4DatasetSummary[];
  active_dataset: C4DatasetDetail | null;
  action?: string;
  row?: C4DatasetRow;
  dataset?: C4DatasetDetail;
  version?: C4DatasetVersion;
  validation_report?: {
    dataset_id: string;
    rows_total: number;
    status: "ok" | "failed";
    issues: Array<{
      severity: "error" | "warning" | string;
      code: string;
      row_index: number | null;
      message: string;
    }>;
  };
};

// Русский комментарий: comparative метрика evaluation profile.
export type C4ComparativeMetric = {
  metric_id: string;
  title: string;
  description: string;
  enabled: boolean;
  weight: number;
  required_features?: string[];
  availability_status?: "available" | "unavailable" | string;
  availability_reason?: string;
  target_stage?: "retrieval" | "rerank" | "synthesis" | "final" | string;
};

// Русский комментарий: diagnostic сигнал evaluation profile.
export type C4DiagnosticSignal = {
  signal_id: string;
  title: string;
  description: string;
  enabled: boolean;
  required_features?: string[];
  availability_status?: "available" | "unavailable" | string;
  availability_reason?: string;
};

// Русский комментарий: evaluator adapter для evaluation profile.
export type C4Evaluator = {
  evaluator_id: string;
  adapter_kind?: string;
  title: string;
  description: string;
  enabled: boolean;
  requires_dataset?: boolean;
  requires_llm?: boolean;
  requires_stage_mapping?: boolean;
  supported_metric_refs?: string[];
  supported_metric_kinds?: string[];
  budget_cost_model?: string;
  adapter_status?: "available" | "planned" | "needs_config" | string;
  adapter_status_reason?: string;
};

// Русский комментарий: связь покрытия между evaluator и метрикой/сигналом.
export type C4EvaluatorMetricLink = {
  evaluator_id: string;
  metric_kind: "comparative" | "diagnostic" | string;
  metric_id: string;
  enabled: boolean;
  compatibility_status?: "compatible" | "incompatible" | string;
  compatibility_reason?: string;
};

// Русский комментарий: пользовательская запись stage_ref binding для non-final оценки.
export type C4StageBinding = {
  binding_id: string;
  stage_ref: string;
  target_stage: "retrieval" | "rerank" | "synthesis" | "final" | string;
  match_policy: "primary_only" | "all_must_pass" | "best_of" | string;
  enabled: boolean;
  notes: string;
};

// Русский комментарий: результат резолва stage_ref на конкретного кандидата.
export type C4StageBindingCandidateCoverage = {
  binding_id: string;
  candidate_id: string;
  candidate_title: string;
  status: "bound" | "ambiguous" | "missing" | string;
  resolved_step_ids: string[];
  resolved_steps_total: number;
  confidence: number;
  reason: string;
};

// Русский комментарий: агрегированный coverage по одному stage_ref binding.
export type C4StageBindingCoverage = {
  binding_id: string;
  stage_ref: string;
  target_stage: "retrieval" | "rerank" | "synthesis" | "final" | string;
  match_policy: "primary_only" | "all_must_pass" | "best_of" | string;
  enabled: boolean;
  summary: {
    candidates_total: number;
    bound_total: number;
    ambiguous_total: number;
    missing_total: number;
  };
  candidates: C4StageBindingCandidateCoverage[];
};

// Русский комментарий: строка пользовательского stage mapping (target_stage -> candidate node ids).
export type C4StageMapping = {
  mapping_id: string;
  target_stage: "retrieval" | "rerank" | "synthesis" | "final" | string;
  candidate_id: string;
  candidate_title: string;
  selected_node_ids: string[];
  suggested_node_ids: string[];
  status: "bound" | "ambiguous" | "missing" | string;
  confidence: number;
  reason: string;
  enabled: boolean;
  notes: string;
  source: "auto" | "manual" | string;
};

// Русский комментарий: coverage-вердикт для одной строки stage mapping.
export type C4StageMappingCoverage = {
  mapping_id: string;
  target_stage: "retrieval" | "rerank" | "synthesis" | "final" | string;
  candidate_id: string;
  candidate_title: string;
  selected_node_ids: string[];
  selected_nodes_total: number;
  status: "bound" | "ambiguous" | "missing" | string;
  confidence: number;
  reason: string;
  enabled: boolean;
  source: "auto" | "manual" | string;
};

// Русский комментарий: бюджет evaluation profile.
export type C4EvaluationBudget = {
  max_cases: number;
  max_llm_calls: number;
  max_cost_usd: number;
};

// Русский комментарий: версия evaluation profile.
export type C4EvaluationVersion = {
  version_id: string;
  label: string;
  created_at: string;
  source: string;
  enabled_comparative_total: number;
  enabled_diagnostic_total: number;
  enabled_evaluators_total: number;
  enabled_stage_bindings_total?: number;
  enabled_stage_mappings_total?: number;
};

// Русский комментарий: item HITL proposal для task-specific metric crafting.
export type C4MetricProposalItem = {
  proposal_item_id: string;
  metric_kind: "comparative" | "diagnostic" | string;
  metric_id: string;
  title: string;
  description: string;
  enabled: boolean;
  selected: boolean;
  weight: number;
  required_features: string[];
  target_stage: "retrieval" | "rerank" | "synthesis" | "final" | string;
  recommended_evaluators: string[];
  rationale: string;
  compatibility_status: "ready" | "review_only" | "needs_evaluator" | "not_applicable" | string;
  compatibility_reason: string;
};

// Русский комментарий: HITL proposal метрик, который не меняет profile до явного apply.
export type C4MetricProposal = {
  proposal_id: string;
  arena_id: string;
  profile_id: string;
  status: "draft" | "applied" | string;
  source: string;
  created_at: string;
  applied_at?: string;
  summary: string;
  items: C4MetricProposalItem[];
};

// Русский комментарий: ответ состояния C4 Metrics & Evaluators Studio.
export type C4EvaluationStateResponse = {
  status: "success";
  capability_id: "c4";
  arena_id: string;
  comparative_metrics: C4ComparativeMetric[];
  diagnostic_signals: C4DiagnosticSignal[];
  evaluators: C4Evaluator[];
  stage_mappings?: C4StageMapping[];
  stage_mapping_coverage?: C4StageMappingCoverage[];
  stage_bindings?: C4StageBinding[];
  stage_binding_coverage?: C4StageBindingCoverage[];
  evaluator_metric_links: C4EvaluatorMetricLink[];
  latest_metric_proposal?: C4MetricProposal | null;
  candidate_features?: Record<string, boolean>;
  budget: C4EvaluationBudget;
  versions: C4EvaluationVersion[];
  updated_at: string;
  action?: string;
  version?: C4EvaluationVersion;
  suggested_stage_mappings?: C4StageMapping[];
  suggested_stage_mapping_coverage?: C4StageMappingCoverage[];
  suggested_stage_bindings?: C4StageBinding[];
  suggested_stage_binding_coverage?: C4StageBindingCoverage[];
  validation_report?: {
    status: "ready" | "warnings" | "invalid";
    updated_at: string;
    issues: Array<{
      severity: "error" | "warning" | string;
      code: string;
      message: string;
    }>;
  };
};

// Русский комментарий: метод оптимизации C5 Optimizer Setup.
export type C5OptimizerMethod = {
  method_id: string;
  title: string;
  description: string;
  enabled: boolean;
};

// Русский комментарий: control-переключатель C5 для области оптимизации.
export type C5OptimizerControl = {
  control_id: string;
  title: string;
  description: string;
  enabled: boolean;
};

// Русский комментарий: run-plan ограничения C5.
export type C5OptimizerRunPlan = {
  epochs_total: number;
  candidates_per_epoch: number;
  max_parallel_trials: number;
  early_stop_patience: number;
};

// Русский комментарий: бюджетные ограничения C5.
export type C5OptimizerBudget = {
  max_cases: number;
  max_llm_calls: number;
  max_cost_usd: number;
  max_runtime_minutes: number;
};

// Русский комментарий: версия optimizer setup профиля C5.
export type C5OptimizerVersion = {
  version_id: string;
  label: string;
  created_at: string;
  source: string;
  enabled_methods_total: number;
  enabled_controls_total: number;
  epochs_total: number;
};

// Русский комментарий: запись run history для C5 launch.
export type C5OptimizerLaunchEntry = {
  run_id: string;
  created_at: string;
  status: string;
  method_id: string;
  epochs_total: number;
  selected_candidates_total: number;
  assigned_datasets_total: number;
  triggered_by: string;
};

// Русский комментарий: ответ состояния C5 Optimizer Setup Studio.
export type C5OptimizerStateResponse = {
  status: "success" | "error";
  capability_id: "c5";
  arena_id: string;
  methods: C5OptimizerMethod[];
  controls: C5OptimizerControl[];
  run_plan: C5OptimizerRunPlan;
  budget: C5OptimizerBudget;
  versions: C5OptimizerVersion[];
  launch_history: C5OptimizerLaunchEntry[];
  updated_at: string;
  action?: string;
  code?: string;
  message?: string;
  version?: C5OptimizerVersion;
  run?: C5OptimizerLaunchEntry;
  validation_report?: {
    status: "ready" | "warnings" | "invalid";
    updated_at: string;
    issues: Array<{
      severity: "error" | "warning" | string;
      code: string;
      message: string;
    }>;
  };
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
