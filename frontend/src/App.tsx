import { useEffect, useMemo, useState } from "react";

import { fetchCapabilityCatalog, fetchStubCapability, runC1ValidateCompile } from "./api";
import type { C1SuccessPayload, Capability, CompileIssue, ErrorPayload } from "./types";
import { exportJsonToFile, makeTimestampedFileName, prettyJson } from "./utils";

declare global {
  interface Window {
    lucide?: {
      createIcons: () => void;
    };
  }
}

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: fallback-РєР°С‚Р°Р»РѕРі, РµСЃР»Рё backend capability API РІСЂРµРјРµРЅРЅРѕ РЅРµРґРѕСЃС‚СѓРїРµРЅ.
const FALLBACK_CAPABILITIES: Capability[] = [
  {
    id: "c1",
    name: "DSL/IR Studio",
    description: "Validate DSL and compile Graph IR.",
    status: "enabled",
    badge_count: 1,
  },
  {
    id: "c2",
    name: "Runtime Run",
    description: "Workflow execution and trace.",
    status: "planned",
    badge_count: 0,
  },
  {
    id: "c3",
    name: "Evaluation Profile",
    description: "Profile-based evaluation.",
    status: "planned",
    badge_count: 0,
  },
  {
    id: "c4",
    name: "Arena Ranking",
    description: "Compare candidates.",
    status: "planned",
    badge_count: 0,
  },
  {
    id: "c5",
    name: "Evidence & Diagnostics",
    description: "Comparative and diagnostics layers.",
    status: "planned",
    badge_count: 0,
  },
  {
    id: "c6",
    name: "Champion Bundle",
    description: "Champion export and parity.",
    status: "planned",
    badge_count: 0,
  },
];

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РёРєРѕРЅРєРё capability РґР»СЏ Р»РµРІРѕРіРѕ РјРµРЅСЋ workbench.
const CAPABILITY_ICONS: Record<string, string> = {
  c1: "file-check-2",
  c2: "play-circle",
  c3: "list-checks",
  c4: "trophy",
  c5: "activity",
  c6: "package-check",
};

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: СЃС‚СЂСѓРєС‚СѓСЂРёСЂРѕРІР°РЅРЅС‹Р№ state С‚РµРєСѓС‰РµРіРѕ UI-С†РёРєР»Р° C1.
type UiState = {
  capabilities: Capability[];
  activeCapabilityId: string;
  dslFilePath: string;
  jsonText: string;
  budgetPercent: number;
  budgetStage: string;
  metricValidation: string;
  metricValidationDelta: { text: string; tone: "neutral" | "positive" | "negative" };
  metricNodes: string;
  metricEdges: string;
  metricIssues: string;
  compileSource: string;
  compileSummaryCells: Array<{ key: string; value: string }>;
  issues: CompileIssue[];
  bottleneckId: string;
  bottleneckText: string;
  suggestions: Array<{ tag: string; title: string; detail: string }>;
  exportMeta: string;
  lastPayload: C1SuccessPayload | null;
  lastErrorPayload: ErrorPayload | null;
};

// Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РєРѕСЂРЅРµРІРѕР№ React-РєРѕРјРїРѕРЅРµРЅС‚ frontend workbench РІ РєР°СЂРєР°СЃРµ app-v3.
export function App(): JSX.Element {
  const [state, setState] = useState<UiState>({
    capabilities: FALLBACK_CAPABILITIES,
    activeCapabilityId: "c1",
    dslFilePath: "examples/dsl/style_direct_llm.yaml",
    jsonText: "Run C1 to see compile payload.",
    budgetPercent: 0,
    budgetStage: "idle",
    metricValidation: "idle",
    metricValidationDelta: { text: "pending", tone: "neutral" },
    metricNodes: "-",
    metricEdges: "-",
    metricIssues: "0",
    compileSource: "no run yet",
    compileSummaryCells: [
      { key: "Status", value: "idle" },
      { key: "Mappings", value: "0" },
      { key: "Warnings", value: "0" },
      { key: "Errors", value: "0" },
    ],
    issues: [],
    bottleneckId: "waiting_for_run",
    bottleneckText: "Run C1 to detect compile bottlenecks and validation risks.",
    suggestions: [],
    exportMeta: "No payload available yet.",
    lastPayload: null,
    lastErrorPayload: null,
  });

  // Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: С‚РµРєСѓС‰Р°СЏ Р°РєС‚РёРІРЅР°СЏ capability, РІС‹С‡РёСЃР»СЏРµС‚СЃСЏ РёР· РєР°С‚Р°Р»РѕРіР°.
  const activeCapability = useMemo(
    () => state.capabilities.find((item) => item.id === state.activeCapabilityId) ?? FALLBACK_CAPABILITIES[0],
    [state.capabilities, state.activeCapabilityId],
  );

  // Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РїСЂРё СЃС‚Р°СЂС‚Рµ РїРѕРґС‚СЏРіРёРІР°РµРј capability-РєР°С‚Р°Р»РѕРі РѕС‚ backend.
  useEffect(() => {
    void (async () => {
      try {
        const catalog = await fetchCapabilityCatalog();
        setState((prev) => ({ ...prev, capabilities: catalog.capabilities }));
      } catch {
        // Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: fallback РѕСЃС‚Р°РµС‚СЃСЏ Р°РєС‚РёРІРЅС‹Рј, РїРѕСЌС‚РѕРјСѓ РѕС€РёР±РєСѓ РјРѕР¶РЅРѕ Р±РµР·РѕРїР°СЃРЅРѕ РёРіРЅРѕСЂРёСЂРѕРІР°С‚СЊ.
      }
    })();
  }, []);

  // Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РїРѕСЃР»Рµ РєР°Р¶РґРѕРіРѕ СЂРµРЅРґРµСЂР° РїРµСЂРµРёРЅРёС†РёР°Р»РёР·РёСЂСѓРµРј Lucide-РёРєРѕРЅРєРё.
  useEffect(() => {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  });

  // Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РѕР±СЂР°Р±РѕС‚С‡РёРє РїРµСЂРµРєР»СЋС‡РµРЅРёСЏ capability РІ Р»РµРІРѕРј РјРµРЅСЋ.
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
      const payload = await fetchStubCapability(capabilityId);
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson(payload),
        compileSummaryCells: [
          { key: "Status", value: "planned" },
          { key: "Mappings", value: "0" },
          { key: "Warnings", value: "0" },
          { key: "Errors", value: "0" },
        ],
        issues: [
          {
            severity: "warning",
            message: "Capability is in planned state. Real backend path will be unlocked in next slices.",
          },
        ],
        bottleneckId: "planned_capability",
        bottleneckText: "This capability is intentionally locked until its vertical slice is delivered.",
        suggestions: [
          {
            tag: "Roadmap",
            title: "Stay in C1 for real flow",
            detail: "Use DSL validate/compile run to verify backend + frontend integration now.",
          },
        ],
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: String(error) }),
      }));
    }
  }

  // Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РѕР±СЂР°Р±РѕС‚С‡РёРє Р·Р°РїСѓСЃРєР° СЂРµР°Р»СЊРЅРѕРіРѕ C1 validate+compile.
  async function handleRunC1(): Promise<void> {
    const dslFilePath = state.dslFilePath.trim();
    if (!dslFilePath) {
      setState((prev) => ({
        ...prev,
        jsonText: prettyJson({ status: "error", message: "DSL file path is required." }),
      }));
      return;
    }

    setState((prev) => ({
      ...prev,
      budgetPercent: 35,
      budgetStage: "running",
      metricValidation: "running",
      metricValidationDelta: { text: "in progress", tone: "neutral" },
      jsonText: "Running C1 validate + compile...",
      bottleneckId: "compile_in_progress",
      bottleneckText: "Backend is validating DSL and compiling Graph IR.",
      suggestions: [],
      lastPayload: null,
      lastErrorPayload: null,
    }));

    const result = await runC1ValidateCompile(dslFilePath);

    if (!result.ok) {
      const payload = result.payload;
      setState((prev) => ({
        ...prev,
        budgetPercent: 100,
        budgetStage: "failed",
        metricValidation: "failed",
        metricValidationDelta: { text: "error", tone: "negative" },
        metricNodes: "-",
        metricEdges: "-",
        metricIssues: "1",
        compileSource: dslFilePath,
        compileSummaryCells: [
          { key: "Status", value: "failure" },
          { key: "Mappings", value: "0" },
          { key: "Warnings", value: "0" },
          { key: "Errors", value: "1" },
        ],
        issues: [{ severity: "error", message: payload.message ?? "Unknown error" }],
        bottleneckId: "compile_failed",
        bottleneckText: "C1 call failed. Check DSL path and schema validity before retry.",
        suggestions: [
          {
            tag: "Path",
            title: "Verify DSL path",
            detail: "Ensure dsl_file points to an existing file inside repository.",
          },
          {
            tag: "Schema",
            title: "Fix schema violations",
            detail: "Open the error message and correct DSL fields before retry.",
          },
        ],
        jsonText: prettyJson(payload),
        exportMeta: "Error payload ready. Export can still be used for debugging.",
        lastErrorPayload: payload,
      }));
      return;
    }

    const payload = result.payload;
    const summary = payload.compile_summary;
    const graphSummary = payload.graph_ir_summary;

    setState((prev) => ({
      ...prev,
      budgetPercent: 100,
      budgetStage: "completed",
      metricValidation: summary.status,
      metricValidationDelta: { text: "pass", tone: "positive" },
      metricNodes: String(graphSummary.nodes_total ?? 0),
      metricEdges: String(graphSummary.edges_total ?? 0),
      metricIssues: String((summary.warnings ?? 0) + (summary.errors ?? 0)),
      compileSource: payload.dsl_file,
      compileSummaryCells: [
        { key: "Status", value: summary.status },
        { key: "Mappings", value: String(summary.node_mappings ?? 0) },
        { key: "Warnings", value: String(summary.warnings ?? 0) },
        { key: "Errors", value: String(summary.errors ?? 0) },
      ],
      issues: payload.compile_report.issues ?? [],
      bottleneckId:
        (payload.compile_report.issues ?? []).length > 0 ? "compile_issues_detected" : "no_compile_issues",
      bottleneckText:
        (payload.compile_report.issues ?? []).length > 0
          ? "Compilation succeeded but produced issues. Review warnings/errors before promotion."
          : "Compilation finished with zero issues. Candidate is ready for next slices.",
      suggestions:
        (payload.compile_report.issues ?? []).length > 0
          ? [
              {
                tag: "Quality",
                title: "Review warning contexts",
                detail:
                  "Inspect warning messages and decide whether to enforce stricter DSL conventions.",
              },
              {
                tag: "Next",
                title: "Prepare C2 run",
                detail: "After warning review, this candidate is ready for runtime tracing in the next slice.",
              },
            ]
          : [
              {
                tag: "Promotion",
                title: "Move to C2 runtime run",
                detail: "C1 checks are green. Next step is runtime execution and white-box tracing.",
              },
            ],
      jsonText: prettyJson(payload),
      exportMeta: "Payload ready. Click export to save current compile result.",
      lastPayload: payload,
      lastErrorPayload: null,
    }));
  }

  // Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: РѕР±СЂР°Р±РѕС‚С‡РёРє СЌРєСЃРїРѕСЂС‚Р° РїРѕСЃР»РµРґРЅРµРіРѕ payload РІ Р»РѕРєР°Р»СЊРЅС‹Р№ JSON С„Р°Р№Р».
  function handleExportPayload(): void {
    const payload = state.lastPayload ?? state.lastErrorPayload;
    if (!payload) {
      setState((prev) => ({ ...prev, jsonText: prettyJson({ status: "notice", message: "No payload to export yet." }) }));
      return;
    }

    const fileName = makeTimestampedFileName("c1_compile_payload");
    exportJsonToFile(payload, fileName);
    setState((prev) => ({ ...prev, exportMeta: `Saved: ${fileName}` }));
  }

  // Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: helper РґР»СЏ РёР·РјРµРЅРµРЅРёСЏ DSL РїСѓС‚Рё РІ input.
  function handleDslPathChange(nextValue: string): void {
    setState((prev) => ({ ...prev, dslFilePath: nextValue }));
  }

  // Р СѓСЃСЃРєРёР№ РєРѕРјРјРµРЅС‚Р°СЂРёР№: helper РґР»СЏ РјРіРЅРѕРІРµРЅРЅРѕРіРѕ РІРѕР·РІСЂР°С‚Р° Рє РєР°РЅРѕРЅРёС‡РµСЃРєРѕРјСѓ DSL РїСЂРёРјРµСЂСѓ.
  function handleFillExample(): void {
    setState((prev) => ({ ...prev, dslFilePath: "examples/dsl/style_direct_llm.yaml" }));
  }

  const isC1Enabled = activeCapability.id === "c1" && activeCapability.status === "enabled";

  return (
    <div className="app" id="app-root">
      <aside className="app-sidebar">
        <div className="app-sidebar-brand">
          <img src="/design_system/assets/logo-lockup.svg" alt="AutoAgent Optimizer" />
        </div>

        <div className="app-sidebar-section">
          <div className="app-side-label">Workspace</div>
          <button type="button" className="app-side-pick" id="workspace-pick">
            <span className="ws-dot" />
            <span>autoagent-optimizer</span>
            <i data-lucide="chevrons-up-down" />
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
            <span className="tb-crumb">Runs</span>
            <span className="tb-sep">/</span>
            <span className="tb-id">run_c1</span>
            <span className="tb-pill">{isC1Enabled ? "C1 enabled" : "planned capability"}</span>
          </div>

          <div className="tb-budget" id="budget-box">
            <div className="tb-budget-label">
              <i data-lucide="gauge" />
              <span>Compile budget</span>
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
            <button
              type="button"
              className="tb-btn tb-btn-ghost"
              onClick={() => {
                setState((prev) => ({
                  ...prev,
                  jsonText: prettyJson({ status: "notice", message: "Compare action is planned for C4 slice." }),
                }));
              }}
            >
              <i data-lucide="git-compare" />
              Compare
            </button>
            <button
              type="button"
              className="tb-btn tb-btn-primary"
              onClick={() => {
                setState((prev) => ({
                  ...prev,
                  jsonText: prettyJson({ status: "notice", message: "Promote action is planned for C6 slice." }),
                }));
              }}
            >
              Promote champion
            </button>
          </div>
        </header>

        <div className="app-content">
          <main className="app-center">
            <section className="content-head">
              <div>
                <h1 className="ch-title">
                  DSL/IR Studio <span>- C1 vertical slice</span>
                </h1>
                <p className="ch-sub">
                  {isC1Enabled
                    ? "Validate DSL, compile to Graph IR and inspect compile diagnostics."
                    : "Capability is visible in the product shell and will be unlocked by roadmap slices."}
                </p>
              </div>
              <div className="ch-actions">
                <span className="ch-pill">
                  <span className="dot" />
                  {state.activeCapabilityId.toUpperCase()} - {activeCapability.name}
                </span>
              </div>
            </section>

            <section className="metric-strip" id="metric-strip">
              <article className="ms-cell">
                <div className="ms-lbl">Validation</div>
                <div className="ms-row">
                  <div className="ms-val">{state.metricValidation}</div>
                  <span
                    className={`ms-delta${
                      state.metricValidationDelta.tone === "positive"
                        ? " pos"
                        : state.metricValidationDelta.tone === "negative"
                          ? " neg"
                          : ""
                    }`}
                  >
                    {state.metricValidationDelta.text}
                  </span>
                </div>
                <div className="ms-cap">Schema and graph integrity check</div>
              </article>

              <article className="ms-cell">
                <div className="ms-lbl">Graph nodes</div>
                <div className="ms-row">
                  <div className="ms-val">{state.metricNodes}</div>
                </div>
                <div className="ms-cap">IR nodes total</div>
              </article>

              <article className="ms-cell">
                <div className="ms-lbl">Graph edges</div>
                <div className="ms-row">
                  <div className="ms-val">{state.metricEdges}</div>
                </div>
                <div className="ms-cap">IR edges total</div>
              </article>

              <article className="ms-cell">
                <div className="ms-lbl">Issues</div>
                <div className="ms-row">
                  <div className="ms-val">{state.metricIssues}</div>
                </div>
                <div className="ms-cap">Warnings + errors</div>
              </article>
            </section>

            <section className="arch-list">
              <header className="arch-list-head">
                <div className="al-label">C1 run input</div>
                <div className="al-tools">
                  <button type="button" className="al-tool" onClick={handleFillExample} disabled={!isC1Enabled}>
                    <i data-lucide="wand-sparkles" />
                    Example
                  </button>
                </div>
              </header>
              <div className="c1-form-row">
                <label className="c1-field-label" htmlFor="dsl-file-input">
                  DSL file path
                </label>
                <div className="c1-form-controls">
                  <input
                    id="dsl-file-input"
                    type="text"
                    value={state.dslFilePath}
                    onChange={(event) => {
                      handleDslPathChange(event.target.value);
                    }}
                    disabled={!isC1Enabled}
                  />
                  <button type="button" className="tb-btn tb-btn-primary" onClick={() => void handleRunC1()} disabled={!isC1Enabled}>
                    Validate + compile
                  </button>
                </div>
                <p className="c1-hint">
                  Use relative path from repo root. Example: <code>examples/dsl/style_direct_llm.yaml</code>
                </p>
              </div>
            </section>

            <section className="trace-view">
              <header className="tv-head">
                <div className="tv-title">
                  <i data-lucide="workflow" />
                  <span>Compile report</span>
                  <span className="tv-arch">{state.compileSource}</span>
                </div>
              </header>
              <div className="tv-body">
                <div className="compile-summary-grid">
                  {state.compileSummaryCells.map((item) => (
                    <div className="summary-cell" key={item.key}>
                      <div className="summary-key">{item.key}</div>
                      <div className="summary-value">{item.value}</div>
                    </div>
                  ))}
                </div>

                <div className="issues-box">
                  {state.issues.length === 0 ? (
                    <div className="issue-row info">No issues detected for the current payload.</div>
                  ) : (
                    state.issues.map((issue, index) => (
                      <div key={`${issue.severity}-${index}`} className={`issue-row ${issue.severity}`}>
                        <b>{issue.severity.toUpperCase()}:</b> {issue.message}
                      </div>
                    ))
                  )}
                </div>

                <pre className="json-view">{state.jsonText}</pre>
              </div>
            </section>
          </main>

          <aside className="rail">
            <section className="rail-section">
              <div className="rail-label">Bottleneck found</div>
              <div className="rail-bottleneck">
                <div className="rb-top">
                  <div className="rb-icon">
                    <i data-lucide="triangle-alert" />
                  </div>
                  <div className="rb-id">{state.bottleneckId}</div>
                </div>
                <p className="rb-copy">{state.bottleneckText}</p>
              </div>
            </section>

            <section className="rail-section">
              <div className="rail-label">Suggested interventions</div>
              <div className="suggest">
                {state.suggestions.length === 0 ? (
                  <div className="sg-row">
                    <div>
                      <div className="sg-tag">Idle</div>
                      <div className="sg-title">No interventions yet</div>
                      <div className="sg-sub">Run C1 to generate actionable guidance.</div>
                    </div>
                    <button type="button" className="sg-apply" disabled>
                      Apply
                    </button>
                  </div>
                ) : (
                  state.suggestions.map((item, index) => (
                    <div className="sg-row" key={`${item.tag}-${index}`}>
                      <div>
                        <div className="sg-tag">{item.tag}</div>
                        <div className="sg-title">{item.title}</div>
                        <div className="sg-sub">{item.detail}</div>
                      </div>
                      <button type="button" className="sg-apply" disabled>
                        Apply
                      </button>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="rail-section">
              <div className="rail-label">Export</div>
              <button type="button" className="rail-export" onClick={handleExportPayload}>
                <i data-lucide="file-json-2" />
                Export compile payload
              </button>
              <div className="rail-export-meta">{state.exportMeta}</div>
            </section>
          </aside>
        </div>
      </div>
    </div>
  );
}
