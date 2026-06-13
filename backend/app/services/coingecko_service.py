from datetime import UTC, datetime
from time import sleep

import httpx

from app.core.config import settings
from app.schemas.dashboard import CoinPriceItem, CoinPricesSection

COIN_ID_MAP = {
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "eth": "ethereum",
    "ethereum": "ethereum",
    "sol": "solana",
    "solana": "solana",
    "ada": "cardano",
    "cardano": "cardano",
    "doge": "dogecoin",
    "dogecoin": "dogecoin",
    "xrp": "ripple",
    "ripple": "ripple",
    "bnb": "binancecoin",
    "binance coin": "binancecoin",
}

DEFAULT_COIN_IDS = ["bitcoin", "ethereum", "solana"]
COINGECKO_TIMEOUT_SECONDS = 8.0
COINGECKO_RETRY_DELAY_SECONDS = 0.3

FALLBACK_PRICES = {
    "bitcoin": CoinPriceItem(
        content_id="price-bitcoin",
        symbol="BTC",
        name="Bitcoin",
        price_usd=65000,
        change_24h_percent=0.0,
        market_cap_usd=1_280_000_000_000,
    ),
    "ethereum": CoinPriceItem(
        content_id="price-ethereum",
        symbol="ETH",
        name="Ethereum",
        price_usd=3500,
        change_24h_percent=0.0,
        market_cap_usd=420_000_000_000,
    ),
    "solana": CoinPriceItem(
        content_id="price-solana",
        symbol="SOL",
        name="Solana",
        price_usd=150,
        change_24h_percent=0.0,
        market_cap_usd=70_000_000_000,
    ),
    "cardano": CoinPriceItem(
        content_id="price-cardano",
        symbol="ADA",
        name="Cardano",
        price_usd=0.45,
        change_24h_percent=0.0,
        market_cap_usd=16_000_000_000,
    ),
}

_last_successful_sections: dict[tuple[str, ...], CoinPricesSection] = {}


def _coin_ids_from_preferences(crypto_assets: list[str]) -> list[str]:
    coin_ids: list[str] = []
    for asset in crypto_assets:
        coin_id = COIN_ID_MAP.get(asset.strip().lower())
        if coin_id and coin_id not in coin_ids:
            coin_ids.append(coin_id)
    return coin_ids or DEFAULT_COIN_IDS


def _fallback_section(coin_ids: list[str]) -> CoinPricesSection:
    items = [FALLBACK_PRICES[coin_id] for coin_id in coin_ids if coin_id in FALLBACK_PRICES]
    if not items:
        items = list(FALLBACK_PRICES.values())
    return CoinPricesSection(
        title="Coin Prices",
        source="fallback",
        is_fallback=True,
        generated_at=datetime.now(UTC),
        items=items,
    )


def _cache_key(coin_ids: list[str]) -> tuple[str, ...]:
    return tuple(coin_ids)


def _cached_section(coin_ids: list[str]) -> CoinPricesSection | None:
    cached = _last_successful_sections.get(_cache_key(coin_ids))
    if cached is None:
        return None
    return cached.model_copy(update={"source": "coingecko_cached", "is_fallback": True}, deep=True)


def _live_section(payload: list[dict]) -> CoinPricesSection | None:
    items = [
        CoinPriceItem(
            content_id=f"price-{coin.get('id')}",
            symbol=str(coin.get("symbol", "")).upper(),
            name=str(coin.get("name", "")),
            price_usd=coin.get("current_price"),
            change_24h_percent=coin.get("price_change_percentage_24h"),
            market_cap_usd=coin.get("market_cap"),
        )
        for coin in payload
        if coin.get("id") and coin.get("symbol") and coin.get("name")
    ]

    if not items:
        return None

    return CoinPricesSection(
        title="Coin Prices",
        source="coingecko",
        is_fallback=False,
        generated_at=datetime.now(UTC),
        items=items,
    )


def _fetch_coingecko_prices(coin_ids: list[str], headers: dict[str, str]) -> list[dict]:
    response = httpx.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params={
            "vs_currency": "usd",
            "ids": ",".join(coin_ids),
            "price_change_percentage": "24h",
        },
        headers=headers,
        timeout=COINGECKO_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def get_coin_prices(crypto_assets: list[str]) -> CoinPricesSection:
    coin_ids = _coin_ids_from_preferences(crypto_assets)
    headers = {}
    if settings.coingecko_api_key:
        headers["x-cg-demo-api-key"] = settings.coingecko_api_key

    for attempt in range(2):
        try:
            section = _live_section(_fetch_coingecko_prices(coin_ids, headers))
            if section is not None:
                _last_successful_sections[_cache_key(coin_ids)] = section
                return section
        except Exception:
            if attempt == 0:
                sleep(COINGECKO_RETRY_DELAY_SECONDS)

    return _cached_section(coin_ids) or _fallback_section(coin_ids)
