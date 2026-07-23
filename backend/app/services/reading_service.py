"""阅读进度服务 — FK 改为 file_hash"""

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.exceptions import BookNotFoundException
from app.models.reading_progress import ReadingProgress
from app.models.book import Book
from app.schemas.reading import ReadingProgressRequest, ReadingProgressResponse


class ReadingService:

    @staticmethod
    def get_progress(db: Session, device_id: str, book_hash: str) -> ReadingProgressResponse | None:
        book = db.query(Book).filter(
            Book.file_hash == book_hash,
            Book.deleted_at.is_(None),
        ).first()
        if not book:
            raise BookNotFoundException()

        progress = db.query(ReadingProgress).filter(
            ReadingProgress.device_id == device_id,
            ReadingProgress.book_hash == book_hash,
        ).first()
        if not progress:
            return None
        return ReadingProgressResponse.model_validate(progress)

    @staticmethod
    def save_progress(
        db: Session, device_id: str, book_hash: str, req: ReadingProgressRequest
    ) -> ReadingProgressResponse:
        book = db.query(Book).filter(
            Book.file_hash == book_hash,
            Book.deleted_at.is_(None),
        ).first()
        if not book:
            raise BookNotFoundException()

        stmt = text("""
            INSERT INTO reading_progress (device_id, book_hash, spine_index, content_id, scroll_percent, updated_at)
            VALUES (:device_id, :book_hash, :spine_index, :content_id, :scroll_percent, CURRENT_TIMESTAMP)
            ON CONFLICT(device_id, book_hash) DO UPDATE SET
                spine_index = :spine_index,
                content_id = :content_id,
                scroll_percent = :scroll_percent,
                updated_at = CURRENT_TIMESTAMP
        """)
        db.execute(stmt, {
            "device_id": device_id,
            "book_hash": book_hash,
            "spine_index": req.spine_index,
            "content_id": req.content_id,
            "scroll_percent": req.scroll_percent,
        })
        db.commit()

        progress = db.query(ReadingProgress).filter(
            ReadingProgress.device_id == device_id,
            ReadingProgress.book_hash == book_hash,
        ).first()
        return ReadingProgressResponse.model_validate(progress)

    @staticmethod
    def clear_progress(db: Session, device_id: str, book_hash: str) -> None:
        db.query(ReadingProgress).filter(
            ReadingProgress.device_id == device_id,
            ReadingProgress.book_hash == book_hash,
        ).delete()
        db.commit()
