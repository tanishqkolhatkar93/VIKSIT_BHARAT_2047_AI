import { useEffect, useMemo, useState } from "react";
import { AIResponse } from "./components/AIResponse";
import { Footer } from "./components/Footer";
import { Hero } from "./components/Hero";
import { Navbar } from "./components/Navbar";
import { PulseDashboard } from "./components/PulseDashboard";
import { VisionCard } from "./components/VisionCard";
import { VisionInput } from "./components/VisionInput";
import { useSpeech } from "./hooks/useSpeech";
import { generateVision, getPulse } from "./services/api";
import type { PulseSummary, VisionResponse } from "./types/api";
import { getDictionary, getSavedLanguage, type LanguageCode } from "./utils/i18n";

export default function App() {
  const [language, setLanguage] = useState<LanguageCode>(getSavedLanguage);
  const [state, setState] = useState("All India");
  const [category, setCategory] = useState("Education");
  const [name, setName] = useState("");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<VisionResponse | null>(null);
  const [pulse, setPulse] = useState<PulseSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const t = useMemo(() => getDictionary(language), [language]);
  const speech = useSpeech(language);

  useEffect(() => {
    localStorage.setItem("language", language);
  }, [language]);

  useEffect(() => {
    getPulse()
      .then(setPulse)
      .catch(() => setPulse(null));
  }, []);

  async function submitVision() {
    setError("");
    setLoading(true);
    try {
      const data = await generateVision({ name, question, language, state, category });
      setResult(data);
      speech.speak(data.response.summary_2047);
      getPulse()
        .then(setPulse)
        .catch(() => {});
    } catch (err) {
      setError(err instanceof Error ? err.message : "India AI is taking a little longer than expected. Please try again.");
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
      }
    );
  }

  return (
    <main>
      <Navbar language={language} setLanguage={setLanguage} t={t} />
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
      {error ? <p className="toast" role="alert">{error}</p> : null}
      {result ? (
        <>
          <AIResponse response={result.response} sources={result.sources} t={t} />
          <VisionCard card={result.response.card} name={name} language={language} t={t} />
        </>
      ) : null}
      <PulseDashboard pulse={pulse} t={t} />
      <Footer t={t} />
    </main>
  );
}

