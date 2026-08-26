import { ArrowDownRight, Boxes, CheckCircle2, Cloud, ShieldCheck, Sparkles } from "lucide-react";

const layers = [
  {
    icon: Boxes,
    label: "Product model",
    title: "A blueprint before feature drift",
    copy: "Routes, roles, data, states, assumptions, and acceptance criteria live beside the code.",
  },
  {
    icon: Sparkles,
    label: "UI / UX",
    title: "A visual thesis, not a theme swap",
    copy: "Semantic tokens and a responsive shell are ready to become a product-specific design system.",
  },
  {
    icon: Cloud,
    label: "Firebase / GCP",
    title: "Deployable boundaries from day one",
    copy: "App Hosting config, locked Rules, Emulator settings, and public/server configuration boundaries are present.",
  },
];

export default function Home() {
  return (
    <>
      <header className="masthead" aria-label="Primary navigation">
        <a className="wordmark" href="#top" aria-label="__APP_NAME__ home">
          __APP_NAME__
        </a>
        <nav>
          <a href="#foundation">Foundation</a>
          <a href="#readiness">Readiness</a>
          <a href="#release-gates">Release gates</a>
        </nav>
      </header>

      <main id="main-content">
        <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">Prompt → blueprint → working Firebase app</p>
          <h1>__APP_DESCRIPTION__</h1>
          <p className="lede">
            This is the operational foundation—not the final product. Replace this surface with the primary user journey while preserving its build, access, and release guardrails.
          </p>
          <div className="hero-actions">
            <a className="button primary" href="#foundation">
              Inspect the foundation <ArrowDownRight aria-hidden="true" size={18} />
            </a>
            <a className="button secondary" href="#readiness">
              Review readiness
            </a>
          </div>
        </div>
        <aside className="contract-card" aria-label="Build contract">
          <p className="contract-index">01 / BUILD CONTRACT</p>
          <h2>Useful before impressive. Complete before claimed.</h2>
          <ul>
            <li><CheckCircle2 aria-hidden="true" /> One primary journey end to end</li>
            <li><CheckCircle2 aria-hidden="true" /> Every visible action operational</li>
            <li><CheckCircle2 aria-hidden="true" /> Privacy-protective defaults</li>
            <li><CheckCircle2 aria-hidden="true" /> Launch claims backed by evidence</li>
          </ul>
        </aside>
        </section>

        <section className="section" id="foundation" aria-labelledby="foundation-heading">
        <div className="section-heading">
          <p className="eyebrow">The substrate</p>
          <h2 id="foundation-heading">Three layers that must evolve together</h2>
          <p>Do not finish the UI and bolt on security, data, or legal behavior afterward.</p>
        </div>
        <div className="layer-list">
          {layers.map(({ icon: Icon, label, title, copy }, index) => (
            <article className="layer" key={label}>
              <span className="layer-number">0{index + 1}</span>
              <Icon aria-hidden="true" size={24} />
              <div>
                <p className="layer-label">{label}</p>
                <h3>{title}</h3>
                <p>{copy}</p>
              </div>
            </article>
          ))}
        </div>
        </section>

        <section className="readiness-grid" id="readiness" aria-labelledby="readiness-heading">
        <div className="readiness-intro">
          <p className="eyebrow">Truthful readiness</p>
          <h2 id="readiness-heading">A runnable shell is not a launched product.</h2>
          <p>Use the blueprint and readiness report to distinguish what works, what is mocked, and what needs an accountable decision.</p>
        </div>
        <article>
          <span className="status-dot ready" aria-hidden="true" />
          <h3>Operational foundation</h3>
          <ul>
            <li>Next.js production build path</li>
            <li>Responsive semantic document shell</li>
            <li>Locked Firestore and Storage Rules</li>
            <li>Firebase Emulator configuration</li>
            <li>Analytics and ads disabled by default</li>
          </ul>
        </article>
        <article>
          <span className="status-dot blocked" aria-hidden="true" />
          <h3>Required before launch</h3>
          <ul>
            <li>Product-specific primary journey and states</li>
            <li>Verified operator, market, content, and policies</li>
            <li>Firebase projects, regions, Rules, and credentials</li>
            <li>Runtime, accessibility, security, and consent tests</li>
            <li>Monitoring, budgets, recovery, and owner approval</li>
          </ul>
        </article>
        </section>

        <section className="release-band" id="release-gates" aria-labelledby="release-heading">
        <ShieldCheck aria-hidden="true" size={34} />
        <div>
          <p className="eyebrow">Release gate</p>
          <h2 id="release-heading">Keep optional collection off until the legal profile permits it.</h2>
          <p>Do not initialize analytics, advertising, tracking, or third-party embeds merely because configuration keys exist.</p>
        </div>
        </section>
      </main>
    </>
  );
}
