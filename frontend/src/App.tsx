import { useEffect, useMemo, useState } from "react";
import { KeyRound as KeyRoundIcon } from "lucide-react";
import { AIResponse } from "./components/AIResponse";
import { AnalyticsDashboard } from "./components/AnalyticsDashboard";
import { Footer } from "./components/Footer";
import { GeminiConnectModal, type ConnectionStatus } from "./components/GeminiConnectModal";
import { Hero } from "./components/Hero";
import { Navbar } from "./components/Navbar";
import { PulseDashboard } from "./components/PulseDashboard";
import { VisionCard } from "./components/VisionCard";
import { VisionInput } from "./components/VisionInput";
import { useSpeech } from "./hooks/useSpeech";
import { generateVision, getAnalytics, getPulse, recordPageView, type AnalyticsSummary } from "./services/api";
import type { PulseSummary, VisionResponse } from "./types/api";
import { getDictionary, getSavedLanguage, type LanguageCode } from "./utils/i18n";

const KEY_STORAGE = "gemini_api_key";
const MODEL_STORAGE = "gemini_detected_model";
const USE_MY_KEY_STORAGE = "gemini_use_my_key";

function getStored(key: string, fallback = ""): string {
  try {
    return localStorage.getItem(key) ?? fallback;
  } catch {
    return fallback;
  }
}

function setStored(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    // storage unavailable — fail silently
  }
}

function getStoredBool(key: string): boolean {
  return getStored(key) === "1";
}

export default function App() {
  const [language, setLanguage] = useState<LanguageCode>(getSavedLanguage);
  const [state, setState] = useState("All India");
  const [category, setCategory] = useState("Education");
  const [name, setName] = useState("");
  const [question, setQuestion] = useState("");
  const [apiKey, setApiKey] = useState(() => getStored(KEY_STORAGE));
  const [detectedModel, setDetectedModel] = useState(() => getStored(MODEL_STORAGE));
  const [useMyKey, setUseMyKey] = useState(() => getStoredBool(USE_MY_KEY_STORAGE));
  const [geminiOpen, setGeminiOpen] = useState(false);
  const [result, setResult] = useState<VisionResponse | null>(null);
  const [pulse, setPulse] = useState<PulseSummary | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [suggestGemini, setSuggestGemini] = useState(false);
  const t = useMemo(() => getDictionary(language), [language]);
  const speech = useSpeech(language);

  useEffect(() => {
    localStorage.setItem("language", language);
  }, [language]);

  const geminiStatus: ConnectionStatus = useMyKey
    ? apiKey
      ? "connected"
      : "not-connected"
    : "default";

  useEffect(() => {
    getPulse()
      .then(setPulse)
      .catch(() => setPulse(null));
  }, []);

  useEffect(() => {
    recordPageView(window.location.pathname);
    getAnalytics()
      .then(setAnalytics)
      .catch(() => setAnalytics(null));
  }, []);

  function saveKey(key: string, model: string) {
    setApiKey(key);
    setDetectedModel(model);
    setUseMyKey(true);
    setStored(KEY_STORAGE, key);
    setStored(MODEL_STORAGE, model);
    setStored(USE_MY_KEY_STORAGE, "1");
  }

  function removeKey() {
    setApiKey("");
    setDetectedModel("");
    setUseMyKey(false);
    setStored(KEY_STORAGE, "");
    setStored(MODEL_STORAGE, "");
    setStored(USE_MY_KEY_STORAGE, "0");
  }

  function toggleUseMyKey() {
    const next = !useMyKey;
    setUseMyKey(next);
    setStored(USE_MY_KEY_STORAGE, next ? "1" : "0");
  }

  async function submitVision() {
    setError("");
    setSuggestGemini(false);
    setLoading(true);
    try {
      const activeKey = useMyKey && apiKey ? apiKey : null;
      const activeModel = useMyKey && detectedModel ? detectedModel : null;
      const data = await generateVision({ name, question, language, state, category, api_key: activeKey, model: activeModel });
      setResult(data);
      speech.speak(data.response.summary_2047);
      getPulse()
        .then(setPulse)
        .catch(() => {});
    } catch (err) {
      const message = err instanceof Error ? err.message : "India AI is taking a little longer than expected. Please try again.";
      setError(message);
      setSuggestGemini(
        message.includes("daily free limit") || message.includes("taking a little longer") || !useMyKey
      );
    } finally {
      setLoading(false);
    }
  }

  function startVoice() {
    speech.listen(
      (text) => setQuestion(text),
      (code) => {
        const messages: Record<string, string> = {
          unsupported: t.voiceUnsupported,
          permission: t.voicePermission,
          network: t.voiceNetwork,
          noSpeech: t.voiceNoSpeech,
          failed: t.voiceFailed,
        };
        setError(messages[code] ?? t.voiceFailed);
        setSuggestGemini(false);
      }
    );
  }

  return (
    <main>
      <Navbar language={language} setLanguage={setLanguage} t={t} geminiStatus={geminiStatus} onOpenGemini={() => setGeminiOpen(true)} />
      <Hero t={t} />
      <VisionInput
        t={t}
        language={language}
        state={state}
        category={category}
        name={name}
        question={question}
        loading={loading}
        onState={setState}
        onCategory={setCategory}
        onName={setName}
        onQuestion={setQuestion}
        onSubmit={submitVision}
        onVoice={startVoice}
      />
      {error ? (
        <div className="toast-wrap">
          <p className="toast" role="alert">{error}</p>
          {suggestGemini ? (
            <button type="button" className="toast-action" onClick={() => setGeminiOpen(true)}>
              <KeyRoundIcon size={16} /> {t.geminiSuggestBtn}
            </button>
          ) : null}
        </div>
      ) : null}
      {result ? (
        <>
          <AIResponse response={result.response} sources={result.sources} t={t} />
          <VisionCard card={result.response.card} name={name} language={language} t={t} />
        </>
      ) : null}
      <PulseDashboard pulse={pulse} t={t} />
      <AnalyticsDashboard analytics={analytics} t={t} />
      <Footer t={t} />
      {geminiOpen ? (
        <GeminiConnectModal
          apiKey={apiKey}
          detectedModel={detectedModel}
          status={geminiStatus}
          useMyKey={useMyKey}
          t={t}
          onSaveKey={saveKey}
          onRemoveKey={removeKey}
          onToggleUseMyKey={toggleUseMyKey}
          onClose={() => setGeminiOpen(false)}
        />
      ) : null}
    </main>
  );
}
