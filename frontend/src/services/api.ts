import type { PublicCard, PulseSummary, VisionResponse } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export const languages = [
  { code: "en", name: "English", voice: "en-IN" },
  { code: "hi", name: "हिन्दी", voice: "hi-IN" },
  { code: "te", name: "తెలుగు", voice: "te-IN" },
  { code: "ta", name: "தமிழ்", voice: "ta-IN" },
  { code: "mr", name: "मराठी", voice: "mr-IN" },
  { code: "bn", name: "বাংলা", voice: "bn-IN" },
  { code: "gu", name: "ગુજરાતી", voice: "gu-IN" },
  { code: "kn", name: "ಕನ್ನಡ", voice: "kn-IN" },
  { code: "ml", name: "മലയാളം", voice: "ml-IN" },
  { code: "pa", name: "ਪੰਜਾਬੀ", voice: "pa-IN" },
  { code: "or", name: "ଓଡ଼ିଆ", voice: "or-IN" }
] as const;

export const states = [
  "All India", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
  "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
  "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
  "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
  "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
  "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi",
  "Jammu & Kashmir", "Ladakh", "Puducherry", "Chandigarh", "Other"
];

export const categories = [
  "Agriculture", "Education", "Healthcare", "Employment", "Technology",
  "Infrastructure", "Environment", "Climate", "Smart Cities",
  "Rural Development", "Women Empowerment", "Entrepreneurship",
  "Digital India", "Manufacturing", "Transportation", "Energy",
  "Space & Science"
];

export async function generateVision(payload: {
  name: string;
  question: string;
  language: string;
  state: string;
  category: string;
  api_key?: string | null;
  model?: string | null;
}): Promise<VisionResponse> {
  const body: Record<string, unknown> = {
    name: payload.name,
    question: payload.question,
    language: payload.language,
    state: payload.state,
    category: payload.category,
  };
  if (payload.api_key) {
    body.api_key = payload.api_key.trim();
  }
  if (payload.model) {
    body.model = payload.model.trim();
  }
  const response = await fetch(`${API_BASE_URL}/api/v1/vision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "India AI is taking a little longer than expected. Please try again.");
  }
  return response.json();
}

export type GeminiTestResult = {
  connected: boolean;
  model: string | null;
  message: string;
};

export async function testGeminiKey(apiKey: string): Promise<GeminiTestResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/gemini/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey.trim() }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Could not reach the connection service. Please try again.");
  }
  return response.json();
}

export async function getPulse(): Promise<PulseSummary> {
  const response = await fetch(`${API_BASE_URL}/api/v1/pulse`);
  if (!response.ok) {
    throw new Error("Failed to load pulse data.");
  }
  return response.json();
}

export async function createPublicCard(payload: {
  name: string;
  theme: string;
  impact: string;
  quote: string;
  shareableVision?: string | null;
  tags: string[];
  language: string;
  image: string;
}): Promise<PublicCard> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cards`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Could not create your shareable card.");
  }
  return response.json();
}

export async function getPublicCard(cardId: string): Promise<PublicCard> {
  const response = await fetch(`${API_BASE_URL}/api/v1/cards/${cardId}`);
  if (!response.ok) {
    throw new Error("Card not found.");
  }
  return response.json();
}

