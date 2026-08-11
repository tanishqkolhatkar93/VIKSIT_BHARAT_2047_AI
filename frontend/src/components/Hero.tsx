import { ArrowDown, Sparkles } from "lucide-react";
import type { Dictionary } from "../utils/i18n";

export function Hero({ t }: { t: Dictionary }) {
  return (
    <section id="top" className="hero">
      <div className="hero-map" aria-hidden="true">
        <div className="chakra" />
      </div>
      <div className="hero-content">
        <p className="eyebrow">{t.tagline}</p>
        <h1>{t.heroTitle}</h1>
        <p className="lead">{t.heroLead}</p>
        <div className="cta-row">
          <a className="button primary" href="#ask">
            <Sparkles size={18} /> {t.primaryCta}
          </a>
          <a className="button secondary" href="#pulse">
            <ArrowDown size={18} /> {t.secondaryCta}
          </a>
        </div>
      </div>
    </section>
  );
}

