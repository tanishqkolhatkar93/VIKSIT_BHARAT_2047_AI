import { languages } from "../services/api";
import type { Dictionary, LanguageCode } from "../utils/i18n";

type Props = {
  language: LanguageCode;
  setLanguage: (language: LanguageCode) => void;
  t: Dictionary;
};

export function Navbar({ language, setLanguage, t }: Props) {
  return (
    <nav className="navbar" aria-label="Primary navigation">
      <a className="brand" href="#top" aria-label={t.appName}>
        <span className="brand-mark" aria-hidden="true" />
        {t.appName}
      </a>
      <div className="nav-links">
        <a href="#ask">{t.primaryCta}</a>
        <a href="#pulse">{t.pulseTitle}</a>
        <label className="language-label">
          <span>{t.language}</span>
          <select
            aria-label={t.language}
            value={language}
            onChange={(event) => setLanguage(event.target.value as LanguageCode)}
          >
            {languages.map((item) => (
              <option value={item.code} key={item.code}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
      </div>
    </nav>
  );
}

