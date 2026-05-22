/* global React */
const { useEffect: useEffectArchList } = React;

function ArchList({ items, activeId, onSelect }) {
  useEffectArchList(() => { if (window.lucide) window.lucide.createIcons(); });
  return (
    <div className="arch-list">
      <div className="arch-list-head">
        <span className="al-label">Architectures · sorted by f1@k</span>
        <div className="al-tools">
          <button className="al-tool"><i data-lucide="arrow-down-up"></i>Sort</button>
          <button className="al-tool"><i data-lucide="filter"></i>Filter</button>
        </div>
      </div>
      {items.map(a => (
        <div
          key={a.id}
          className={`arch-row status-${a.status} ${a.id === activeId ? 'active' : ''}`}
          onClick={() => onSelect(a.id)}
        >
          <div className="ar-id mono">{a.id}</div>
          <div className="ar-name">
            <div className="ar-title">{a.name}</div>
            <div className="ar-shape mono">{a.shape}</div>
          </div>
          <div className="ar-met"><div className="ar-met-val mono">{a.f1}</div><div className="ar-met-lbl">f1@k</div></div>
          <div className="ar-met"><div className="ar-met-val mono">{a.cost}</div><div className="ar-met-lbl">cost</div></div>
          <div className="ar-met"><div className="ar-met-val mono">{a.p95}</div><div className="ar-met-lbl">p95</div></div>
          <div className="ar-status">
            <span className={`pill p-${a.status}`}>
              <span className="dot"></span>{a.status}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
window.ArchList = ArchList;
