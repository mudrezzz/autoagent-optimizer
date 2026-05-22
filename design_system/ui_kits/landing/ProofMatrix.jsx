/* global React */
function ProofMatrix() {
  const rows = [
    { id: "arch_001", name: "Single-shot",         f1: "0.804", cost: "$0.49", p95: "0.92 s", status: "baseline" },
    { id: "arch_07a", name: "Plan + act",          f1: "0.811", cost: "$0.62", p95: "1.41 s", status: "fail",     reason: "tool.calc 12 fails" },
    { id: "arch_1c2", name: "RAG · single",         f1: "0.823", cost: "$0.44", p95: "1.05 s", status: "pass" },
    { id: "arch_b4f", name: "RAG · rerank · HyDE", f1: "0.842", cost: "$0.31", p95: "1.24 s", status: "champion",  reason: "Promoted" },
    { id: "arch_2e8", name: "Ensemble · judge",     f1: "0.838", cost: "$1.02", p95: "2.18 s", status: "warn",     reason: "budget exceeded" },
    { id: "arch_3c1", name: "HITL · gate",          f1: "0.851", cost: "$0.36", p95: "+ 14 m", status: "warn",     reason: "human in loop" },
  ];

  return (
    <section className="lp-proof" id="proof">
      <div className="lp-section-head">
        <span className="lp-eyebrow"><span className="ey-dot"></span>The receipts</span>
        <h2 className="lp-h2">Every architecture, side-by-side.</h2>
        <p className="lp-section-sub">
          From a single run on the customer-support QA suite (n = 480 cases, judge:&nbsp;
          <code>gpt-4o-mini</code>, budget&nbsp;<code>cost ≤ $0.40 / case</code>).
        </p>
      </div>

      <div className="lp-table-wrap">
        <div className="lp-table">
          <div className="lp-table-head">
            <div>Arch</div><div>Name</div><div>f1@k</div><div>Cost</div><div>p95</div><div>Status</div>
          </div>
          {rows.map(r => (
            <div className={`lp-table-row r-${r.status}`} key={r.id}>
              <div className="mono mono-id">{r.id}</div>
              <div className="row-name">{r.name}</div>
              <div className="mono">{r.f1}</div>
              <div className="mono">{r.cost}</div>
              <div className="mono">{r.p95}</div>
              <div className="row-status">
                <span className={`pill p-${r.status}`}>
                  <span className="dot"></span>{capitalize(r.status)}
                </span>
                {r.reason && <span className="reason">{r.reason}</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="lp-proof-foot">
        <div className="pf-item">
          <div className="pf-num">100 %</div>
          <div className="pf-cap">white-box trace coverage</div>
        </div>
        <div className="pf-item">
          <div className="pf-num">24</div>
          <div className="pf-cap">candidate architectures bracketed</div>
        </div>
        <div className="pf-item">
          <div className="pf-num">$24.80</div>
          <div className="pf-cap">total spend to find the champion</div>
        </div>
      </div>
    </section>
  );
}

function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

window.ProofMatrix = ProofMatrix;
