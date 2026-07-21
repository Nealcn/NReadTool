"""阅读进度服务"""

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.exceptions import BookNotFoundException
from app.models.reading_progress import ReadingProgress
from app.models.book import Book
from app.schemas.reading import ReadingProgressRequest, ReadingProgressResponse


class ReadingService:
    """阅读进度管理"""

    @staticmethod
    def get_progress(db: Session, device_id: str, book_id: int) -> ReadingProgressResponse | None:
        """获取阅读进度"""
        # 验证书籍存在
        book = db.query(Book).filter(
            Book.id == book_id,
            Book.deleted_at.is_(None),
        ).first()
        if not book:
            raise BookNotFoundException()

        progress = db.query(ReadingProgress).filter(
            ReadingProgress.device_id == device_id,
            ReadingProgress.book_id == book_id,
        ).first()

        if not progress:
            return None

        return ReadingProgressResponse.model_validate(progress)

    @staticmethod
    def save_progress(
        db: Session, device_id: str, book_id: int, req: ReadingProgressRequest
    ) -> ReadingProgressResponse:
        """保存阅读进度（UPSERT）"""
        # 验证书籍存在
        book = db.query(Book).filter(
            Book.id == book_id,
            Book.deleted_at.is_(None),
        ).first()
        if not book:
            raise BookNotFoundException()

        # 使用 UPSERT 避免竞态
        stmt = text("""
            INSERT INTO reading_progress (device_id, book_id, spine_index, content_id, scroll_percent, updated_at)
            VALUES (:device_id, :book_id, :spine_index, :content_id, :scroll_percent, CURRENT_TIMESTAMP)
            ON CONFLICT(device_id, book_id) DO UPDATE SET
                spine_index = :spine_index,
                content_id = :content_id,
                scroll_percent = :scroll_percent,
                updated_at = CURRENT_TIMESTAMP
        """)
        db.execute(stmt, {
            "device_id": device_id,
            "book_id": book_id,
            "spine_index": req.spine_index,
            "content_id": req.content_id,
            "scroll_percent": req.scroll_percent,
        })
        db.commit()

        # 返回最新进度
        progress = db.query(ReadingProgress).filter(
            ReadingProgress.device_id == device_id,
            ReadingProgress.book_id == book_id,
        ).first()

        return ReadingProgressResponse.model_validate(progress)

    @staticmethod
    def clear_progress(db: Session, device_id: str, book_id: int) -> None:
        """清除阅读进度"""
        db.query(ReadingProgress).filter(
            ReadingProgress.device_id == device_id,
            ReadingProgress.book_id == book_id,
        ).delete()
        db.commit()
