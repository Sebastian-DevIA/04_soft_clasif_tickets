from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.dependencies import get_db
from backend.app.schemas.comments import CommentIn, CommentOut
from backend.app.services import comments as comments_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(payload: CommentIn, db: Session = Depends(get_db)) -> CommentOut:
    try:
        comment = comments_service.create_comment(db, payload)
    except Exception as exc:  # noqa: BLE001 - no exponer el traceback crudo al cliente
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo clasificar y guardar el comentario: {exc}",
        ) from exc
    return CommentOut.model_validate(comment)


@router.get("", response_model=list[CommentOut])
def list_comments(
    sentiment: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[CommentOut]:
    comments = comments_service.list_comments(
        db, sentiment=sentiment, limit=limit, offset=offset
    )
    return [CommentOut.model_validate(comment) for comment in comments]


@router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int, db: Session = Depends(get_db)) -> CommentOut:
    comment = comments_service.get_comment(db, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un comentario con id {comment_id}.",
        )
    return CommentOut.model_validate(comment)
