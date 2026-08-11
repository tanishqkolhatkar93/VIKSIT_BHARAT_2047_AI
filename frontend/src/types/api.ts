export type Source = {
  title: string;
  source: string;
  url: string;
  category: string;
  state: string;
  date: string;
};

export type VisionCardData = {
  theme: string;
  beneficiaries: string[];
  technology: string[];
  impact: string;
  quote: string;
  shareableVision?: string | null;
};

export type VisionPayload = {
  vision: string;
  opportunities: string[];
  role_of_ai: string;
  role_of_technology: string;
  potential_impact: string;
  challenges: string[];
  action_plan: string[];
  summary_2047: string;
  fact_scenario_note: string;
  card: VisionCardData;
};

export type VisionResponse = {
  cached: boolean;
  question_hash: string;
  response: VisionPayload;
  sources: Source[];
};

export type CountItem = {
  name: string;
  count: number;
};

export type TrendItem = {
  category: string;
  state: string;
};

export type PulseSummary = {
  totalVisions: number;
  popularCategories: CountItem[];
  popularStates: CountItem[];
  languageDistribution: CountItem[];
  recentTrends: TrendItem[];
  message: string;
};

export type PublicCard = {
  id: string;
  name: string;
  theme: string;
  impact: string;
  quote: string;
  shareableVision: string | null;
  tags: string[];
  language: string;
  share_url: string;
  image_url: string;
};

