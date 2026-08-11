import { KeyRound } from "lucide-react";
import { languages } from "../services/api";
import type { Dictionary, LanguageCode } from "../utils/i18n";
import type { ConnectionStatus } from "./GeminiConnectModal";

type Props = {
  language: LanguageCode;
  setLanguage: (language: LanguageCode) => void;
  t: Dictionary;
  geminiStatus: ConnectionStatus;
  onOpenGemini: () => void;
};

export function Navbar({ language, setLanguage, t, geminiStatus, onOpenGemini }: Props) {
  const statusLabel = {
    connected: t.geminiNavConnected,
    default: t.geminiNavDefault,
    "not-connected": t.geminiNavNotConnected,
  }[geminiStatus];

  return (
    <nav className="navbar" aria-label="Primary navigation">
      <a className="brand" href="#top" aria-label={t.appName}>
        <span className="brand-mark" aria-hidden="true" />
        {t.appName}
      </a>
      <div className="nav-links">
        <a href="#ask">{t.primaryCta}</a>
        <a href="#pulse">{t.pulseTitle}</a>
        <button type="button" className={`gemini-nav-pill ${geminiStatus}`} onClick={onOpenGemini} aria-label={t.geminiNavLabel}>
          <span className="gemini-nav-dot" aria-hidden="true" />
          <KeyRound size={14} aria-hidden="true" />
          {statusLabel}
        </button>
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
