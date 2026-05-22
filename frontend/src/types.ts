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

// Русский комментарий: тип записи workspace в C1 API.
export type WorkspaceRecord = {
  workspace_id: string;
  name: string;
  description: string;
  created_at: string;
  tenant_id: string;
  owner_user_id: string;
};

// Русский комментарий: тип записи project в C1 API.
export type ProjectRecord = {
  project_id: string;
  workspace_id: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
  tenant_id: string;
  owner_user_id: string;
};

// Русский комментарий: ответ списка workspace.
export type WorkspacesListResponse = {
  status: "success";
  workspaces: WorkspaceRecord[];
  total: number;
};

// Русский комментарий: ответ создания workspace.
export type WorkspaceCreateResponse = {
  status: "success";
  workspace: WorkspaceRecord;
};

// Русский комментарий: ответ списка project в workspace.
export type ProjectsListResponse = {
  status: "success";
  workspace_id: string;
  projects: ProjectRecord[];
  total: number;
};

// Русский комментарий: ответ создания project.
export type ProjectCreateResponse = {
  status: "success";
  project: ProjectRecord;
};

// Русский комментарий: ответ получения project по id.
export type ProjectGetResponse = {
  status: "success";
  project: ProjectRecord;
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

// Русский комментарий: тип ответа успешного C1 legacy вызова.
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
