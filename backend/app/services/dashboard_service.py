from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.schemas.dashboard import CoinPricesSection, DashboardPreferencesSummary, DashboardResponse
from app.services.ai_service import get_ai_insight
from app.services.coingecko_service import get_coin_prices
from app.services.meme_service import get_crypto_meme
from app.services.news_service import get_market_news


def _preferences_summary(preferences: UserPreferences | None) -> DashboardPreferencesSummary:
    if preferences is None:
        return DashboardPreferencesSummary()

    settings = preferences.settings or {}
    return DashboardPreferencesSummary(
        crypto_assets=preferences.preferred_coins or [],
        investor_type=preferences.risk_profile,
        content_preferences=settings.get("content_preferences", []),
    )


def build_dashboard(db: Session, user: User) -> DashboardResponse:
    preferences = db.scalar(select(UserPreferences).where(UserPreferences.user_id == user.id))
    summary = _preferences_summary(preferences)

    sections = [
        get_market_news(summary.crypto_assets),
        get_coin_prices(summary.crypto_assets),
        get_ai_insight(db, summary.crypto_assets, summary.investor_type, summary.content_preferences),
        get_crypto_meme(),
    ]

    return DashboardResponse(
        user_id=user.id,
        generated_at=datetime.now(UTC),
        preferences=summary,
        sections=sections,
    )


def build_coin_prices_section(db: Session, user: User) -> CoinPricesSection:
    preferences = db.scalar(select(UserPreferences).where(UserPreferences.user_id == user.id))
    summary = _preferences_summary(preferences)
    return get_coin_prices(summary.crypto_assets)
