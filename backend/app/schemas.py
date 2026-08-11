from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str
    source: str
    url: str
    category: str
    state: str
    date: str


class VisionRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    question: str = Field(..., min_length=8, max_length=800)
    language: str = Field(default="en", min_length=2, max_length=5)
    state: str = Field(default="All India", max_length=80)
    category: str = Field(default="Technology", max_length=80)


class VisionCard(BaseModel):
    theme: str
    beneficiaries: list[str]
    technology: list[str]
    impact: str
    quote: str
    shareableVision: str | None = None


class VisionPayload(BaseModel):
    vision: str
    opportunities: list[str]
    role_of_ai: str
    role_of_technology: str
    potential_impact: str
    challenges: list[str]
    action_plan: list[str]
    summary_2047: str
    fact_scenario_note: str
    card: VisionCard


class VisionResponse(BaseModel):
    cached: bool
    question_hash: str
    response: VisionPayload
    sources: list[Source]


class CountItem(BaseModel):
    name: str
    count: int


class TrendItem(BaseModel):
    category: str
    state: str


class PulseSummary(BaseModel):
    totalVisions: int
    popularCategories: list[CountItem]
    popularStates: list[CountItem]
    languageDistribution: list[CountItem]
    recentTrends: list[TrendItem]
    message: str


class CreateCardRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    theme: str = Field(..., max_length=80)
    impact: str = Field(..., max_length=300)
    quote: str = Field(..., min_length=1, max_length=500)
    shareableVision: str | None = Field(default=None, max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=5)
    language: str = Field(default="en", min_length=2, max_length=5)
    image: str = Field(..., min_length=20, max_length=8_000_000)


class PublicCard(BaseModel):
    id: str
    name: str
    theme: str
    impact: str
    quote: str
    shareableVision: str | None
    tags: list[str]
    language: str
    share_url: str
    image_url: str

