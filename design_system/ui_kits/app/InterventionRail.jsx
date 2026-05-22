/* global React */
const { useEffect: useEffectIR } = React;

function InterventionRail() {
  useEffectIR(() => { if (window.lucide) window.lucide.createIcons(); });
  return (
    <aside className="rail">
      <div className="rail-section">
        <div className="rail-label">Bottleneck found</div>
        <div className="rail-bottleneck">
          <div className="rb-top">
            <div className="rb-icon"><i data-lucide="alert-triangle"></i></div>
            <span className="rb-id">judge.f1</span>
          </div>
          <p className="rb-copy">
            Judge disagrees with itself on <b>14 / 480</b> cases (κ = 0.71). Drives <b>+0.18 s</b> p95 and <b>3 / 6</b> false regressions in the matrix.
          </p>
          <div className="rb-evidence">
            <span className="mono">evidence:</span>
            <a>disagreement matrix</a>
            <a>14 borderline cases</a>
          </div>
        </div>
      </div>

      <div className="rail-section">
        <div className="rail-label">Suggested interventions</div>
        <div className="suggest">
          <div className="sg-row" data-tint="indigo">
            <div>
              <span className="sg-tag">Deterministic</span>
              <div className="sg-title">Move arithmetic out of LLM</div>
              <div className="sg-sub">Drop a <code>tool.calc</code> contract before <code>llm.answer</code>. Est. <b>−$0.04</b> per case.</div>
            </div>
            <button className="sg-apply">Apply</button>
          </div>
          <div className="sg-row" data-tint="amber">
            <div>
              <span className="sg-tag">HITL gate</span>
              <div className="sg-title">Route borderline cases to a reviewer</div>
              <div className="sg-sub">Send the 14 disagreement cases to a human. Est. <b>+0.04 f1</b>, <b>+12 m</b> human time.</div>
            </div>
            <button className="sg-apply">Apply</button>
          </div>
          <div className="sg-row" data-tint="green">
            <div>
              <span className="sg-tag">Component</span>
              <div className="sg-title">Swap cross-encoder reranker</div>
              <div className="sg-sub">Try <code>bge-reranker-large</code>. Est. <b>+0.02 f1</b>, <b>+0.09 s</b> p95.</div>
            </div>
            <button className="sg-apply">Apply</button>
          </div>
        </div>
      </div>

      <div className="rail-section">
        <div className="rail-label">Export</div>
        <button className="rail-export">
          <i data-lucide="file-check-2"></i>
          <span>Export evidence bundle</span>
          <span className="kbd">⌘ E</span>
        </button>
        <div className="rail-export-meta">
          Champion · regression matrix · 24 traces · signed manifest
        </div>
      </div>
    </aside>
  );
}
window.InterventionRail = InterventionRail;
