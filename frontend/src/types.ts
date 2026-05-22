// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РёРї capability, РїСЂРёС…РѕРґСЏС‰РёР№ РёР· backend capability-РєР°С‚Р°Р»РѕРіР°.
export type Capability = {
  id: string;
  name: string;
  description: string;
  status: "enabled" | "planned" | "beta" | "disabled" | string;
  route?: string;
  badge_count?: number;
};

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РёРї РѕС‚РІРµС‚Р° capability-РєР°С‚Р°Р»РѕРіР°.
export type CapabilityCatalogResponse = {
  version: string;
  ux_reference?: string;
  capabilities: Capability[];
};

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РёРї issue РІ compile report.
export type CompileIssue = {
  severity: "warning" | "error" | string;
  message: string;
};

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РёРї compile summary РґР»СЏ KPI-РІРёРґР¶РµС‚РѕРІ.
export type CompileSummary = {
  status: string;
  source: string;
  node_mappings: number;
  warnings: number;
  errors: number;
};

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РёРї graph IR summary РґР»СЏ KPI-РІРёРґР¶РµС‚РѕРІ.
export type GraphIrSummary = {
  available: boolean;
  entry_node?: string;
  nodes_total?: number;
  edges_total?: number;
  terminal_nodes?: string[];
};

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РёРї РѕС‚РІРµС‚Р° СѓСЃРїРµС€РЅРѕРіРѕ C1 РІС‹Р·РѕРІР°.
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

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РёРї РѕС€РёР±РѕС‡РЅРѕРіРѕ payload РѕС‚ backend.
export type ErrorPayload = {
  status: "error";
  message: string;
  [key: string]: unknown;
};

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РёРї payload planned capability РґР»СЏ C2..C6.
export type StubPayload = {
  status: "stub_success";
  capability_id: string;
  capability_name: string;
  capability_status: string;
  summary: string;
  next_step: string;
};
