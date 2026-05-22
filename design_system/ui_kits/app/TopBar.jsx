/* global React */
const { useEffect: useEffectTopBar } = React;

function TopBar({ run, onPalette }) {
  useEffectTopBar(() => { if (window.lucide) window.lucide.createIcons(); });
  return (
    <header className="app-topbar">
      <div className="tb-left">
        <span className="tb-crumb">Runs</span>
        <span className="tb-sep">/</span>
        <span className="tb-id mono">{run.id}</span>
        <span className="tb-pill">v3 · 24 candidates</span>
      </div>

      <div className="tb-mid">
        <div className="tb-budget">
          <div className="tb-budget-label">
            <i data-lucide="coins"></i>
            <span>Budget</span>
          </div>
          <div className="tb-budget-bar">
            <div className="tb-budget-fill" style={{width: '62%'}}></div>
          </div>
          <div className="tb-budget-vals">
            <span className="mono">$24.80</span>
            <span className="muted">/ $40.00 · cost ≤ $0.40 / case</span>
          </div>
        </div>
      </div>

      <div className="tb-right">
        <button className="tb-search" onClick={onPalette}>
          <i data-lucide="search"></i>
          <span>Find architecture, trace, case…</span>
          <span className="kbd">⌘ K</span>
        </button>
        <button className="tb-btn tb-btn-ghost"><i data-lucide="git-compare"></i>Compare</button>
        <button className="tb-btn tb-btn-primary"><i data-lucide="check-check"></i>Promote champion</button>
      </div>
    </header>
  );
}
window.TopBar = TopBar;
