# AI 陪伴阅读 (AI Companion Reader)

沉浸式阅读 + AI 智能辅助 —— 阅读优先、AI 辅助、无打扰、轻量化。

## 项目架构

```
bookread/
├── backend/          # Python FastAPI 后端
│   ├── app/
│   │   ├── api/v1/   # REST API 路由
│   │   ├── models/   # SQLAlchemy ORM 模型
│   │   ├── schemas/  # Pydantic 数据校验
│   │   ├── services/ # 业务逻辑层
│   │   ├── core/     # 基础设施（数据库、异常、响应）
│   │   └── utils/    # 工具（EPUB 解析等）
│   ├── storage/books/# EPUB 源文件存储
│   └── tests/
├── frontend/         # Fork 自 Readest (Next.js 15 + React + TypeScript)
│   ├── apps/readest-app/  # 主应用
│   └── packages/     # 共享库（foliate-js 等）
└── docs/
```

## MVP 核心功能

- **EPUB 文件上传**（单文件 ≤50MB，重复校验，自动解析）
- **沉浸式阅读**（原版排版，左右/上下翻页，字体/背景/亮度调节，章节目录）
- **AI 划词解释**（字词释义、句意解析、语法解读、背景拓展）
- **自动进度保存**（实时保存 + 云端持久化 + 本地缓存兜底）
- **书籍库管理**（列表展示、重命名、删除）

## 开发环境搭建

### 前置条件

- Python 3.10+
- Node.js 20+
- pnpm 9+

### 后端

```bash
# 安装依赖
cd backend && pip install -r requirements.txt

# 初始化数据库
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
# 安装依赖
cd frontend && pnpm install

# 启动开发服务器
pnpm dev
```

后端 API 文档地址：http://localhost:8000/docs

## 技术选型

| 层 | 技术 | 说明 |
|---|---|---|
| 后端 | Python FastAPI | REST API |
| 数据库 | SQLite + SQLAlchemy | ORM + WAL 模式 |
| 前端 | Next.js 15 + React + TypeScript | Fork Readest |
| AI | DeepSeek API | 兼容 OpenAI 格式 |
| 阅读渲染 | Foliate.js | EPUB 排版引擎 |

## 开发计划

| 阶段 | 内容 | 时间 |
|------|------|------|
| P0 | 基础设施搭建 | 3 天 |
| P1 | 核心后端开发 | 7 天 |
| P2 | 前端改造与集成 | 10 天 |
| P3 | AI 集成 | 3 天 |
| P4 | 联调测试与优化 | 5 天 |
| P5 | 验收与部署 | 2 天 |
