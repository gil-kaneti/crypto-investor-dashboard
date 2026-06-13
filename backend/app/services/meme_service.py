import json
import random
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.dashboard import MemeSection

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
MEMES_PATH = DATA_DIR / "memes.json"


def get_crypto_meme() -> MemeSection:
    with MEMES_PATH.open("r", encoding="utf-8") as file:
        memes = json.load(file)
    meme = random.choice(memes)
    return MemeSection(
        title="Fun Crypto Meme",
        source="static_json",
        is_fallback=False,
        generated_at=datetime.now(UTC),
        content_id=meme["content_id"],
        caption=meme["caption"],
        image_url=meme.get("image_url"),
        alt_text=meme["alt_text"],
    )
