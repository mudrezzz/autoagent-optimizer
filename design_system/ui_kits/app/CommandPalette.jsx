/* global React */
const { useEffect: useEffectCP, useState: useStateCP } = React;

function CommandPalette({ open, onClose }) {
  useEffectCP(() => { if (window.lucide) window.lucide.createIcons(); });
  const [q, setQ] = useStateCP("");

  if (!open) return null;

  const items = [
    { kind: "run",   icon: "flask-conical", title: "Start new run from spec",   sub: "aao run --spec ./spec.yaml" },
    { kind: "arch",  icon: "boxes",         title: "Promote arch_b4f to champion", sub: "rag · rerank · hyde · +4.2 f1" },
    { kind: "trace", icon: "activity",      title: "Open trace · arch_b4f case 14", sub: "judge.f1 regression" },
    { kind: "comp",  icon: "git-compare",   title: "Compare arch_b4f vs arch_001", sub: "side-by-side" },
    { kind: "exp",   icon: "file-check-2",  title: "Export evidence bundle",   sub: "current run · signed" },
    { kind: "doc",   icon: "book-open",     title: "Open DSL reference",       sub: "docs · v0.4" },
  ];

  return (
    <div className="cp-overlay" onClick={onClose}>
      <div className="cp" onClick={e => e.stopPropagation()}>
        <div className="cp-search">
          <i data-lucide="search"></i>
          <input
            autoFocus
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder="Run a command, find an architecture, jump to a trace…"
          />
          <span className="kbd">esc</span>
        </div>
        <div className="cp-list">
          <div className="cp-group">jump to</div>
          {items.map((it, i) => (
            <div className={`cp-row ${i === 0 ? 'sel' : ''}`} key={i}>
              <i data-lucide={it.icon}></i>
              <div className="cp-text">
                <div className="cp-title">{it.title}</div>
                <div className="cp-sub mono">{it.sub}</div>
              </div>
              <span className="cp-kind mono">{it.kind}</span>
            </div>
          ))}
        </div>
        <div className="cp-foot mono">
          <span><span className="kbd">↑</span><span className="kbd">↓</span> navigate</span>
          <span><span className="kbd">↵</span> run</span>
          <span><span className="kbd">⌘ K</span> close</span>
        </div>
      </div>
    </div>
  );
}
window.CommandPalette = CommandPalette;
