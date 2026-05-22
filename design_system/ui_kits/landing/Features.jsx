/* global React */
const { useEffect: useEffectFeat } = React;

function Features() {
  useEffectFeat(() => { if (window.lucide) window.lucide.createIcons(); });
  const items = [
    {
      icon: "boxes",
      tint: "indigo",
      title: "Generate architectures",
      copy: "Describe your task once. AutoAgent spawns architecturally distinct baselines — single-shot, retrieval, plan-then-act, tool-augmented, ensemble, HITL-gated.",
    },
    {
      icon: "activity",
      tint: "blue",
      title: "Measure as white boxes",
      copy: "Every component is traced. Middle-metrics surface regressions invisible to end-to-end scores: retrieval recall, tool error rate, judge agreement.",
    },
    {
      icon: "target",
      tint: "green",
      title: "Optimize under budget",
      copy: "Search across cost, latency, accuracy, and human-effort constraints. Promote a champion you can ship — and export the evidence behind it.",
    },
  ];

  return (
    <section className="lp-features" id="how">
      <div className="lp-section-head">
        <span className="lp-eyebrow"><span className="ey-dot"></span>How it works</span>
        <h2 className="lp-h2">Three moves. Repeated until the evidence is undeniable.</h2>
        <p className="lp-section-sub">A workbench, not a black box. You see every architecture, every trace, every metric — and you decide what ships.</p>
      </div>
      <div className="lp-feature-grid">
        {items.map((it, i) => (
          <article className={`feat-card tint-${it.tint}`} key={i}>
            <div className="feat-ico"><i data-lucide={it.icon}></i></div>
            <h3 className="feat-title">{it.title}</h3>
            <p className="feat-copy">{it.copy}</p>
            <a className="feat-link">Learn more <i data-lucide="arrow-right"></i></a>
          </article>
        ))}
      </div>
    </section>
  );
}
window.Features = Features;
