"""全局配置管理"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "sqlite:///./data/bookread.db"

    # 文件存储
    STORAGE_DIR: str = "./storage/books"
    FILE_MAX_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set[str] = {".epub"}

    # DeepSeek AI
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    AI_MODEL: str = "deepseek-chat"
    AI_MAX_TOKENS: int = 1000
    AI_REQUEST_TIMEOUT: int = 30

    # 服务器
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 限流
    AI_RATE_LIMIT: int = 10  # 次/分钟/设备

    # JWT 认证
    JWT_SECRET_KEY: str = "nreadtool-dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 720  # 30 天

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
