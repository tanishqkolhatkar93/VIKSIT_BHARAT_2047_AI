import { Mic, Send } from "lucide-react";
import { categories, states } from "../services/api";
import type { Dictionary, LanguageCode } from "../utils/i18n";

type Props = {
  t: Dictionary;
  language: LanguageCode;
  state: string;
  category: string;
  name: string;
  question: string;
  loading: boolean;
  onState: (value: string) => void;
  onCategory: (value: string) => void;
  onName: (value: string) => void;
  onQuestion: (value: string) => void;
  onSubmit: () => void;
  onVoice: () => void;
};

export function VisionInput({
  t,
  state,
  category,
  name,
  question,
  loading,
  onState,
  onCategory,
  onName,
  onQuestion,
  onSubmit,
  onVoice
}: Props) {
  const canSubmit = !loading && name.trim().length >= 2 && question.trim().length >= 8;
  return (
    <section id="ask" className="ask-shell" aria-labelledby="question-title">
      <div className="section-heading">
        <p>Imagine → Ask → Contribute → Create → Share</p>
        <h2 id="question-title">{t.questionTitle}</h2>
      </div>
      <div className="ask-card">
        <div className="control-grid">
          <label>
            {t.state}
            <select value={state} onChange={(event) => onState(event.target.value)}>
              {states.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            {t.category}
            <select value={category} onChange={(event) => onCategory(event.target.value)}>
              {categories.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            {t.nameLabel}
            <input
              type="text"
              value={name}
              maxLength={100}
              onChange={(event) => onName(event.target.value)}
              placeholder={t.namePlaceholder}
            />
          </label>
        </div>
        <label className="question-label">
          {t.questionLabel}
          <textarea
            value={question}
            maxLength={800}
            onChange={(event) => onQuestion(event.target.value)}
            placeholder={`"${t.questionPlaceholder}"`}
          />
        </label>
        <div className="ask-actions">
          <button type="button" className="button secondary" onClick={onVoice}>
            <Mic size={18} /> {t.voice}
          </button>
          <button
            type="button"
            className="button primary"
            disabled={!canSubmit}
            onClick={onSubmit}
          >
            <Send size={18} /> {loading ? t.loading : t.submit}
          </button>
        </div>
      </div>
    </section>
  );
}

