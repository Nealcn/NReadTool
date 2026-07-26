@echo off
chcp 65001 >nul
title NReadTool

echo ========================================
echo   NReadTool — AI 陪伴阅读
echo ========================================
echo.

:: 启动后端
echo [1/2] 启动后端 (FastAPI)...
start "Backend" cmd /c "cd /d %~dp0backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"
if %errorlevel% neq 0 (
    echo   后端启动失败！
    pause
    exit /b
)
echo   后端 -> http://localhost:8000
echo.

:: 等待后端就绪
:wait_backend
timeout /t 2 /nobreak >nul
curl -s -o nul http://localhost:8000/api/v1/ai/health 2>nul
if %errorlevel% neq 0 goto wait_backend
echo   后端就绪 ✅
echo.

:: 启动前端
echo [2/2] 启动前端 (Next.js)...
start "Frontend" cmd /c "cd /d %~dp0frontend\apps\readest-app && pnpm dev-web"
echo   前端 -> http://localhost:3000
echo.

:: 等待前端就绪
:wait_frontend
timeout /t 2 /nobreak >nul
curl -s -o nul http://localhost:3000/ 2>nul
if %errorlevel% neq 0 goto wait_frontend
echo   前端就绪 ✅
echo.

echo ========================================
echo   启动完成！
echo.
echo   前端: http://localhost:3000
echo   后端: http://localhost:8000
echo   API: http://localhost:8000/docs
echo ========================================
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:3000
