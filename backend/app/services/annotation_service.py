"""高亮/笔记服务"""

from typing import List
from sqlalchemy.orm import Session

from app.models.annotation import Annotation
from app.schemas.annotation import AnnotationCreate, AnnotationUpdate, AnnotationResponse


class AnnotationService:

    @staticmethod
    def create(db: Session, book_hash: str, device_id: str, req: AnnotationCreate) -> AnnotationResponse:
        annotation = Annotation(
            book_hash=book_hash,
            device_id=device_id,
            cfi=req.cfi,
            type=req.type,
            style=req.style,
            color=req.color,
            text=req.text,
            note=req.note,
        )
        db.add(annotation)
        db.commit()
        db.refresh(annotation)
        return AnnotationResponse.model_validate(annotation)

    @staticmethod
    def list_by_book(db: Session, book_hash: str, device_id: str) -> List[AnnotationResponse]:
        annotations = db.query(Annotation).filter(
            Annotation.book_hash == book_hash,
            Annotation.device_id == device_id,
        ).order_by(Annotation.created_at).all()
        return [AnnotationResponse.model_validate(a) for a in annotations]

    @staticmethod
    def update(db: Session, annotation_id: int, req: AnnotationUpdate) -> AnnotationResponse:
        annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
        if not annotation:
            raise Exception("Annotation not found")
        if req.style is not None:
            annotation.style = req.style
        if req.color is not None:
            annotation.color = req.color
        if req.note is not None:
            annotation.note = req.note
        db.commit()
        db.refresh(annotation)
        return AnnotationResponse.model_validate(annotation)

    @staticmethod
    def delete(db: Session, annotation_id: int) -> None:
        db.query(Annotation).filter(Annotation.id == annotation_id).delete()
        db.commit()
