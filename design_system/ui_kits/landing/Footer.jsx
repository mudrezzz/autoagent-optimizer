/* global React */
const { useEffect: useEffectFooter } = React;

function Footer() {
  useEffectFooter(() => { if (window.lucide) window.lucide.createIcons(); });
  return (
    <footer className="lp-foot">
      <div className="lp-foot-inner">
        <div className="lp-foot-brand">
          <img src="../../assets/logo-lockup.svg" alt="AutoAgent Optimizer" />
          <p className="foot-tag">Compound AI systems, designed and measured with evidence.</p>
          <div className="foot-soc">
            <a aria-label="GitHub"><span className="foot-soc-text">GH</span></a>
            <a aria-label="Twitter"><span className="foot-soc-text">X</span></a>
            <a aria-label="Discord"><i data-lucide="message-circle"></i></a>
          </div>
        </div>
        <div className="lp-foot-cols">
          <div>
            <div className="foot-lbl">Product</div>
            <a>Workbench</a>
            <a>Trace viewer</a>
            <a>Evidence export</a>
            <a>Pricing</a>
          </div>
          <div>
            <div className="foot-lbl">Docs</div>
            <a>Quickstart</a>
            <a>DSL reference</a>
            <a>Recipes</a>
            <a>Changelog</a>
          </div>
          <div>
            <div className="foot-lbl">Community</div>
            <a>GitHub</a>
            <a>Discord</a>
            <a>Papers</a>
            <a>Roadmap</a>
          </div>
          <div>
            <div className="foot-lbl">Company</div>
            <a>About</a>
            <a>Blog</a>
            <a>Careers</a>
            <a>Contact</a>
          </div>
        </div>
      </div>
      <div className="lp-foot-bot">
        <span>© 2026 AutoAgent · Apache 2.0 · Open source</span>
        <span className="mono">v0.4 · commit b4f3a01</span>
      </div>
    </footer>
  );
}
window.Footer = Footer;
