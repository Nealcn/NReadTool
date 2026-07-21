"""EPUB 解析与入库服务"""

import os
import shutil
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import BookNotFoundException, DuplicateFileException
from app.models.book import Book
from app.models.book_content import BookContent, BookSpine
from app.schemas.book import BookInfo
from app.utils.epub_parser import EpubParser, EpubResult
from app.utils.file_utils import compute_sha256


class EpubService:
    """EPUB 解析与入库服务"""

    @staticmethod
    def check_duplicate(db: Session, file_hash: str, upload_device_id: str, file_name: str) -> None:
        """检查重复文件"""
        # 同名 + 同设备
        existing_by_name = db.query(Book).filter(
            Book.file_name == file_name,
            Book.upload_device_id == upload_device_id,
            Book.deleted_at.is_(None),
        ).first()
        if existing_by_name:
            raise DuplicateFileException()

        # 同哈希
        existing_by_hash = db.query(Book).filter(
            Book.file_hash == file_hash,
            Book.deleted_at.is_(None),
        ).first()
        if existing_by_hash:
            raise DuplicateFileException()

    @staticmethod
    def save_uploaded_file(upload_path: str, book_id: int) -> str:
        """将上传文件保存到存储目录"""
        storage_dir = os.path.join(settings.STORAGE_DIR, str(book_id))
        os.makedirs(storage_dir, exist_ok=True)
        dest_path = os.path.join(storage_dir, f"{book_id}.epub")
        shutil.copy2(upload_path, dest_path)
        return dest_path

    @staticmethod
    def import_epub(
        db: Session,
        file_path: str,
        file_name: str,
        file_hash: str,
        file_size: int,
        upload_device_id: str,
    ) -> BookInfo:
        """解析 EPUB 并入库"""
        # 1. 解析 EPUB
        parser = EpubParser(file_path)
        result = parser.parse()

        # 2. 创建书籍记录
        book = Book(
            title=result.metadata.title or file_name.replace(".epub", ""),
            author=result.metadata.author,
            publisher=result.metadata.publisher,
            language=result.metadata.language or "zh",
            isbn=result.metadata.isbn,
            description=result.metadata.description,
            file_name=file_name,
            file_hash=file_hash,
            file_size=file_size,
            file_path=file_path,
            total_chapters=len(result.chapters),
            total_words=sum(c.word_count for c in result.chapters),
            upload_device_id=upload_device_id,
        )
        db.add(book)
        db.flush()  # 获取 book.id

        # 3. 保存封面
        if result.cover_image:
            import base64
            book.cover_image = base64.b64encode(result.cover_image).decode("utf-8")

        # 4. 存储源文件
        stored_path = EpubService.save_uploaded_file(file_path, book.id)
        book.file_path = stored_path

        # 5. 存储章节内容
        for i, chapter in enumerate(result.chapters):
            content = BookContent(
                book_id=book.id,
                spine_index=i,
                chapter_title=chapter.plain_text[:100] if chapter.plain_text else f"第{i+1}节",
                href=chapter.href,
                html_content=chapter.html_content,
                plain_text=chapter.plain_text,
                word_count=chapter.word_count,
            )
            db.add(content)
            db.flush()

            # 6. 记录 spine
            spine = BookSpine(
                book_id=book.id,
                spine_index=i,
                content_id=content.id,
            )
            db.add(spine)

        db.commit()
        db.refresh(book)
        return BookInfo.model_validate(book)

    @staticmethod
    def get_book_list(db: Session, device_id: str) -> List[BookInfo]:
        """获取书籍列表"""
        books = db.query(Book).filter(
            Book.upload_device_id == device_id,
            Book.deleted_at.is_(None),
        ).order_by(Book.updated_at.desc()).all()
        return [BookInfo.model_validate(b) for b in books]

    @staticmethod
    def get_book(db: Session, book_id: int) -> Book:
        """获取书籍详情"""
        book = db.query(Book).filter(
            Book.id == book_id,
            Book.deleted_at.is_(None),
        ).first()
        if not book:
            raise BookNotFoundException()
        return book

    @staticmethod
    def rename_book(db: Session, book_id: int, title: str) -> Book:
        """重命名书籍"""
        book = EpubService.get_book(db, book_id)
        book.title = title
        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def delete_book(db: Session, book_id: int) -> None:
        """软删除书籍"""
        book = EpubService.get_book(db, book_id)
        book.deleted_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def get_toc(db: Session, book_id: int) -> List[dict]:
        """获取章节目录"""
        # 验证书籍存在
        EpubService.get_book(db, book_id)

        spines = db.query(BookSpine).filter(
            BookSpine.book_id == book_id,
        ).order_by(BookSpine.spine_index).all()

        toc = []
        for spine in spines:
            content = db.query(BookContent).filter(
                BookContent.id == spine.content_id,
            ).first()
            title = content.chapter_title if content else f"章节{spine.spine_index + 1}"
            toc.append({
                "spine_index": spine.spine_index,
                "content_id": spine.content_id,
                "title": title,
            })

        return toc

    @staticmethod
    def get_chapter_content(db: Session, book_id: int, content_id: int) -> BookContent:
        """获取章节内容"""
        EpubService.get_book(db, book_id)
        content = db.query(BookContent).filter(
            BookContent.id == content_id,
            BookContent.book_id == book_id,
        ).first()
        if not content:
            raise BookNotFoundException("章节内容不存在")
        return content
