/* global React */
const { useEffect } = React;

function Nav() {
  useEffect(() => { if (window.lucide) window.lucide.createIcons(); });
  return (
    <nav className="lp-nav">
      <div className="lp-nav-inner">
        <a className="lp-brand" href="#">
          <img src="../../assets/logo-lockup.svg" alt="AutoAgent Optimizer" />
        </a>
        <div className="lp-nav-links">
          <a href="#how">Product</a>
          <a href="#proof">Architectures</a>
          <a href="#docs">Docs</a>
          <a href="#examples">Examples</a>
          <a href="#pricing">Pricing</a>
        </div>
        <div className="lp-nav-cta">
          <a className="lp-star" href="#github">
            <i data-lucide="star"></i>
            <span>4.2k</span>
          </a>
          <a className="lp-link" href="#signin">Sign in</a>
          <a className="lp-btn-primary" href="#start">
            Get started
            <i data-lucide="arrow-right"></i>
          </a>
        </div>
      </div>
    </nav>
  );
}

window.Nav = Nav;
