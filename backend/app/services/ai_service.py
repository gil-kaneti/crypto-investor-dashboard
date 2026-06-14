from datetime import UTC, datetime, timedelta
from hashlib import sha256
import logging

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_insight_cache import AIInsightCache
from app.schemas.dashboard import AIInsightSection

logger = logging.getLogger(__name__)

DISCLAIMER = "Educational information only. Not financial advice."
OPENROUTER_SYSTEM_PROMPT = (
    "You write safe, general crypto education for a dashboard. "
    "Return only the final dashboard insight, not instructions, reasoning, or analysis. "
    "Write 2 to 4 short sentences in plain text only. "
    "Do not use markdown, bullet points, headings, or prompt-instruction language. "
    "Do not include phrases like 'we need to', 'the user is', or 'I should'. "
    "Do not include price predictions, buy/sell/hold advice, trade instructions, entry or exit points, "
    "or breakout/rally signals. "
    "Keep the insight educational, general, and focused on context, risk awareness, or learning."
)
PROMPT_LEAK_PHRASES = (
    "we need to",
    "plain text only",
    "no markdown",
    "the user is",
    "i should",
)
FALLBACK_INSIGHT = (
    "A useful crypto dashboard habit is to separate price movement from thesis movement. "
    "Short-term volatility can be noisy, while adoption, liquidity, developer activity, "
    "security events, and macro conditions may give better context for long-term decisions."
)


def _fallback_section() -> AIInsightSection:
    # Keep the dashboard useful without consuming paid/free AI quota or exposing users to failed provider calls.
    return AIInsightSection(
        title="AI Insight of the Day",
        source="safe_fallback",
        is_fallback=True,
        generated_at=datetime.now(UTC),
        content_id="ai-insight-fallback",
        insight=FALLBACK_INSIGHT,
        disclaimer=DISCLAIMER,
    )


def _cache_key(crypto_assets: list[str], investor_type: str | None) -> str:
    today = datetime.now(UTC).date().isoformat()
    assets = ",".join(sorted(asset.strip().lower() for asset in crypto_assets if asset.strip()))
    return f"daily:{today}:{investor_type or 'general'}:{assets or 'default'}"


def _build_user_context(crypto_assets: list[str], investor_type: str | None, content_preferences: list[str]) -> str:
    assets = ", ".join(crypto_assets[:5]) or "Bitcoin, Ethereum, and Solana"
    profile = investor_type or "general crypto investor"
    content = ", ".join(content_preferences[:5]) or "market news, prices, learning, and humor"
    return f"User profile: {profile}. Preferred assets: {assets}. Content interests: {content}."


def _looks_like_prompt_leak(insight: str) -> bool:
    normalized = insight.lower()
    return any(phrase in normalized for phrase in PROMPT_LEAK_PHRASES)


def _extract_openrouter_insight(payload: dict) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        logger.warning("OpenRouter AI insight fallback: unexpected response shape choices_type=%s", type(choices).__name__)
        return ""

    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        logger.warning("OpenRouter AI insight fallback: unexpected response shape message_type=%s", type(message).__name__)
        return ""

    content = message.get("content")
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = [part.get("text", "") for part in content if isinstance(part, dict)]
        insight = " ".join(part.strip() for part in parts if part.strip()).strip()
        if not insight:
            logger.warning("OpenRouter AI insight fallback: unexpected response shape content_list_text_empty")
        return insight

    logger.warning("OpenRouter AI insight fallback: unexpected response shape content_type=%s", type(content).__name__)
    return ""


def get_ai_insight(
    db: Session,
    crypto_assets: list[str],
    investor_type: str | None,
    content_preferences: list[str],
) -> AIInsightSection:
    key = _cache_key(crypto_assets, investor_type)
    cached = db.scalar(
        select(AIInsightCache).where(
            AIInsightCache.cache_key == key,
            AIInsightCache.expires_at > datetime.now(UTC),
        )
    )
    if cached is not None:
        return AIInsightSection(
            title="AI Insight of the Day",
            source=(cached.metadata_ or {}).get("source", "openrouter_cache"),
            is_fallback=False,
            generated_at=cached.created_at,
            content_id=f"ai-insight-{cached.id}",
            insight=cached.response_text,
            disclaimer=DISCLAIMER,
        )

    logger.info(
        "OpenRouter AI insight config: api_key_configured=%s model=%s",
        bool(settings.openrouter_api_key),
        settings.openrouter_model,
    )

    if not settings.openrouter_api_key:
        logger.warning("OpenRouter AI insight fallback: missing OPENROUTER_API_KEY")
        return _fallback_section()

    user_context = _build_user_context(crypto_assets, investor_type, content_preferences)
    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openrouter_model,
                "messages": [
                    {"role": "system", "content": OPENROUTER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_context},
                ],
                "max_tokens": 90,
                "temperature": 0.4,
            },
            timeout=12.0,
        )
        response.raise_for_status()
        payload = response.json()
        insight = _extract_openrouter_insight(payload)
    except httpx.HTTPStatusError as exc:
        response_text = exc.response.text.replace("\n", " ")[:300]
        logger.warning(
            "OpenRouter AI insight fallback: http_status=%s response_text=%s",
            exc.response.status_code,
            response_text,
        )
        return _fallback_section()
    except Exception as exc:
        logger.warning("OpenRouter AI insight fallback: exception_type=%s", type(exc).__name__)
        return _fallback_section()

    if not insight:
        logger.warning("OpenRouter AI insight fallback: empty response text")
        return _fallback_section()

    if _looks_like_prompt_leak(insight):
        logger.warning("OpenRouter AI insight fallback: prompt leak detected")
        return _fallback_section()

    cache = AIInsightCache(
        cache_key=key,
        prompt_hash=sha256(user_context.encode("utf-8")).hexdigest(),
        response_text=insight,
        metadata_={"source": "openrouter", "model": settings.openrouter_model},
        expires_at=datetime.now(UTC) + timedelta(hours=24),
    )
    db.add(cache)
    db.commit()
    db.refresh(cache)

    return AIInsightSection(
        title="AI Insight of the Day",
        source="openrouter",
        is_fallback=False,
        generated_at=cache.created_at,
        content_id=f"ai-insight-{cache.id}",
        insight=insight,
        disclaimer=DISCLAIMER,
    )
