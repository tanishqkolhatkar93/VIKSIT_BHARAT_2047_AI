import {
  CheckCircle2,
  Eye,
  EyeOff,
  ExternalLink,
  KeyRound,
  Loader2,
  ShieldCheck,
  Trash2,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { testGeminiKey, type GeminiTestResult } from "../services/api";
import type { Dictionary } from "../utils/i18n";

export type ConnectionStatus = "connected" | "default" | "not-connected";

type Props = {
  apiKey: string;
  detectedModel: string;
  status: ConnectionStatus;
  useMyKey: boolean;
  t: Dictionary;
  onSaveKey: (apiKey: string, detectedModel: string) => void;
  onRemoveKey: () => void;
  onToggleUseMyKey: () => void;
  onClose: () => void;
};

const GEMINI_KEY_URL = "https://aistudio.google.com/app/apikey";

export function GeminiConnectModal({
  apiKey,
  detectedModel,
  status,
  useMyKey,
  t,
  onSaveKey,
  onRemoveKey,
  onToggleUseMyKey,
  onClose,
}: Props) {
  const [inputKey, setInputKey] = useState(apiKey);
  const [showKey, setShowKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<GeminiTestResult | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  async function runTest() {
    const key = inputKey.trim();
    if (key.length < 10) return;
    setTesting(true);
    setResult(null);
    try {
      const res = await testGeminiKey(key);
      setResult(res);
      if (res.connected) {
        onSaveKey(key, res.model ?? "");
      }
    } catch {
      setResult({
        connected: false,
        model: null,
        message: "Could not reach the connection service. Please try again.",
      });
    } finally {
      setTesting(false);
      inputRef.current?.focus();
    }
  }

  function removeKey() {
    setInputKey("");
    setResult(null);
    onRemoveKey();
    inputRef.current?.focus();
  }

  return (
    <div className="gemini-overlay" role="dialog" aria-modal="true" aria-labelledby="gemini-modal-title">
      <div className="gemini-modal">
        <div className="gemini-modal-glow" aria-hidden="true" />
        <header className="gemini-modal-head">
          <div className="gemini-title-row">
            <span className="gemini-icon" aria-hidden="true">
              <KeyRound size={22} />
            </span>
            <div>
              <h3 id="gemini-modal-title">{t.geminiTitle}</h3>
              <p>{t.geminiSubtitle}</p>
            </div>
          </div>
          <button type="button" className="gemini-close" onClick={onClose} aria-label={t.geminiClose}>
            <X size={20} />
          </button>
        </header>

        <div className="gemini-modal-body">
          <label className="gemini-field">
            <span>{t.apiKeyLabel}</span>
            <div className="gemini-input-row">
              <input
                ref={inputRef}
                type={showKey ? "text" : "password"}
                value={inputKey}
                maxLength={200}
                onChange={(event) => {
                  setInputKey(event.target.value);
                  setResult(null);
                }}
                placeholder={t.apiKeyPlaceholder}
                autoComplete="off"
                spellCheck={false}
                aria-label={t.apiKeyLabel}
              />
              <button
                type="button"
                className="gemini-input-toggle"
                onClick={() => setShowKey((value) => !value)}
                aria-label={showKey ? t.geminiHide : t.geminiShow}
              >
                {showKey ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </label>

          <div className="gemini-link-row">
            <span>{t.geminiGetHint}</span>
            <a href={GEMINI_KEY_URL} target="_blank" rel="noopener noreferrer">
              {t.geminiGetLink} <ExternalLink size={14} />
            </a>
          </div>

          <button
            type="button"
            className="button primary gemini-test-btn"
            disabled={testing || inputKey.trim().length < 10}
            onClick={runTest}
          >
            {testing ? <Loader2 size={18} className="spin" /> : <ShieldCheck size={18} />}
            {testing ? t.geminiTesting : t.geminiTestBtn}
          </button>

          {result ? (
            result.connected ? (
              <div className="gemini-status gemini-status-ok" role="status">
                <CheckCircle2 size={18} />
                <div>
                  <strong>{t.geminiConnected}</strong>
                  <span>
                    {t.geminiModelDetected} <code>{result.model}</code>
                  </span>
                </div>
              </div>
            ) : (
              <div className="gemini-status gemini-status-err" role="alert">
                <X size={18} />
                <div>
                  <strong>{t.geminiFailed}</strong>
                  <span>{result.message}</span>
                </div>
              </div>
            )
          ) : null}

          {status === "connected" && !result ? (
            <div className="gemini-status gemini-status-ok" role="status">
              <CheckCircle2 size={18} />
              <div>
                <strong>{t.geminiConnected}</strong>
                <span>
                  {t.geminiModelDetected} <code>{detectedModel}</code>
                </span>
              </div>
            </div>
          ) : null}

          <div className="gemini-toggle-row">
            <label className="gemini-toggle">
              <input
                type="checkbox"
                checked={useMyKey}
                disabled={!apiKey}
                onChange={onToggleUseMyKey}
              />
              <span className="gemini-toggle-track" aria-hidden="true">
                <span className="gemini-toggle-thumb" aria-hidden="true" />
              </span>
              <span>
                <strong>{t.geminiUseMyKey}</strong>
                <small>{t.geminiUseMyKeyDesc}</small>
              </span>
            </label>
          </div>

          <div className="gemini-privacy">
            <ShieldCheck size={16} />
            <p>{t.geminiPrivacy}</p>
          </div>
          <p className="gemini-storage-note">{t.geminiStorageNote}</p>

          {status === "connected" ? (
            <button type="button" className="gemini-remove-btn" onClick={removeKey}>
              <Trash2 size={16} /> {t.geminiRemove}
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
