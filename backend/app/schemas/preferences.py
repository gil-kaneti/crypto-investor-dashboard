from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.schemas.timestamps import utc_z_timestamp


class PreferencesBase(BaseModel):
    crypto_assets: list[str] = Field(default_factory=list)
    investor_type: str | None = Field(default=None, max_length=50)
    content_preferences: list[str] = Field(default_factory=list)

    @field_validator("crypto_assets", "content_preferences")
    @classmethod
    def normalize_list_values(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value.strip()]

    @field_validator("investor_type")
    @classmethod
    def normalize_investor_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class PreferencesUpdate(PreferencesBase):
    pass


class PreferencesRead(PreferencesBase):
    id: int | None = None
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_serializer("created_at", "updated_at")
    def serialize_timestamps(self, value: datetime | None) -> str | None:
        return utc_z_timestamp(value)

    model_config = ConfigDict(from_attributes=True)
