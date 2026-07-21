"""自定义异常与全局异常处理器"""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """业务异常基类"""

    def __init__(self, code: int, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


class FileTooLargeException(AppException):
    def __init__(self):
        super().__init__(code=40001, message="文件大小超过限制（最大 50MB）")


class InvalidFileTypeException(AppException):
    def __init__(self):
        super().__init__(code=40002, message="不支持的文件格式，仅支持 EPUB 格式")


class DuplicateFileException(AppException):
    def __init__(self):
        super().__init__(code=40003, message="该书已在书库中，请勿重复上传")


class FileCorruptedException(AppException):
    def __init__(self):
        super().__init__(code=40004, message="文件已损坏，请重新下载后上传")


class FileEncryptedException(AppException):
    def __init__(self):
        super().__init__(code=40005, message="文件已加密/受保护，暂不支持该格式")


class ParseFailedException(AppException):
    def __init__(self):
        super().__init__(code=40006, message="文件解析失败，请确认是否为标准 EPUB 格式")


class BookNotFoundException(AppException):
    def __init__(self):
        super().__init__(code=40007, message="书籍不存在", status_code=404)


class AIRequestTimeoutException(AppException):
    def __init__(self):
        super().__init__(code=50001, message="AI 服务繁忙，请稍后重试", status_code=504)


class AIRateLimitException(AppException):
    def __init__(self):
        super().__init__(code=50002, message="请求过于频繁，请稍后再试", status_code=429)


class AIServiceUnavailableException(AppException):
    def __init__(self):
        super().__init__(code=50003, message="AI 服务暂不可用", status_code=503)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )
