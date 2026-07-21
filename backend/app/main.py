"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.database import engine, Base
from app.core.exceptions import AppException, app_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：创建数据库表 & 存储目录
    Base.metadata.create_all(bind=engine)
    Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="AI 陪伴阅读 API",
    description="AI-powered companion reading API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP 阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理器
app.add_exception_handler(AppException, app_exception_handler)


# 注册路由
from app.api.v1.router import api_router  # noqa: E402
app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
