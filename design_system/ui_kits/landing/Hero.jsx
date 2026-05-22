/* global React */
const { useEffect: useEffectHero } = React;

function Hero() {
  useEffectHero(() => { if (window.lucide) window.lucide.createIcons(); });
  return (
    <section className="lp-hero">
      <div className="lp-hero-inner">
        <div className="lp-hero-text">
          <span className="lp-eyebrow">
            <span className="ey-dot"></span>
            Compound AI systems · OSS
          </span>

          <h1 className="lp-display">
            Design many architectures.<br/>
            Ship the one that <span className="accent">proves itself</span>.
          </h1>

          <p className="lp-sub">
            AutoAgent Optimizer generates architecturally distinct baselines for the same task,
            measures them as white boxes, and returns a deployable champion — with the trace,
            the budget, and the regression matrix to back it up.
          </p>

          <div className="lp-cta-row">
            <a className="lp-btn-primary lg" href="#start">
              Start a run free
              <i data-lucide="arrow-right"></i>
            </a>
            <a className="lp-btn-secondary lg" href="#demo">
              <i data-lucide="play"></i>
              Watch a 3-min demo
            </a>
          </div>

          <div className="lp-hero-meta">
            <span><i data-lucide="check"></i>No credit card</span>
            <span><i data-lucide="check"></i>Open source · Apache 2.0</span>
            <span><i data-lucide="check"></i>BYO models & components</span>
          </div>
        </div>

        <div className="lp-hero-visual">
          <HeroDemo />
        </div>
      </div>

      <div className="lp-trust">
        <span className="lp-trust-lbl">Trusted by teams shipping production AI at</span>
        <div className="lp-trust-logos">
          <span>Anthropic</span>
          <span>Stripe</span>
          <span>Linear</span>
          <span>Notion</span>
          <span>Vercel</span>
          <span>Modal</span>
        </div>
      </div>
    </section>
  );
}

function HeroDemo() {
  return (
    <div className="hero-demo">
      <div className="hd-tabs">
        <span className="hd-tab on"><span className="hd-dot champ"></span>arch_b4f · champion</span>
        <span className="hd-tab"><span className="hd-dot"></span>arch_3c1</span>
        <span className="hd-tab"><span className="hd-dot"></span>arch_2e8</span>
      </div>

      <div className="hd-metrics">
        <div className="hd-m">
          <span className="hd-m-lbl">f1@k</span>
          <span className="hd-m-val">0.842</span>
          <span className="hd-m-delta pos">+4.2</span>
        </div>
        <div className="hd-m">
          <span className="hd-m-lbl">Cost / case</span>
          <span className="hd-m-val">$0.31</span>
          <span className="hd-m-delta pos">−38 %</span>
        </div>
        <div className="hd-m">
          <span className="hd-m-lbl">p95</span>
          <span className="hd-m-val">1.24 s</span>
          <span className="hd-m-delta neg">+0.32 s</span>
        </div>
      </div>

      <div className="hd-trace">
        <div className="hd-trace-head">
          <span>White-box trace</span>
          <span className="hd-trace-meta">case 14 / 24</span>
        </div>
        <div className="hd-trace-rows">
          <div className="hd-r"><span className="hd-r-lbl">retriever</span><div className="hd-track"><div className="hd-seg retrieval" style={{left:'0%', width:'32%'}}></div></div></div>
          <div className="hd-r"><span className="hd-r-lbl">reranker</span><div className="hd-track"><div className="hd-seg llm" style={{left:'32%', width:'24%'}}></div></div></div>
          <div className="hd-r"><span className="hd-r-lbl">tool.calc</span><div className="hd-track"><div className="hd-seg tool" style={{left:'56%', width:'5%'}}></div></div></div>
          <div className="hd-r"><span className="hd-r-lbl">llm.answer</span><div className="hd-track"><div className="hd-seg llm" style={{left:'61%', width:'30%'}}></div></div></div>
          <div className="hd-r"><span className="hd-r-lbl">hitl.review</span><div className="hd-track"><div className="hd-seg hitl" style={{left:'91%', width:'9%'}}></div></div></div>
        </div>
      </div>
    </div>
  );
}

window.Hero = Hero;
