// Русский комментарий: capability shell frontend для V2.1.S1.
(function () {
  "use strict";

  // Русский комментарий: канонический список capability для отображения вкладок.
  const CAPABILITIES = [
    { id: "c1", name: "DSL/IR Studio", description: "Валидация DSL и compile report в Graph IR." },
    { id: "c2", name: "Runtime Run", description: "Запуск workflow и просмотр white-box trace." },
    { id: "c3", name: "Evaluation Profile", description: "Profile-runner для dsl/native target." },
    { id: "c4", name: "Arena Ranking", description: "Сравнение кандидатов, ranking и winner." },
    { id: "c5", name: "Evidence & Diagnostics", description: "Comparative и diagnostic слои анализа." },
    { id: "c6", name: "Champion Bundle", description: "Native-first экспорт и parity артефакты." }
  ];

  // Русский комментарий: общее состояние интерфейса и текущей capability.
  const state = {
    activeCapabilityId: "c1",
    mode: "idle",
    payload: null,
    error: null
  };

  // Русский комментарий: кэш DOM-узлов для переиспользования при ререндере.
  const elements = {
    tabs: document.getElementById("capability-tabs"),
    header: document.getElementById("capability-header"),
    content: document.getElementById("capability-content")
  };

  // Русский комментарий: инициализация приложения и первичный рендер.
  function initApp() {
    renderTabs();
    renderActiveCapability();
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  }

  // Русский комментарий: рисует список вкладок capability в sidebar.
  function renderTabs() {
    elements.tabs.innerHTML = "";
    CAPABILITIES.forEach((capability) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `capability-tab${capability.id === state.activeCapabilityId ? " active" : ""}`;
      button.textContent = `${capability.id.toUpperCase()} · ${capability.name}`;
      button.addEventListener("click", () => switchCapability(capability.id));
      elements.tabs.appendChild(button);
    });
  }

  // Русский комментарий: переключает активную capability и сбрасывает state-box.
  function switchCapability(capabilityId) {
    state.activeCapabilityId = capabilityId;
    state.mode = "idle";
    state.payload = null;
    state.error = null;
    renderTabs();
    renderActiveCapability();
  }

  // Русский комментарий: отображает текущую capability (заголовок + контент).
  function renderActiveCapability() {
    const capability = CAPABILITIES.find((item) => item.id === state.activeCapabilityId);
    if (!capability) {
      return;
    }

    elements.header.innerHTML = `
      <h2>${escapeHtml(capability.name)}</h2>
      <p>${escapeHtml(capability.description)}</p>
    `;

    if (capability.id === "c1") {
      renderCapabilityC1();
      return;
    }
    renderStubCapability(capability.id);
  }

  // Русский комментарий: рендер C1 с реальным вызовом backend endpoint `/api/c1/validate-compile`.
  function renderCapabilityC1() {
    elements.content.innerHTML = `
      <div class="state-strip">
        <button type="button" class="state-btn" data-mode="idle">Idle</button>
        <button type="button" class="state-btn" data-mode="loading">Loading</button>
        <button type="button" class="state-btn" data-mode="error">Error</button>
      </div>
      <div class="state-box">
        <p class="state-line">Run real C1 backend call with DSL file path.</p>
        <div class="form-grid">
          <input id="c1-dsl-file" value="examples/dsl/style_direct_llm.yaml" />
          <button type="button" id="c1-run-btn" class="btn-primary">Validate and compile</button>
        </div>
        <pre id="c1-output" class="json-view">State: idle</pre>
      </div>
    `;

    const runButton = document.getElementById("c1-run-btn");
    const dslFileInput = document.getElementById("c1-dsl-file");
    const output = document.getElementById("c1-output");
    attachStateButtons(output);

    runButton.addEventListener("click", async () => {
      state.mode = "loading";
      output.textContent = "State: loading";
      try {
        const response = await fetch("/api/c1/validate-compile", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dsl_file: dslFileInput.value.trim() })
        });
        const payload = await response.json();
        if (!response.ok) {
          state.mode = "error";
          state.error = payload;
          output.innerHTML = `<span class="state-error">State: error</span>\n${prettyJson(payload)}`;
          return;
        }
        state.mode = "success";
        state.payload = payload;
        output.textContent = `State: success\n${prettyJson(payload)}`;
      } catch (error) {
        state.mode = "error";
        state.error = { message: String(error) };
        output.innerHTML = `<span class="state-error">State: error</span>\n${prettyJson(state.error)}`;
      }
    });
  }

  // Русский комментарий: рендер остальных capability через stub-endpoints для success-state.
  function renderStubCapability(capabilityId) {
    elements.content.innerHTML = `
      <div class="state-strip">
        <button type="button" class="state-btn" data-mode="idle">Idle</button>
        <button type="button" class="state-btn" data-mode="loading">Loading</button>
        <button type="button" class="state-btn" data-mode="error">Error</button>
      </div>
      <div class="state-box">
        <p class="state-line">Stub endpoint for ${escapeHtml(capabilityId.toUpperCase())}.</p>
        <button type="button" id="stub-run-btn" class="btn-primary">Load sample payload</button>
        <pre id="stub-output" class="json-view">State: idle</pre>
      </div>
    `;

    const runButton = document.getElementById("stub-run-btn");
    const output = document.getElementById("stub-output");
    attachStateButtons(output);

    runButton.addEventListener("click", async () => {
      state.mode = "loading";
      output.textContent = "State: loading";
      try {
        const response = await fetch(`/api/${capabilityId}/sample`);
        const payload = await response.json();
        if (!response.ok) {
          state.mode = "error";
          state.error = payload;
          output.innerHTML = `<span class="state-error">State: error</span>\n${prettyJson(payload)}`;
          return;
        }
        state.mode = "success";
        state.payload = payload;
        output.textContent = `State: success\n${prettyJson(payload)}`;
      } catch (error) {
        state.mode = "error";
        state.error = { message: String(error) };
        output.innerHTML = `<span class="state-error">State: error</span>\n${prettyJson(state.error)}`;
      }
    });
  }

  // Русский комментарий: подключает управляющие кнопки режимов `idle/loading/error` для демонстрации UI-state.
  function attachStateButtons(outputElement) {
    const buttons = elements.content.querySelectorAll(".state-btn");
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const mode = button.getAttribute("data-mode") || "idle";
        if (mode === "idle") {
          outputElement.textContent = "State: idle";
          return;
        }
        if (mode === "loading") {
          outputElement.textContent = "State: loading";
          return;
        }
        outputElement.innerHTML = `<span class="state-error">State: error</span>\n${prettyJson({ message: "Manual error state sample." })}`;
      });
    });
  }

  // Русский комментарий: безопасный рендер JSON payload в читаемом виде.
  function prettyJson(value) {
    return JSON.stringify(value, null, 2);
  }

  // Русский комментарий: экранирование HTML в текстовых полях заголовков.
  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  initApp();
})();

