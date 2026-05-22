// Русский комментарий: C1 vertical slice frontend-логика в каркасе app-v3.
(function () {
  "use strict";

  // Русский комментарий: fallback-каталог capability, если API временно недоступен.
  const FALLBACK_CAPABILITIES = [
    { id: "c1", name: "DSL/IR Studio", description: "Validate DSL and compile Graph IR.", status: "enabled", badge_count: 1 },
    { id: "c2", name: "Runtime Run", description: "Workflow execution and trace.", status: "planned", badge_count: 0 },
    { id: "c3", name: "Evaluation Profile", description: "Profile-based evaluation.", status: "planned", badge_count: 0 },
    { id: "c4", name: "Arena Ranking", description: "Compare candidates.", status: "planned", badge_count: 0 },
    { id: "c5", name: "Evidence & Diagnostics", description: "Comparative and diagnostics layers.", status: "planned", badge_count: 0 },
    { id: "c6", name: "Champion Bundle", description: "Champion export and parity.", status: "planned", badge_count: 0 }
  ];

  // Русский комментарий: иконки capability для левой навигации.
  const CAPABILITY_ICONS = {
    c1: "file-check-2",
    c2: "play-circle",
    c3: "list-checks",
    c4: "trophy",
    c5: "activity",
    c6: "package-check"
  };

  // Русский комментарий: централизованное состояние workbench-страницы.
  const state = {
    capabilities: FALLBACK_CAPABILITIES,
    activeCapabilityId: "c1",
    activeCapabilityStatus: "enabled",
    lastPayload: null,
    lastRequestPath: "examples/dsl/style_direct_llm.yaml",
    lastRunAtUtc: null,
    lastError: null
  };

  // Русский комментарий: DOM-узлы для переиспользования во всех рендерах.
  const dom = {
    capabilityNav: document.getElementById("capability-nav"),
    runPill: document.getElementById("run-pill"),
    activeCapabilityLabel: document.getElementById("active-capability-label"),
    subtitle: document.getElementById("content-subtitle"),
    validation: document.getElementById("metric-validation"),
    validationDelta: document.getElementById("metric-validation-delta"),
    nodes: document.getElementById("metric-nodes"),
    edges: document.getElementById("metric-edges"),
    issues: document.getElementById("metric-issues"),
    source: document.getElementById("compile-source"),
    summaryGrid: document.getElementById("compile-summary-grid"),
    issuesBox: document.getElementById("issues-box"),
    jsonView: document.getElementById("compile-json"),
    bottleneckId: document.getElementById("bottleneck-id"),
    bottleneckCopy: document.getElementById("bottleneck-copy"),
    suggestionsBox: document.getElementById("suggestions-box"),
    dslInput: document.getElementById("dsl-file-input"),
    runButton: document.getElementById("c1-run-btn"),
    fillExampleButton: document.getElementById("fill-example-btn"),
    exportButton: document.getElementById("export-btn"),
    exportMeta: document.getElementById("export-meta"),
    compareButton: document.getElementById("compare-btn"),
    promoteButton: document.getElementById("promote-btn"),
    budgetFill: document.getElementById("budget-fill"),
    budgetValue: document.getElementById("budget-value"),
    budgetSub: document.getElementById("budget-sub")
  };

  // Русский комментарий: точка входа страницы, связывает события и загружает capability-каталог.
  async function initApp() {
    bindStaticActions();
    await loadCapabilities();
    renderCapabilityNav();
    renderCapabilityState();
    renderReportSummary(null);
    renderIssues([]);
    renderSuggestions([]);
    refreshIcons();
  }

  // Русский комментарий: навешивает обработчики статичных кнопок интерфейса.
  function bindStaticActions() {
    dom.runButton.addEventListener("click", runC1ValidationCompile);
    dom.fillExampleButton.addEventListener("click", fillC1Example);
    dom.exportButton.addEventListener("click", exportLastPayload);

    dom.compareButton.addEventListener("click", function () {
      showUiNotice("Compare action is planned for C4 slice.");
    });

    dom.promoteButton.addEventListener("click", function () {
      showUiNotice("Promote action is planned for C6 slice.");
    });
  }

  // Русский комментарий: загружает capability-каталог с backend и обновляет локальное состояние.
  async function loadCapabilities() {
    try {
      const response = await fetch("/api/capabilities");
      if (!response.ok) {
        return;
      }
      const payload = await response.json();
      if (!payload || !Array.isArray(payload.capabilities)) {
        return;
      }
      state.capabilities = payload.capabilities;
      const c1 = state.capabilities.find(function (item) { return item.id === "c1"; });
      if (c1 && typeof c1.status === "string") {
        state.activeCapabilityStatus = c1.status;
      }
    } catch (_error) {
      // Русский комментарий: fallback уже установлен, поэтому сетевую ошибку безопасно игнорируем.
    }
  }

  // Русский комментарий: рисует левую capability-навигацию в стиле app-v3.
  function renderCapabilityNav() {
    dom.capabilityNav.innerHTML = "";
    state.capabilities.forEach(function (capability) {
      const button = document.createElement("button");
      const iconName = CAPABILITY_ICONS[capability.id] || "circle";
      const status = String(capability.status || "planned");
      const badgeCount = Number(capability.badge_count || 0);
      button.type = "button";
      button.className = "cap-link" +
        (capability.id === state.activeCapabilityId ? " active" : "") +
        (status === "planned" ? " disabled" : "");
      button.innerHTML = "" +
        '<i data-lucide="' + escapeHtml(iconName) + '" class="cap-icon"></i>' +
        '<span class="cap-name">' + escapeHtml(capability.name) + "</span>" +
        '<span class="cap-badge ' + escapeHtml(status) + '">' +
        (status === "enabled" ? "live" : "planned") + (badgeCount > 0 ? " " + badgeCount : "") +
        "</span>";
      button.addEventListener("click", function () {
        switchCapability(capability.id);
      });
      dom.capabilityNav.appendChild(button);
    });
  }

  // Русский комментарий: переключает capability и обновляет центральный контент без смены каркаса.
  function switchCapability(capabilityId) {
    state.activeCapabilityId = capabilityId;
    const capability = state.capabilities.find(function (item) { return item.id === capabilityId; });
    state.activeCapabilityStatus = capability && capability.status ? capability.status : "planned";
    state.lastError = null;

    renderCapabilityNav();
    renderCapabilityState();

    if (capabilityId !== "c1") {
      loadStubForCapability(capabilityId);
    } else {
      renderReportSummary(state.lastPayload);
      renderIssues(extractIssuesFromPayload(state.lastPayload));
      renderSuggestions(buildSuggestions(state.lastPayload, state.lastError));
    }

    refreshIcons();
  }

  // Русский комментарий: подтягивает stub-payload для planned capability и отображает его в workbench-зоне.
  async function loadStubForCapability(capabilityId) {
    setBudgetProgress(10, "planned");
    dom.jsonView.textContent = "Loading planned capability preview...";
    try {
      const response = await fetch("/api/" + capabilityId + "/sample");
      const payload = await response.json();
      dom.jsonView.textContent = prettyJson(payload);
      renderReportSummary(null);
      renderIssues([{ severity: "info", message: "Capability is in planned state. Real backend path will be unlocked in next slices." }]);
      renderBottleneck("planned_capability", "This capability is intentionally locked until its vertical slice is delivered.");
      renderSuggestions([
        {
          title: "Stay in C1 for real flow",
          detail: "Use DSL validate/compile run to verify backend + frontend integration now.",
          tag: "Roadmap",
          actionable: false
        }
      ]);
    } catch (error) {
      dom.jsonView.textContent = prettyJson({ status: "error", message: String(error) });
    }
  }

  // Русский комментарий: обновляет заголовки и доступность элементов в зависимости от активной capability.
  function renderCapabilityState() {
    const capability = state.capabilities.find(function (item) { return item.id === state.activeCapabilityId; });
    const name = capability ? capability.name : "Unknown";
    const status = capability && capability.status ? capability.status : "planned";

    dom.activeCapabilityLabel.textContent = state.activeCapabilityId.toUpperCase() + " - " + name;
    dom.runPill.textContent = status === "enabled" ? "C1 enabled" : "planned capability";
    dom.subtitle.textContent = status === "enabled"
      ? "Validate DSL, compile to Graph IR and inspect compile diagnostics."
      : "Capability is visible in the product shell and will be unlocked by roadmap slices.";

    const c1Enabled = state.activeCapabilityId === "c1" && status === "enabled";
    dom.runButton.disabled = !c1Enabled;
    dom.dslInput.disabled = !c1Enabled;
    dom.fillExampleButton.disabled = !c1Enabled;
  }

  // Русский комментарий: заполняет поле DSL-пути эталонным примером для быстрого запуска.
  function fillC1Example() {
    dom.dslInput.value = "examples/dsl/style_direct_llm.yaml";
  }

  // Русский комментарий: выполняет реальный C1 вызов `/api/c1/validate-compile` и рендерит результат.
  async function runC1ValidationCompile() {
    if (state.activeCapabilityId !== "c1") {
      return;
    }

    const dslFile = String(dom.dslInput.value || "").trim();
    if (!dslFile) {
      renderErrorPayload({ status: "error", message: "DSL file path is required." });
      return;
    }

    state.lastRequestPath = dslFile;
    state.lastError = null;
    state.lastPayload = null;

    setBudgetProgress(35, "running");
    dom.validation.textContent = "running";
    dom.validationDelta.className = "ms-delta";
    dom.validationDelta.textContent = "in progress";
    dom.jsonView.textContent = "Running C1 validate + compile...";
    renderBottleneck("compile_in_progress", "Backend is validating DSL and compiling Graph IR.");
    renderSuggestions([]);

    try {
      const response = await fetch("/api/c1/validate-compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dsl_file: dslFile })
      });
      const payload = await response.json();

      if (!response.ok) {
        renderErrorPayload(payload);
        return;
      }

      state.lastPayload = payload;
      state.lastRunAtUtc = new Date().toISOString();
      setBudgetProgress(100, "completed");
      renderSuccessPayload(payload);
    } catch (error) {
      renderErrorPayload({ status: "error", message: String(error) });
    }
  }

  // Русский комментарий: отображает успешный результат C1-компиляции в метриках, диагностике и JSON.
  function renderSuccessPayload(payload) {
    const compileSummary = payload && payload.compile_summary ? payload.compile_summary : {};
    const graphSummary = payload && payload.graph_ir_summary ? payload.graph_ir_summary : {};
    const issues = extractIssuesFromPayload(payload);

    dom.validation.textContent = String(compileSummary.status || "success");
    dom.validationDelta.className = "ms-delta pos";
    dom.validationDelta.textContent = "pass";
    dom.nodes.textContent = String(graphSummary.nodes_total || "0");
    dom.edges.textContent = String(graphSummary.edges_total || "0");
    dom.issues.textContent = String((Number(compileSummary.warnings || 0) + Number(compileSummary.errors || 0)));

    dom.source.textContent = String(payload.dsl_file || state.lastRequestPath);
    dom.jsonView.textContent = prettyJson(payload);
    renderReportSummary(payload);
    renderIssues(issues);

    if (issues.length > 0) {
      renderBottleneck("compile_issues_detected", "Compilation succeeded but produced issues. Review warnings/errors before promotion.");
    } else {
      renderBottleneck("no_compile_issues", "Compilation finished with zero issues. Candidate is ready for next slices.");
    }

    renderSuggestions(buildSuggestions(payload, null));
    dom.exportMeta.textContent = "Payload ready. Click export to save current compile result.";
  }

  // Русский комментарий: отображает ошибочный C1-результат и диагностические подсказки для исправления.
  function renderErrorPayload(payload) {
    state.lastError = payload;
    setBudgetProgress(100, "failed");

    dom.validation.textContent = "failed";
    dom.validationDelta.className = "ms-delta neg";
    dom.validationDelta.textContent = "error";
    dom.nodes.textContent = "-";
    dom.edges.textContent = "-";
    dom.issues.textContent = "1";

    dom.source.textContent = state.lastRequestPath;
    dom.jsonView.textContent = prettyJson(payload);
    renderReportSummary(null);
    renderIssues([{ severity: "error", message: String(payload && payload.message ? payload.message : "Unknown error") }]);
    renderBottleneck("compile_failed", "C1 call failed. Check DSL path and schema validity before retry.");
    renderSuggestions(buildSuggestions(null, payload));
    dom.exportMeta.textContent = "Error payload ready. Export can still be used for debugging.";
  }

  // Русский комментарий: формирует компактный summary-блок из compile payload.
  function renderReportSummary(payload) {
    if (!payload || !payload.compile_summary) {
      dom.summaryGrid.innerHTML = "" +
        '<div class="summary-cell"><div class="summary-key">Status</div><div class="summary-value">idle</div></div>' +
        '<div class="summary-cell"><div class="summary-key">Mappings</div><div class="summary-value">0</div></div>' +
        '<div class="summary-cell"><div class="summary-key">Warnings</div><div class="summary-value">0</div></div>' +
        '<div class="summary-cell"><div class="summary-key">Errors</div><div class="summary-value">0</div></div>';
      return;
    }

    const summary = payload.compile_summary;
    dom.summaryGrid.innerHTML = "" +
      '<div class="summary-cell"><div class="summary-key">Status</div><div class="summary-value">' + escapeHtml(String(summary.status || "unknown")) + "</div></div>" +
      '<div class="summary-cell"><div class="summary-key">Mappings</div><div class="summary-value">' + escapeHtml(String(summary.node_mappings || 0)) + "</div></div>" +
      '<div class="summary-cell"><div class="summary-key">Warnings</div><div class="summary-value">' + escapeHtml(String(summary.warnings || 0)) + "</div></div>" +
      '<div class="summary-cell"><div class="summary-key">Errors</div><div class="summary-value">' + escapeHtml(String(summary.errors || 0)) + "</div></div>";
  }

  // Русский комментарий: отрисовывает список compile-issues с цветовой семантикой severity.
  function renderIssues(issues) {
    if (!Array.isArray(issues) || issues.length === 0) {
      dom.issuesBox.innerHTML = '<div class="issue-row info">No issues detected for the current payload.</div>';
      return;
    }

    dom.issuesBox.innerHTML = issues.map(function (item) {
      const severity = item && item.severity ? String(item.severity) : "info";
      const message = item && item.message ? String(item.message) : "Unknown issue";
      return '<div class="issue-row ' + escapeHtml(severity) + '"><b>' + escapeHtml(severity.toUpperCase()) + ':</b> ' + escapeHtml(message) + "</div>";
    }).join("");
  }

  // Русский комментарий: извлекает compile issues из payload в унифицированном формате для UI.
  function extractIssuesFromPayload(payload) {
    if (!payload || !payload.compile_report || !Array.isArray(payload.compile_report.issues)) {
      return [];
    }
    return payload.compile_report.issues.map(function (item) {
      return {
        severity: item && item.severity ? String(item.severity) : "info",
        message: item && item.message ? String(item.message) : "Unknown issue"
      };
    });
  }

  // Русский комментарий: обновляет правую панель bottleneck в зависимости от текущего шага run.
  function renderBottleneck(id, text) {
    dom.bottleneckId.textContent = id;
    dom.bottleneckCopy.textContent = text;
  }

  // Русский комментарий: строит список рекомендаций для intervention rail.
  function buildSuggestions(payload, errorPayload) {
    if (errorPayload) {
      return [
        {
          title: "Verify DSL path",
          detail: "Ensure `dsl_file` points to an existing file inside repository.",
          tag: "Path",
          actionable: false
        },
        {
          title: "Fix schema violations",
          detail: "Open the error message and correct DSL fields before retry.",
          tag: "Schema",
          actionable: false
        }
      ];
    }

    if (!payload || !payload.compile_summary) {
      return [];
    }

    const warnings = Number(payload.compile_summary.warnings || 0);
    const errors = Number(payload.compile_summary.errors || 0);

    if (errors > 0) {
      return [
        {
          title: "Resolve compile errors",
          detail: "Errors must be fixed before this candidate can move to C2 runtime run.",
          tag: "Compiler",
          actionable: false
        }
      ];
    }

    if (warnings > 0) {
      return [
        {
          title: "Review warning contexts",
          detail: "Inspect warning messages and decide whether to enforce stricter DSL conventions.",
          tag: "Quality",
          actionable: false
        },
        {
          title: "Prepare C2 run",
          detail: "After warning review, this candidate is ready for runtime tracing in the next slice.",
          tag: "Next",
          actionable: false
        }
      ];
    }

    return [
      {
        title: "Move to C2 runtime run",
        detail: "C1 checks are green. Next step is runtime execution and white-box tracing.",
        tag: "Promotion",
        actionable: false
      }
    ];
  }

  // Русский комментарий: рендерит intervention-карточки в правом rail.
  function renderSuggestions(suggestions) {
    if (!Array.isArray(suggestions) || suggestions.length === 0) {
      dom.suggestionsBox.innerHTML = '<div class="sg-row"><div><div class="sg-tag">Idle</div><div class="sg-title">No interventions yet</div><div class="sg-sub">Run C1 to generate actionable guidance.</div></div><button type="button" class="sg-apply" disabled>Apply</button></div>';
      return;
    }

    dom.suggestionsBox.innerHTML = suggestions.map(function (item) {
      const tag = item && item.tag ? String(item.tag) : "Hint";
      const title = item && item.title ? String(item.title) : "Suggestion";
      const detail = item && item.detail ? String(item.detail) : "";
      const disabledAttr = item && item.actionable ? "" : " disabled";
      return "" +
        '<div class="sg-row">' +
        '<div>' +
        '<div class="sg-tag">' + escapeHtml(tag) + "</div>" +
        '<div class="sg-title">' + escapeHtml(title) + "</div>" +
        '<div class="sg-sub">' + escapeHtml(detail) + "</div>" +
        "</div>" +
        '<button type="button" class="sg-apply"' + disabledAttr + ">Apply</button>" +
        "</div>";
    }).join("");
  }

  // Русский комментарий: обновляет визуальный прогресс бюджетной полосы в верхнем баре.
  function setBudgetProgress(percent, stage) {
    const normalized = Math.max(0, Math.min(100, Number(percent || 0)));
    dom.budgetFill.style.width = String(normalized) + "%";
    dom.budgetValue.textContent = String(Math.round(normalized)) + "%";
    dom.budgetSub.textContent = String(stage || "idle");
  }

  // Русский комментарий: экспортирует текущий payload в JSON-файл для локального разбора.
  function exportLastPayload() {
    const payload = state.lastPayload || state.lastError;
    if (!payload) {
      showUiNotice("No payload to export yet.");
      return;
    }

    const fileName = "c1_compile_payload_" + new Date().toISOString().replace(/[.:]/g, "-") + ".json";
    const blob = new Blob([prettyJson(payload)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);

    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = fileName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);

    dom.exportMeta.textContent = "Saved: " + fileName;
  }

  // Русский комментарий: выводит техническое уведомление в JSON-панель без изменения бизнес-состояния.
  function showUiNotice(message) {
    dom.jsonView.textContent = prettyJson({ status: "notice", message: String(message) });
  }

  // Русский комментарий: безопасный JSON pretty-print для диагностических панелей.
  function prettyJson(value) {
    return JSON.stringify(value, null, 2);
  }

  // Русский комментарий: экранирует HTML-спецсимволы при рендере текстовых фрагментов.
  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  // Русский комментарий: переинициализирует Lucide-иконки после динамического рендера HTML.
  function refreshIcons() {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  }

  initApp();
})();
