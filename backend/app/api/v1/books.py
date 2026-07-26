"""书籍管理接口 — 主键改为 file_hash"""

import os, tempfile, hashlib
from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import InvalidFileTypeException, FileTooLargeException
from app.schemas.common import success, ApiResponse
from app.schemas.book import (
    BookInfo, BookDetail, BookRenameRequest, BookMetadataUpdate,
    TOCResponse, TOCItem, ChapterContent, BookListResponse,
)
from app.services.epub_service import EpubService
from app.utils.file_utils import validate_file_extension, validate_file_size

router = APIRouter(prefix="/books", tags=["书籍管理"])


@router.post("/upload", response_model=ApiResponse)
async def upload_book(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """上传 EPUB 文件，用文件 hash 标识"""
    if not file.filename or not validate_file_extension(file.filename):
        raise InvalidFileTypeException()

    content = await file.read()
    file_size = len(content)
    if not validate_file_size(file_size):
        raise FileTooLargeException()

    file_hash = hashlib.sha256(content).hexdigest()
    EpubService.check_duplicate(db, file_hash)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        book = EpubService.import_epub(
            db=db, file_path=tmp_path, file_name=file.filename,
            file_hash=file_hash, file_size=file_size,
        )
        return success(data=book.model_dump(), message="上传成功")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@router.get("", response_model=ApiResponse)
async def get_book_list(db: Session = Depends(get_db)):
    """获取书籍列表"""
    books = EpubService.get_book_list(db)
    return success(data=BookListResponse(
        books=[b.model_dump() for b in books],
        total=len(books),
    ).model_dump())


@router.get("/{book_hash}", response_model=ApiResponse)
async def get_book_detail(book_hash: str, db: Session = Depends(get_db)):
    """获取书籍详情"""
    book = EpubService.get_book(db, book_hash)
    return success(data=BookDetail.model_validate(book).model_dump())


@router.put("/{book_hash}", response_model=ApiResponse)
async def rename_book(book_hash: str, req: BookRenameRequest, db: Session = Depends(get_db)):
    """重命名书籍"""
    book = EpubService.rename_book(db, book_hash, req.title)
    return success(data=BookInfo.model_validate(book).model_dump(), message="重命名成功")


@router.put("/{book_hash}/metadata", response_model=ApiResponse)
async def update_book_metadata(
    book_hash: str, req: BookMetadataUpdate, db: Session = Depends(get_db),
):
    """更新书籍元数据（书名、作者、出版社、语言、ISBN、描述、封面等）"""
    book = EpubService.update_metadata(
        db, book_hash,
        title=req.title,
        author=req.author,
        publisher=req.publisher,
        language=req.language,
        isbn=req.isbn,
        description=req.description,
        cover_image=req.cover_image,
    )
    return success(data=BookDetail.model_validate(book).model_dump(), message="元数据更新成功")


@router.delete("/{book_hash}", response_model=ApiResponse)
async def delete_book(book_hash: str, db: Session = Depends(get_db)):
    """删除书籍（软删除）"""
    EpubService.delete_book(db, book_hash)
    return success(message="删除成功")


@router.get("/{book_hash}/toc", response_model=ApiResponse)
async def get_book_toc(book_hash: str, db: Session = Depends(get_db)):
    """获取章节目录"""
    items = EpubService.get_toc(db, book_hash)
    return success(data=TOCResponse(book_hash=book_hash, items=[TOCItem(**i) for i in items]).model_dump())


@router.get("/{book_hash}/contents/{content_id}", response_model=ApiResponse)
async def get_chapter_content(book_hash: str, content_id: int, db: Session = Depends(get_db)):
    """获取章节内容"""
    content = EpubService.get_chapter_content(db, book_hash, content_id)
    return success(data=ChapterContent(
        spine_index=content.spine_index,
        title=content.chapter_title,
        html_content=content.html_content,
    ).model_dump())


@router.get("/{book_hash}/download")
async def download_book(book_hash: str, db: Session = Depends(get_db)):
    """下载 EPUB 源文件"""
    book = EpubService.get_book(db, book_hash)
    if not os.path.exists(book.file_path):
        return JSONResponse(status_code=404, content={"code": 40008, "message": "文件不存在", "data": None})
    return FileResponse(path=book.file_path, filename=book.file_name or f"{book.title}.epub", media_type="application/epub+zip")
