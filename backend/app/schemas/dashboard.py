from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_serializer

from app.schemas.timestamps import utc_z_timestamp

SectionId = Literal["market_news", "coin_prices", "ai_insight", "crypto_meme"]


class DashboardSectionBase(BaseModel):
    section_id: SectionId
    title: str
    source: str
    is_fallback: bool = False
    generated_at: datetime

    @field_serializer("generated_at")
    def serialize_generated_at(self, value: datetime) -> str:
        return utc_z_timestamp(value)


class NewsItem(BaseModel):
    content_id: str
    title: str
    url: str | None = None
    source: str
    published_at: datetime | None = None
    summary: str | None = None

    @field_serializer("published_at")
    def serialize_published_at(self, value: datetime | None) -> str | None:
        return utc_z_timestamp(value)


class MarketNewsSection(DashboardSectionBase):
    section_id: Literal["market_news"] = "market_news"
    items: list[NewsItem] = Field(default_factory=list)


class CoinPriceItem(BaseModel):
    content_id: str
    symbol: str
    name: str
    price_usd: float | None = None
    change_24h_percent: float | None = None
    market_cap_usd: float | None = None


class CoinPricesSection(DashboardSectionBase):
    section_id: Literal["coin_prices"] = "coin_prices"
    items: list[CoinPriceItem] = Field(default_factory=list)


class AIInsightSection(DashboardSectionBase):
    section_id: Literal["ai_insight"] = "ai_insight"
    content_id: str
    insight: str
    disclaimer: str


class MemeSection(DashboardSectionBase):
    section_id: Literal["crypto_meme"] = "crypto_meme"
    content_id: str
    caption: str
    image_url: str | None = None
    alt_text: str


class DashboardPreferencesSummary(BaseModel):
    crypto_assets: list[str] = Field(default_factory=list)
    investor_type: str | None = None
    content_preferences: list[str] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    user_id: int
    generated_at: datetime
    preferences: DashboardPreferencesSummary
    sections: list[MarketNewsSection | CoinPricesSection | AIInsightSection | MemeSection]

    @field_serializer("generated_at")
    def serialize_generated_at(self, value: datetime) -> str:
        return utc_z_timestamp(value)
