import bn from "../locales/bn.json";
import en from "../locales/en.json";
import gu from "../locales/gu.json";
import hi from "../locales/hi.json";
import kn from "../locales/kn.json";
import ml from "../locales/ml.json";
import mr from "../locales/mr.json";
import od from "../locales/or.json";
import pa from "../locales/pa.json";
import ta from "../locales/ta.json";
import te from "../locales/te.json";

const dictionaries = { en, hi, te, ta, mr, bn, gu, kn, ml, pa, or: od };

export type LanguageCode = keyof typeof dictionaries;
export type Dictionary = typeof en;

export function getDictionary(language: LanguageCode): Dictionary {
  return dictionaries[language] ?? dictionaries.en;
}

export function getSavedLanguage(): LanguageCode {
  const value = localStorage.getItem("language");
  if (value && value in dictionaries) {
    return value as LanguageCode;
  }
  return "en";
}

