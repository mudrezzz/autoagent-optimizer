/* global React */
function MetricStrip({ metrics }) {
  return (
    <div className="metric-strip">
      {metrics.map((m, i) => (
        <div className="ms-cell" key={i}>
          <div className="ms-lbl">{m.label}</div>
          <div className="ms-row">
            <div className="ms-val">{m.value}</div>
            {m.delta && <div className={`ms-delta ${m.delta.startsWith('−') || m.deltaNeg ? 'neg' : 'pos'}`}>{m.delta}</div>}
          </div>
          <div className="ms-cap">{m.caption}</div>
          {m.spark && (
            <svg className="ms-spark" width="100%" height="22" viewBox="0 0 120 22" preserveAspectRatio="none">
              <polyline points={m.spark} fill="none" stroke="#14130E" strokeWidth="1.2" />
            </svg>
          )}
        </div>
      ))}
    </div>
  );
}
window.MetricStrip = MetricStrip;
