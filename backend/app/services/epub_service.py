"""EPUB 解析与入库服务 — 主键改为 file_hash"""

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
from app.utils.epub_parser import EpubParser
from app.utils.file_utils import compute_sha256


class EpubService:

    @staticmethod
    def check_duplicate(db: Session, file_hash: str) -> None:
        """检查重复文件"""
        existing = db.query(Book).filter(
            Book.file_hash == file_hash,
            Book.deleted_at.is_(None),
        ).first()
        if existing:
            raise DuplicateFileException()

    @staticmethod
    def save_uploaded_file(upload_path: str, file_hash: str) -> str:
        """将上传文件保存到存储目录"""
        storage_dir = os.path.join(settings.STORAGE_DIR, file_hash)
        os.makedirs(storage_dir, exist_ok=True)
        dest_path = os.path.join(storage_dir, f"{file_hash}.epub")
        shutil.copy2(upload_path, dest_path)
        return dest_path

    @staticmethod
    def import_epub(
        db: Session,
        file_path: str,
        file_name: str,
        file_hash: str,
        file_size: int,
    ) -> BookInfo:
        """解析 EPUB 并入库"""
        parser = EpubParser(file_path)
        result = parser.parse()

        book = Book(
            file_hash=file_hash,
            title=result.metadata.title or file_name.replace(".epub", ""),
            author=result.metadata.author,
            publisher=result.metadata.publisher,
            language=result.metadata.language or "zh",
            isbn=result.metadata.isbn,
            description=result.metadata.description,
            file_name=file_name,
            file_size=file_size,
            file_path=file_path,
            total_chapters=len(result.chapters),
            total_words=sum(c.word_count for c in result.chapters),
        )
        db.add(book)
        db.flush()

        if result.cover_image:
            import base64
            book.cover_image = base64.b64encode(result.cover_image).decode("utf-8")

        stored_path = EpubService.save_uploaded_file(file_path, file_hash)
        book.file_path = stored_path

        for i, chapter in enumerate(result.chapters):
            content = BookContent(
                book_hash=file_hash,
                spine_index=i,
                chapter_title=chapter.plain_text[:100] if chapter.plain_text else f"第{i+1}节",
                href=chapter.href,
                html_content=chapter.html_content,
                plain_text=chapter.plain_text,
                word_count=chapter.word_count,
            )
            db.add(content)
            db.flush()

            spine = BookSpine(
                book_hash=file_hash,
                spine_index=i,
                content_id=content.id,
            )
            db.add(spine)

        db.commit()
        db.refresh(book)
        return BookInfo.model_validate(book)

    @staticmethod
    def get_book_list(db: Session) -> List[BookInfo]:
        """获取所有未删除的书籍"""
        books = db.query(Book).filter(
            Book.deleted_at.is_(None),
        ).order_by(Book.updated_at.desc()).all()
        return [BookInfo.model_validate(b) for b in books]

    @staticmethod
    def get_book(db: Session, file_hash: str) -> Book:
        """获取书籍详情"""
        book = db.query(Book).filter(
            Book.file_hash == file_hash,
            Book.deleted_at.is_(None),
        ).first()
        if not book:
            raise BookNotFoundException()
        return book

    @staticmethod
    def rename_book(db: Session, file_hash: str, title: str) -> Book:
        """重命名书籍"""
        book = EpubService.get_book(db, file_hash)
        book.title = title
        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def update_metadata(
        db: Session,
        file_hash: str,
        title: str | None = None,
        author: str | None = None,
        publisher: str | None = None,
        language: str | None = None,
        isbn: str | None = None,
        description: str | None = None,
        cover_image: str | None = None,
    ) -> Book:
        """更新书籍元数据"""
        book = EpubService.get_book(db, file_hash)
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if publisher is not None:
            book.publisher = publisher
        if language is not None:
            book.language = language
        if isbn is not None:
            book.isbn = isbn
        if description is not None:
            book.description = description
        if cover_image is not None:
            book.cover_image = cover_image
        db.commit()
        db.refresh(book)
        return book

    @staticmethod
    def delete_book(db: Session, file_hash: str) -> None:
        """软删除书籍"""
        book = EpubService.get_book(db, file_hash)
        book.deleted_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def get_toc(db: Session, file_hash: str) -> List[dict]:
        """获取章节目录"""
        EpubService.get_book(db, file_hash)
        spines = db.query(BookSpine).filter(
            BookSpine.book_hash == file_hash,
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
    def get_chapter_content(db: Session, book_hash: str, content_id: int) -> BookContent:
        """获取章节内容"""
        EpubService.get_book(db, book_hash)
        content = db.query(BookContent).filter(
            BookContent.id == content_id,
            BookContent.book_hash == book_hash,
        ).first()
        if not content:
            raise BookNotFoundException("章节内容不存在")
        return content
