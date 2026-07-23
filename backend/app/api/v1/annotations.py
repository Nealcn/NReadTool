"""高亮/笔记接口"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_device_id
from app.schemas.common import success, ApiResponse
from app.schemas.annotation import AnnotationCreate, AnnotationUpdate
from app.services.annotation_service import AnnotationService

router = APIRouter(prefix="/books", tags=["高亮笔记"])


@router.post("/{book_hash}/annotations", response_model=ApiResponse)
async def create_annotation(book_hash: str, req: AnnotationCreate, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    ann = AnnotationService.create(db, book_hash, device_id, req)
    return success(data=ann.model_dump(), message="创建成功")


@router.get("/{book_hash}/annotations", response_model=ApiResponse)
async def list_annotations(book_hash: str, device_id: str = Depends(get_device_id), db: Session = Depends(get_db)):
    anns = AnnotationService.list_by_book(db, book_hash, device_id)
    return success(data=[a.model_dump() for a in anns])


@router.put("/annotations/{annotation_id}", response_model=ApiResponse)
async def update_annotation(annotation_id: int, req: AnnotationUpdate, db: Session = Depends(get_db)):
    ann = AnnotationService.update(db, annotation_id, req)
    return success(data=ann.model_dump())


@router.delete("/annotations/{annotation_id}", response_model=ApiResponse)
async def delete_annotation(annotation_id: int, db: Session = Depends(get_db)):
    AnnotationService.delete(db, annotation_id)
    return success(message="删除成功")
