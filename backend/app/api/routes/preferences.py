from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.schemas.preferences import PreferencesRead, PreferencesUpdate

router = APIRouter(prefix="/preferences", tags=["preferences"])


def _serialize_preferences(preferences: UserPreferences | None, user_id: int) -> PreferencesRead:
    if preferences is None:
        return PreferencesRead(user_id=user_id)

    settings = preferences.settings or {}
    return PreferencesRead(
        id=preferences.id,
        user_id=preferences.user_id,
        crypto_assets=preferences.preferred_coins or [],
        investor_type=preferences.risk_profile,
        content_preferences=settings.get("content_preferences", []),
        created_at=preferences.created_at,
        updated_at=preferences.updated_at,
    )


@router.get("", response_model=PreferencesRead)
def read_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PreferencesRead:
    preferences = db.scalar(select(UserPreferences).where(UserPreferences.user_id == current_user.id))
    return _serialize_preferences(preferences, current_user.id)


@router.put("", response_model=PreferencesRead)
def upsert_preferences(
    payload: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PreferencesRead:
    preferences = db.scalar(select(UserPreferences).where(UserPreferences.user_id == current_user.id))
    if preferences is None:
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)

    preferences.risk_profile = payload.investor_type
    preferences.preferred_coins = payload.crypto_assets
    preferences.settings = {"content_preferences": payload.content_preferences}

    db.commit()
    db.refresh(preferences)
    return _serialize_preferences(preferences, current_user.id)
