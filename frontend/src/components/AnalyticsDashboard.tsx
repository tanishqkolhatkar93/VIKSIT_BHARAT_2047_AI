import { BarChart3, Eye, Share2, Sparkles, Users } from "lucide-react";
import type { AnalyticsSummary } from "../services/api";
import type { Dictionary } from "../utils/i18n";

type Props = {
  analytics: AnalyticsSummary | null;
  t: Dictionary;
};

export function AnalyticsDashboard({ analytics, t }: Props) {
  if (!analytics) return null;

  const items = [
    { icon: Eye, value: analytics.total_views, label: t.analyticsVisits },
    { icon: Users, value: analytics.unique_visitors, label: t.analyticsVisitors },
    { icon: Sparkles, value: analytics.total_visions, label: t.analyticsVisions },
    { icon: Share2, value: analytics.total_cards, label: t.analyticsCards },
  ];

  return (
    <section className="analytics-section" aria-labelledby="analytics-title">
      <div className="section-heading">
        <p>{t.analyticsSubtitle}</p>
        <h2 id="analytics-title">{t.analyticsTitle}</h2>
      </div>
      <div className="analytics-card">
        <div className="analytics-grid">
          {items.map(({ icon: Icon, value, label }) => (
            <div className="analytics-stat" key={label}>
              <span className="analytics-icon" aria-hidden="true">
                <Icon size={20} />
              </span>
              <strong>{value}</strong>
              <span className="analytics-label">{label}</span>
            </div>
          ))}
        </div>
        <p className="analytics-today">
          <BarChart3 size={14} /> {t.analyticsToday}: {analytics.visits_today}
        </p>
      </div>
    </section>
  );
}
