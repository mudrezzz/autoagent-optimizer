/* global React */
function Philosophy() {
  return (
    <section className="lp-philo">
      <div className="philo-inner">
        <span className="lp-eyebrow"><span className="ey-dot"></span>Our take</span>
        <h2 className="philo-quote">
          A good AI system is a <span className="accent">balance</span> —
          between LLM, deterministic software, tools, tests, human judgement,
          and runtime constraints.
        </h2>
        <p className="philo-attr">— The AutoAgent thesis</p>
      </div>

      <div className="philo-grid">
        <div className="philo-tile">
          <div className="philo-num">01</div>
          <h4 className="philo-h">Not everything should be LLM.</h4>
          <p className="philo-p">Move arithmetic, lookups, transformations, and deterministic logic into tools. LLM tokens are expensive; <code>deterministic</code> code is not.</p>
        </div>
        <div className="philo-tile">
          <div className="philo-num">02</div>
          <h4 className="philo-h">Not everything should be code.</h4>
          <p className="philo-p">Some decisions are open-ended or value-laden. Let an LLM handle them — but track <code>judge agreement</code> as a first-class metric.</p>
        </div>
        <div className="philo-tile">
          <div className="philo-num">03</div>
          <h4 className="philo-h">Some things need a human.</h4>
          <p className="philo-p">Insert HITL gates exactly where the judge disagrees with itself. Quantify the latency tradeoff. Ship if it's worth it.</p>
        </div>
      </div>
    </section>
  );
}
window.Philosophy = Philosophy;
