/* global React */
const { useEffect: useEffectSidebar } = React;

function Sidebar({ activeRun, runs, onSelectRun }) {
  useEffectSidebar(() => { if (window.lucide) window.lucide.createIcons(); });
  return (
    <aside className="app-sidebar">
      <div className="app-sidebar-brand">
        <img src="../../assets/logo-lockup.svg" alt="autoagent/optimizer" />
      </div>

      <div className="app-sidebar-section">
        <div className="app-side-label">Workspace</div>
        <div className="app-side-pick">
          <span className="ws-dot"></span>
          <span>support-qa</span>
          <i data-lucide="chevrons-up-down"></i>
        </div>
      </div>

      <nav className="app-side-nav">
        <a className="active"><i data-lucide="flask-conical"></i>Runs <span className="n">12</span></a>
        <a><i data-lucide="boxes"></i>Architectures <span className="n">24</span></a>
        <a><i data-lucide="cpu"></i>Components</a>
        <a><i data-lucide="activity"></i>Traces</a>
        <a><i data-lucide="file-check-2"></i>Evidence</a>
        <a><i data-lucide="coins"></i>Budgets</a>
        <a><i data-lucide="user-check"></i>HITL queue <span className="n n-warn">3</span></a>
      </nav>

      <div className="app-sidebar-section">
        <div className="app-side-label">Recent runs</div>
        <div className="app-runs">
          {runs.map(r => (
            <div
              key={r.id}
              className={`app-run-row ${r.id === activeRun ? "active" : ""}`}
              onClick={() => onSelectRun(r.id)}
            >
              <span className={`run-led ${r.status}`}></span>
              <div className="run-text">
                <div className="run-name">{r.name}</div>
                <div className="run-meta">{r.id} · {r.ago}</div>
              </div>
              {r.status === "champion" && <i data-lucide="target" className="run-trophy"></i>}
            </div>
          ))}
        </div>
      </div>

      <div className="app-sidebar-foot">
        <div className="app-side-user">
          <span className="avatar">EK</span>
          <div>
            <div className="user-name">Elena Kuznetsova</div>
            <div className="user-org">ctrl2go · operator</div>
          </div>
          <i data-lucide="settings-2"></i>
        </div>
      </div>
    </aside>
  );
}
window.Sidebar = Sidebar;
