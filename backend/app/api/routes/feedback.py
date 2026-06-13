from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackRead

router = APIRouter(prefix="/feedback", tags=["feedback"])


def _serialize_feedback(feedback: Feedback) -> FeedbackRead:
    return FeedbackRead(
        id=feedback.id,
        user_id=feedback.user_id,
        section_id=feedback.section_id,
        vote=feedback.vote,
        content_id=feedback.content_id,
        comment=feedback.message or None,
        created_at=feedback.created_at,
    )


@router.post("", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackRead:
    feedback = Feedback(
        user_id=current_user.id,
        category=payload.section_id,
        section_id=payload.section_id,
        content_id=payload.content_id,
        vote=payload.vote,
        message=payload.comment or "",
        metadata_={"source": "dashboard"},
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return _serialize_feedback(feedback)
