"""书籍管理接口"""

import tempfile
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import InvalidFileTypeException, FileTooLargeException
from app.schemas.common import success, ApiResponse
from app.schemas.book import (
    BookInfo,
    BookDetail,
    BookRenameRequest,
    TOCResponse,
    TOCItem,
    ChapterContent,
    BookListResponse,
)
from app.services.epub_service import EpubService
from app.utils.file_utils import validate_file_extension, validate_file_size, compute_sha256

router = APIRouter(prefix="/books", tags=["书籍管理"])


@router.post("/upload", response_model=ApiResponse)
async def upload_book(
    file: UploadFile = File(...),
    device_id: str = Form(...),
    db: Session = Depends(get_db),
):
    """上传 EPUB 文件"""
    # 文件类型校验
    if not file.filename or not validate_file_extension(file.filename):
        raise InvalidFileTypeException()

    # 文件大小校验
    content = await file.read()
    file_size = len(content)
    if not validate_file_size(file_size):
        raise FileTooLargeException()

    # 计算哈希
    import hashlib
    file_hash = hashlib.sha256(content).hexdigest()

    # 重复校验
    EpubService.check_duplicate(db, file_hash, device_id, file.filename)

    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 解析入库
        book = EpubService.import_epub(
            db=db,
            file_path=tmp_path,
            file_name=file.filename,
            file_hash=file_hash,
            file_size=file_size,
            upload_device_id=device_id,
        )
        return success(data=book.model_dump(), message="上传成功")
    finally:
        # 清理临时文件
        import os
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@router.get("", response_model=ApiResponse)
async def get_book_list(
    device_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """获取书籍列表"""
    books = EpubService.get_book_list(db, device_id)
    return success(data=BookListResponse(
        books=[b.model_dump() for b in books],
        total=len(books),
    ).model_dump())


@router.get("/{book_id}", response_model=ApiResponse)
async def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    """获取书籍详情"""
    book = EpubService.get_book(db, book_id)
    return success(data=BookDetail.model_validate(book).model_dump())


@router.put("/{book_id}", response_model=ApiResponse)
async def rename_book(
    book_id: int,
    req: BookRenameRequest,
    db: Session = Depends(get_db),
):
    """重命名书籍"""
    book = EpubService.rename_book(db, book_id, req.title)
    return success(data=BookInfo.model_validate(book).model_dump(), message="重命名成功")


@router.delete("/{book_id}", response_model=ApiResponse)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    """删除书籍（软删除）"""
    EpubService.delete_book(db, book_id)
    return success(message="删除成功")


@router.get("/{book_id}/toc", response_model=ApiResponse)
async def get_book_toc(book_id: int, db: Session = Depends(get_db)):
    """获取章节目录"""
    items = EpubService.get_toc(db, book_id)
    return success(data=TOCResponse(book_id=book_id, items=[TOCItem(**i) for i in items]).model_dump())


@router.get("/{book_id}/contents/{content_id}", response_model=ApiResponse)
async def get_chapter_content(
    book_id: int,
    content_id: int,
    db: Session = Depends(get_db),
):
    """获取章节内容"""
    content = EpubService.get_chapter_content(db, book_id, content_id)
    return success(data=ChapterContent(
        spine_index=content.spine_index,
        title=content.chapter_title,
        html_content=content.html_content,
    ).model_dump())


@router.get("/{book_id}/download")
async def download_book(book_id: int, db: Session = Depends(get_db)):
    """下载 EPUB 源文件"""
    book = EpubService.get_book(db, book_id)
    if not os.path.exists(book.file_path):
        return JSONResponse(
            status_code=404,
            content={"code": 40008, "message": "文件不存在", "data": None},
        )
    return FileResponse(
        path=book.file_path,
        filename=book.file_name or f"{book.title}.epub",
        media_type="application/epub+zip",
    )
