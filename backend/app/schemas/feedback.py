from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.schemas.dashboard import SectionId
from app.schemas.timestamps import utc_z_timestamp

FeedbackVote = Literal["thumbs_up", "thumbs_down"]


class FeedbackCreate(BaseModel):
    section_id: SectionId
    vote: FeedbackVote
    content_id: str | None = Field(default=None, max_length=255)
    comment: str | None = Field(default=None, max_length=1000)

    @field_validator("content_id", "comment")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class FeedbackRead(BaseModel):
    id: int
    user_id: int | None
    section_id: SectionId
    vote: FeedbackVote
    content_id: str | None = None
    comment: str | None = None
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return utc_z_timestamp(value)

    model_config = ConfigDict(from_attributes=True)
