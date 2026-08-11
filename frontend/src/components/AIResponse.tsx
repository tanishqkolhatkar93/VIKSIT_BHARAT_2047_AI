import type { Source, VisionPayload } from "../types/api";
import type { Dictionary } from "../utils/i18n";

type Props = {
  response: VisionPayload;
  sources: Source[];
  t: Dictionary;
};

function TextBlock({ title, text }: { title: string; text: string }) {
  return (
    <section className="response-block">
      <h3>{title}</h3>
      <p>{text}</p>
    </section>
  );
}

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="response-block">
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

export function AIResponse({ response, sources, t }: Props) {
  return (
    <section className="response-section" aria-live="polite">
      <TextBlock title={t.vision} text={response.vision} />
      <ListBlock title={t.opportunities} items={response.opportunities} />
      <TextBlock title={t.roleAi} text={response.role_of_ai} />
      <TextBlock title={t.roleTech} text={response.role_of_technology} />
      <TextBlock title={t.impact} text={response.potential_impact} />
      <ListBlock title={t.challenges} items={response.challenges} />
      <ListBlock title={t.action} items={response.action_plan} />
      <TextBlock title={t.summary} text={response.summary_2047} />
      <section className="response-block note">
        <p>{response.fact_scenario_note}</p>
      </section>
      <section className="response-block sources">
        <h3>{t.sources}</h3>
        {sources.map((source) => (
          <a href={source.url} target="_blank" rel="noreferrer" key={`${source.title}-${source.date}`}>
            <strong>{source.title}</strong>
            <span>{source.source} · {source.date}</span>
          </a>
        ))}
      </section>
    </section>
  );
}

