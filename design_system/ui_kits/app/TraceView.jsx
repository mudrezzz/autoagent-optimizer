/* global React */
const { useState: useStateTV, useEffect: useEffectTV } = React;

function TraceView({ archId }) {
  useEffectTV(() => { if (window.lucide) window.lucide.createIcons(); });
  const [caseIdx, setCaseIdx] = useStateTV(14);

  const spans = [
    { name: "retriever.bm25",    kind: "retrieval", x: 0,   w: 14, ms: "178 ms" },
    { name: "retriever.dense",   kind: "retrieval", x: 14,  w: 18, ms: "221 ms" },
    { name: "reranker.cross",    kind: "llm",       x: 32,  w: 24, ms: "298 ms" },
    { name: "tool.calc",         kind: "tool",      x: 56,  w: 5,  ms: "62 ms"  },
    { name: "llm.answer",        kind: "llm",       x: 61,  w: 30, ms: "372 ms" },
    { name: "hitl.review",       kind: "hitl",      x: 91,  w: 6,  ms: "72 ms"  },
    { name: "judge.f1",          kind: "fail",      x: 97,  w: 3,  ms: "41 ms"  },
  ];

  return (
    <div className="trace-view">
      <div className="tv-head">
        <div className="tv-title">
          <i data-lucide="activity"></i>
          <span>White-box trace</span>
          <span className="tv-arch mono">{archId}</span>
        </div>
        <div className="tv-case">
          <button className="tv-step" onClick={() => setCaseIdx(c => Math.max(1, c-1))}><i data-lucide="chevron-left"></i></button>
          <span className="mono">case {caseIdx} / 24</span>
          <button className="tv-step" onClick={() => setCaseIdx(c => Math.min(24, c+1))}><i data-lucide="chevron-right"></i></button>
        </div>
      </div>

      <div className="tv-body">
        <div className="tv-rows">
          {spans.map((s, i) => (
            <div className="tv-row" key={i}>
              <div className={`tv-label ${s.kind === 'fail' ? 'fail' : ''}`}>{s.name}</div>
              <div className="tv-track">
                <div className={`tv-span k-${s.kind}`} style={{left: s.x + '%', width: s.w + '%'}}></div>
              </div>
              <div className="tv-ms">{s.ms}</div>
            </div>
          ))}
        </div>
        <div className="tv-axis">
          <span></span>
          <div className="tv-ticks">
            <span>0</span><span>250 ms</span><span>500</span><span>750</span><span>1.0 s</span><span>1.24</span>
          </div>
          <span></span>
        </div>
      </div>

      <div className="tv-legend">
        <span><span className="lg-sw k-retrieval"></span>retrieval</span>
        <span><span className="lg-sw k-llm"></span>llm</span>
        <span><span className="lg-sw k-tool"></span>tool</span>
        <span><span className="lg-sw k-hitl"></span>hitl</span>
        <span><span className="lg-sw k-fail"></span>regression</span>
      </div>
    </div>
  );
}
window.TraceView = TraceView;
