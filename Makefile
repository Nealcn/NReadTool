# AI陪伴阅读 — 开发环境命令

.PHONY: help backend frontend install-backend install-frontend run-backend run-frontend-dev migrate reset-db setup

help:
	@echo "AI陪伴阅读 开发命令"
	@echo "======================"
	@echo ""
	@echo "--- 后端 ---"
	@echo "make install-backend    - 安装后端依赖"
	@echo "make run-backend        - 启动后端服务 (localhost:8000)"
	@echo "make migrate            - 执行数据库迁移"
	@echo "make reset-db           - 重置数据库（删除后重建）"
	@echo ""
	@echo "--- 前端 ---"
	@echo "make setup-frontend     - 初始化前端子模块 + 安装依赖"
	@echo "make install-frontend   - 安装前端依赖"
	@echo "make run-frontend       - 启动前端开发服务器 (localhost:3000)"
	@echo "make run-frontend-web   - 以 Web 模式启动前端"
	@echo ""
	@echo "--- 其他 ---"
	@echo "make format            - 格式化后端代码"

# === 后端 ===

install-backend:
	cd backend && pip install -r requirements.txt

run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	cd backend && alembic upgrade head

migrate-new:
	cd backend && alembic revision --autogenerate -m "$(name)"

reset-db:
	cd backend && rm -f data/bookread.db && alembic upgrade head

format:
	cd backend && pip install black && black app/ tests/

# === 前端 ===

setup-frontend:
	cd frontend && git submodule update --init --depth 1 packages/foliate-js && pnpm install

install-frontend:
	cd frontend && pnpm install

run-frontend:
	cd frontend/apps/readest-app && pnpm dev

run-frontend-web:
	cd frontend/apps/readest-app && pnpm dev-web

# === 其他 ===

env:
	@echo "请确保以下环境变量已配置："
	@echo "  backend/.env: DEEPSEEK_API_KEY"
	@echo "  frontend/apps/readest-app/.env.local: NEXT_PUBLIC_API_BASE_URL"
