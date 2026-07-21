# AI陪伴阅读 — 开发环境命令

.PHONY: help backend frontend install-backend install-frontend run-backend run-frontend migrate reset-db

help:
	@echo "AI陪伴阅读 开发命令"
	@echo "======================"
	@echo "make install-backend  - 安装后端依赖"
	@echo "make install-frontend - 安装前端依赖"
	@echo "make run-backend      - 启动后端服务 (localhost:8000)"
	@echo "make run-frontend     - 启动前端开发服务器"
	@echo "make migrate          - 执行数据库迁移"
	@echo "make reset-db         - 重置数据库（删除后重建）"
	@echo "make format           - 格式化后端代码"

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

install-frontend:
	cd frontend && pnpm install

run-frontend:
	cd frontend && pnpm dev

# === All-in-one ===

install: install-backend install-frontend

dev: run-backend run-frontend
