import type { CountItem, PulseSummary } from "../types/api";
import type { Dictionary } from "../utils/i18n";

const sampleCategories = ["Agriculture", "Education", "Healthcare", "Employment", "Technology", "Climate", "Infrastructure"];

function Chart({ title, items }: { title: string; items: CountItem[] }) {
  if (items.length === 0) return null;
  const max = Math.max(...items.map((item) => item.count));
  return (
    <div className="chart-block">
      <h3>{title}</h3>
      <div className="chart-bars">
        {items.map((item) => (
          <div className="bar-row" key={`${title}-${item.name}`}>
            <span>{item.name}</span>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${Math.max(8, (item.count / max) * 100)}%` }} />
            </div>
            <em>{item.count}</em>
          </div>
        ))}
      </div>
    </div>
  );
}

type Props = {
  pulse: PulseSummary | null;
  t: Dictionary;
};

export function PulseDashboard({ pulse, t }: Props) {
  const isEmpty = !pulse || pulse.totalVisions === 0;
  return (
    <section id="pulse" className="pulse-section" aria-labelledby="pulse-title">
      <div className="section-heading">
        <p>{t.pulseSubtitle}</p>
        <h2 id="pulse-title">{t.pulseTitle}</h2>
      </div>

      {isEmpty ? (
        <div className="pulse-card">
          <p className="empty-state">{t.pulseEmpty}</p>
          <div className="chart-placeholder" aria-hidden="true">
            {sampleCategories.map((item) => (
              <div className="bar-row" key={item}>
                <span>{item}</span>
                <div />
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="pulse-card">
          <div className="pulse-stats">
            <div className="stat-card">
              <strong>{pulse.totalVisions}</strong>
              <span>{t.pulseTotal}</span>
            </div>
            <div className="stat-card">
              <strong>{pulse.popularCategories[0]?.name ?? "—"}</strong>
              <span>{t.pulseTopTopic}</span>
            </div>
            <div className="stat-card">
              <strong>{pulse.popularStates[0]?.name ?? "—"}</strong>
              <span>{t.pulseTopState}</span>
            </div>
          </div>

          <div className="pulse-charts">
            <Chart title={t.pulseTopics} items={pulse.popularCategories} />
            <Chart title={t.pulseStates} items={pulse.popularStates} />
            <Chart title={t.pulseLanguages} items={pulse.languageDistribution} />
          </div>

          {pulse.recentTrends.length > 0 ? (
            <div className="trend-block">
              <h3>{t.pulseTrends}</h3>
              <div className="trend-chips">
                {pulse.recentTrends.map((item, index) => (
                  <span className="trend-chip" key={`${item.category}-${item.state}-${index}`}>
                    {item.category} · {item.state}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      )}
    </section>
  );
}
