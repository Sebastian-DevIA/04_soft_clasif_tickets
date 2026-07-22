from sqlalchemy.orm import Session

from backend.app.schemas.comments import CommentIn
from backend.app.services.classification import MODEL_VERSION, classify_text
from src.db.models import Comment, Prediction


def _latest_prediction(comment: Comment) -> Prediction | None:
    return max(comment.predictions, key=lambda p: p.predicted_at, default=None)


def create_comment(db: Session, payload: CommentIn) -> Comment:
    sentiment, confidence = classify_text(payload.text)

    comment = Comment(text=payload.text, source=payload.source)
    db.add(comment)
    db.flush()  # autoflush=False: necesitamos comment.id para la FK de Prediction

    prediction = Prediction(
        comment_id=comment.id,
        sentiment=sentiment,
        confidence=confidence,
        model_version=MODEL_VERSION,
    )
    db.add(prediction)
    db.commit()
    db.refresh(comment)

    comment.prediction = _latest_prediction(comment)
    return comment


def list_comments(
    db: Session,
    sentiment: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Comment]:
    query = db.query(Comment)
    if sentiment is not None:
        query = query.join(Prediction).filter(Prediction.sentiment == sentiment)

    comments = (
        query.order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()
    )
    for comment in comments:
        comment.prediction = _latest_prediction(comment)
    return comments


def get_comment(db: Session, comment_id: int) -> Comment | None:
    comment = db.get(Comment, comment_id)
    if comment is not None:
        comment.prediction = _latest_prediction(comment)
    return comment
