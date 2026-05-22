/* global React */
const { useEffect: useEffectCTA } = React;

function CTA() {
  useEffectCTA(() => { if (window.lucide) window.lucide.createIcons(); });
  return (
    <section className="lp-cta-section">
      <div className="cta-card">
        <h2 className="cta-h">Start finding your champion today.</h2>
        <p className="cta-sub">Free for OSS projects. Self-host or use the cloud workbench. Bring your own models, retrievers, and tools.</p>
        <div className="cta-row">
          <a className="lp-btn-primary lg" href="#start">Get started <i data-lucide="arrow-right"></i></a>
          <a className="lp-btn-secondary lg on-dark" href="#book">Talk to the team</a>
        </div>
        <code className="cta-cmd">
          <span className="cmd-p">$</span> pip install autoagent-optimizer
        </code>
      </div>
    </section>
  );
}
window.CTA = CTA;
