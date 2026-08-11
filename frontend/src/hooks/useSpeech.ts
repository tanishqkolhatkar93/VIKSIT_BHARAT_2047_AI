import { languages } from "../services/api";
import type { LanguageCode } from "../utils/i18n";

export type VoiceErrorCode = "unsupported" | "permission" | "network" | "noSpeech" | "failed";

type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  maxAlternatives: number;
  onresult:
    | ((event: { results: { [index: number]: { [index: number]: { transcript: string } } } }) => void)
    | null;
  onerror: ((event: { error: string }) => void) | null;
  start: () => void;
};

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

function getVoiceCode(language: LanguageCode) {
  return languages.find((item) => item.code === language)?.voice ?? "en-IN";
}

function mapError(error: string): VoiceErrorCode {
  if (error === "not-allowed" || error === "service-not-allowed") {
    return "permission";
  }
  if (error === "network") {
    return "network";
  }
  if (error === "no-speech") {
    return "noSpeech";
  }
  return "failed";
}

export function useSpeech(language: LanguageCode) {
  function listen(onText: (text: string) => void, onError: (code: VoiceErrorCode) => void) {
    const SpeechRecognitionApi = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!SpeechRecognitionApi) {
      onError("unsupported");
      return;
    }
    const recognition = new (SpeechRecognitionApi as SpeechRecognitionConstructor)();
    recognition.lang = getVoiceCode(language);
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => {
      onText(event.results[0][0].transcript);
    };
    recognition.onerror = (event) => {
      onError(mapError(event.error));
    };
    recognition.start();
  }

  function speak(text: string) {
    if (!("speechSynthesis" in window)) {
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = getVoiceCode(language);
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  }

  return { listen, speak };
}
