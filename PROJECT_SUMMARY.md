# NReadTool 项目总结

> 基于 Readest Fork 的 AI 陪伴阅读系统 — 完整开发记录

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术选型](#2-技术选型)
3. [架构设计](#3-架构设计)
4. [开发过程](#4-开发过程)
5. [所有改动清单](#5-所有改动清单)
6. [关键发现](#6-关键发现)
7. [当前状态 vs 需求](#7-当前状态-vs-需求)
8. [剩余工作](#8-剩余工作)

---

## 1. 项目概述

**目标**：基于 Readest 开源项目 Fork，打造一个前后端分离的 AI 陪伴阅读系统。

**核心定位**：阅读优先，AI 辅助，无打扰、轻量化、易操作。

**仓库地址**：https://github.com/Nealcn/NReadTool

**需求文档**：[req.md](req.md)

---

## 2. 技术选型

| 层 | 技术 | 说明 |
|---|---|---|
| **前端** | Next.js 15 + React 19 + TypeScript | Fork 自 [Readest](https://github.com/readest/readest) v0.11.20 |
| **阅读引擎** | Foliate-js | EPUB 排版渲染 |
| **后端** | Python FastAPI | REST API |
| **数据库** | SQLite + SQLAlchemy ORM | WAL 模式 |
| **AI** | DeepSeek API（OpenAI 兼容模式） | 4 种 Prompt 模板 |
| **前后端通信** | REST + axios | 统一 X-Device-Id 标识 |

---

## 3. 架构设计

```
用户 → Nginx
        ├── /api/* → FastAPI → SQLite
        │                 ↓
        │           DeepSeek API
        │
        └── /* → 前端静态文件 (Next.js SSG)

Monorepo 结构:
  bookread/
  ├── backend/        # Python FastAPI 自研后端
  ├── frontend/       # Fork 自 Readest
  │   ├── apps/readest-app/  # 主应用
  │   └── packages/          # foliate-js 等共享库
  └── docs/
```

---

## 4. 开发过程

### P0: 基础设施搭建（3天）

- 创建 Monorepo 目录结构（`backend/` + `frontend/`）
- FastAPI 后端骨架（config、database、exceptions、response）
- SQLAlchemy ORM 模型（5 张表）
- Alembic 数据库迁移（SQLite WAL 模式）
- Fork Readest，清理非 MVP 模块（auth、API 代理、书城、OPDS、Stripe 等）
- 开发环境脚本（Makefile、README、.gitignore）

### P1: 后端核心开发（7天）

- **数据库设计**：
  - `devices` — 设备信息（device_id UUID 唯一标识）
  - `books` — 书籍元信息（SHA256 哈希去重、软删除）
  - `book_contents` — 章节内容（html_content + plain_text 双字段）
  - `book_spine` — 阅读顺序索引
  - `reading_progress` — 阅读进度（device_id + book_id 联合唯一）

- **EPUB 解析引擎**（`backend/app/utils/epub_parser.py`）：
  - 技术栈：`zipfile` + `lxml` + `BeautifulSoup`
  - 支持 EPUB 2/3 标准
  - 7 步流水线：文件校验 → SHA256 → container.xml → OPF → spine → 章节提取 → 结构化入库
  - 6 种异常场景：损坏、加密、格式异常、解析失败、空文件等

- **11 个 REST API 接口**：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/devices/register` | 设备注册 |
| POST | `/api/v1/books/upload` | 上传 EPUB |
| GET | `/api/v1/books` | 书籍列表 |
| GET | `/api/v1/books/{id}` | 书籍详情 |
| PUT | `/api/v1/books/{id}` | 重命名 |
| DELETE | `/api/v1/books/{id}` | 删除（软删除） |
| GET | `/api/v1/books/{id}/toc` | 章节目录 |
| GET | `/api/v1/books/{id}/contents/{cid}` | 章节内容 |
| GET | `/api/v1/books/{id}/download` | 下载 EPUB |
| POST | `/api/v1/ai/explain` | AI 划词解读 |
| GET | `/api/v1/ai/health` | AI 健康检查 |
| GET/PUT/DELETE | `/api/v1/reading/progress/{id}` | 阅读进度 |

- **DeepSeek AI 集成**：
  - 4 套 Prompt 模板（字词释义、句意解析、语法解读、背景拓展）
  - 2000 字截断、30s 超时
  - 无缓存、无知识库、实时调用

### P2: 前端改造（10天）

**自定义新增模块**：

```
frontend/apps/readest-app/src/
├── services/api/
│   ├── api.ts          # axios 实例 + X-Device-Id 拦截器
│   ├── books.ts        # 书籍 CRUD API
│   ├── reading.ts      # 阅读进度 API
│   ├── ai.ts           # AI 划词 + 对话 API
│   └── devices.ts      # 设备注册 API
├── hooks/
│   ├── useAI.ts        # AI 划词逻辑
│   ├── useReading.ts   # 阅读进度自动保存/恢复
│   └── useNetwork.ts   # 网络状态监听
├── components/ai/
│   ├── AIFloatingBall.tsx   # （已删除，合并到工具栏）
│   ├── AIChatDialog.tsx     # AI 对话对话框（来自 GitHub 合并）
│   └── NetworkIndicator.tsx # （已删除）
├── app/reader/hooks/
│   └── useCloudProgress.ts  # 云端进度同步
├── app/library/components/
│   └── CloudBooksDialog.tsx # 云端书库（上传+列表+操作菜单）
└── utils/
    ├── device.ts       # 设备 UUID
    ├── localCache.ts   # localStorage 封装
    └── textUtils.ts    # 文本截断工具
```

**Readest 现有组件修改**：

| 文件 | 改动 |
|------|------|
| `AnnotationTools.tsx` | 新增 `ai_explain` 按钮类型 |
| `Annotator.tsx` | 接入 AI 解读 API + 结果弹窗 |
| `annotationToolbar.ts` | 注册 ai_explain 到工具栏 |
| `types/annotator.ts` | 添加 ai_explain 类型 |
| `page.tsx` (library) | 接入云端书库对话框 |
| `ImportMenu.tsx` | 添加 Cloud Books 菜单项 |
| `LibraryHeader.tsx` | 透传 onOpenCloudBooks |
| `FoliateViewer.tsx` | 集成云端进度同步 |

**编译修复**：
- 修复 PHContext.tsx 中 `atob` undefined 问题
- 修复 supabase.ts 中 `atob` undefined 问题
- 创建缺失模块空桩文件（auth、opds、vendor）
- 添加 supabase 占位 URL

### P3: DeepSeek 集成到 Readest 原生 AI 系统

将 DeepSeek 作为 Readest AI（Reedy）的一个提供者接入：

| 文件 | 改动 |
|------|------|
| `types.ts` | 添加 `'deepseek'` 到 AIProviderName |
| `types.ts` | 添加 deepseekApiKey/BaseUrl/Model/EmbeddingModel 设置字段 |
| `providers/DeepSeekProvider.ts` | 🆕 完整的 DeepSeek Provider 实现 |
| `providers/index.ts` | 注册 DeepSeek 到工厂函数 |
| `constants.ts` | 添加 DeepSeek 默认设置 |
| `AIPanel.tsx` | 添加 DeepSeek 单选按钮 + 配置表单 + 保存逻辑 |
| `ReedyBackend.ts` | 适配 DeepSeek 空 embedding 处理 |

### P4: 联调测试

所有 11 个后端端点 + 前端 AI 功能测试通过。

---

## 5. 所有改动清单

### 后端（自研，~30 个文件）

```
backend/
├── app/
│   ├── main.py                    # FastAPI 入口
│   ├── config.py                  # 全局配置
│   ├── dependencies.py            # 依赖注入
│   ├── api/v1/
│   │   ├── books.py               # 书籍 CRUD API
│   │   ├── reading.py             # 阅读进度 API
│   │   ├── ai.py                  # AI 划词 API
│   │   ├── devices.py             # 设备注册 API
│   │   └── router.py              # 路由聚合
│   ├── models/
│   │   ├── device.py              # 设备模型
│   │   ├── book.py                # 书籍模型
│   │   ├── book_content.py        # 章节内容 + Spine 模型
│   │   └── reading_progress.py    # 阅读进度模型
│   ├── schemas/                   # Pydantic 校验模型（5个文件）
│   ├── services/
│   │   ├── device_service.py      # 设备管理
│   │   ├── epub_service.py        # EPUB 解析入库
│   │   ├── reading_service.py     # 阅读进度 UPSERT
│   │   └── ai_service.py          # DeepSeek 调用 + Prompt 模板
│   ├── core/
│   │   ├── database.py            # SQLite WAL 模式
│   │   ├── exceptions.py          # 全局异常
│   │   └── response.py            # 统一响应格式
│   └── utils/
│       ├── epub_parser.py         # EPUB 解析引擎
│       └── file_utils.py          # SHA256 + 校验
├── alembic/                       # 数据库迁移
├── requirements.txt
└── .env
```

### 前端（新增/修改，~20 个文件）

```
frontend/apps/readest-app/src/
├── services/api/                  # 5个文件（自研 API 通信层）
│   ├── api.ts                     # axios 封装
│   ├── books.ts                   # 书籍 API
│   ├── reading.ts                 # 进度 API
│   ├── ai.ts                      # AI 划词 + 对话 API
│   └── devices.ts                 # 设备注册 API
├── hooks/                         # 3个文件（自定义 Hooks）
│   ├── useAI.ts                   # AI 划词状态管理
│   ├── useReading.ts              # 阅读进度自动保存
│   └── useNetwork.ts              # 网络状态监听
├── app/reader/hooks/
│   └── useCloudProgress.ts        # 云端进度同步 Hook
├── app/library/components/
│   └── CloudBooksDialog.tsx       # 云端书库对话框（3点菜单支持导入/重命名/删除）
├── app/reader/components/annotator/
│   ├── Annotator.tsx              # 修改：添加 AI 解读
│   ├── AnnotationTools.tsx        # 修改：添加 ai_explain 按钮
│   └── AIChatDialog.tsx           # 修改：预填不自动发送
├── services/ai/
│   ├── types.ts                   # 修改：添加 deepseek 类型
│   ├── constants.ts               # 修改：添加 DeepSeek 默认值
│   ├── providers/
│   │   ├── DeepSeekProvider.ts    # 🆕 DeepSeek Provider
│   │   └── index.ts              # 修改：注册 DeepSeek
│   └── adapters/
│       └── ReedyBackend.ts        # 修改：适配 DeepSeek
├── components/settings/
│   └── AIPanel.tsx                # 修改：DeepSeek 配置界面
├── utils/
│   ├── device.ts                  # 设备 UUID
│   ├── localCache.ts              # localStorage 封装
│   └── textUtils.ts               # 文本截断工具
├── context/
│   ├── PHContext.tsx              # 修复 atob undefined
│   └── supabase.ts               # 修复 atob undefined + 占位 URL
└── annotationToolbar.ts           # 修改：添加 ai_explain + sanitize 强制注入
```

---

## 6. 关键发现

### Readest 原装 AI 系统（Reedy）

Readest 内置了一个完整的 AI 助手系统 "Reedy"，功能包括：

| 能力 | 说明 |
|------|------|
| **全书搜索** | 语义 + 文本混合搜索，返回带锚点的段落引用 |
| **章节总结** | 自动提取当前章节要点 |
| **深度问答** | 基于 RAG 的整书理解 |
| **引用定位** | 回答中带 CFI 锚点，点击跳转书中位置 |
| **防剧透** | 只回答已读内容 |
| **记忆系统** | 跨会话记住用户偏好和书籍要点 |
| **工具调用** | 11 个工具（getReadingContext、lookupPassage、navigateToCfi 等）|

**存储位置**（全部本地）：

| 数据 | Web 版 | 桌面版 |
|------|--------|--------|
| 书籍切片 + 向量 | IndexedDB (`reedy` 数据库) | `reedy.db` (SQLite 文件) |
| 对话记录 | IndexedDB (`ai-store`) | 同上 |
| AI 设置 | IndexedDB (`settings.json`) | JSON 文件 |

### Readest 前端大的原因

`node_modules` ~500MB，因为包含：
- Foliate-js 渲染引擎（C WASM）
- Tauri 原生壳（Windows/macOS/Linux/iOS/Android）
- AI 系统（Reedy + RAG + 向量库）
- 云同步（Supabase/Google Drive/OneDrive/WebDAV）
- TTS 朗读（多引擎）
- 词典系统、全文搜索、Stripe 支付

**实际上传到服务器的编译产物仅 30-50MB**。

### DeepSeek API 配置

```
API 地址: https://api.deepseek.com/v1
模型: deepseek-chat
API Key: sk-f891bb7519b54a9daf79ce87b9c97473
兼容格式: OpenAI 兼容（可用 openai Python SDK）
```

注意：DeepSeek **不支持 embedding API**，因此 RAG/向量搜索功能不可用，但不影响对话和划词解读。

---

## 7. 当前状态 vs 需求

### ✅ 已完成

| 需求 | 说明 |
|------|------|
| EPUB 文件上传 | 50MB、重复校验、损坏报错、自动解析入库 |
| 沉浸式阅读 | Readest 原生渲染、翻页、样式、目录 |
| 阅读样式设置 | 字体、背景色、亮度、翻页模式 |
| 章节目录跳转 | 原生支持 |
| AI 划词解读 | 4 种 Prompt 模板，集成到选中工具栏 |
| 2000 字截断 | 后端 + 前端双重截断 |
| 自动进度保存 | 云端 + 本地双重，节流同步 |
| 书籍库管理 | 列表展示、上传、重命名、删除 |
| 云端书库 | 独立对话框，完整 CRUD 操作 |
| 设备 UUID | 游客模式，无账号 |
| DeepSeek AI 提供者 | 已接入 Readest 原生 AI 系统 |
| 前后端分离架构 | REST API + 标准化接口 |

### ❌ 未实现

| 需求 | 优先级 |
|------|--------|
| 闲置自动关闭 | 低 |
| 无网络 AI 置灰 | 低 |
| 超出 2000 字友好提示 | 低 |
| 前端偏好缓存对接 | 低 |
| 阅读器对接后端存储层 | 中（核心体验提升） |
| Readest 原生 AI（RAG/全书搜索） | 中（需配置提供者） |

### 🔮 二期规划

- 多角色 TTS 朗读
- AI 深度对话讨论（整书）
- 笔记/批注系统
- 多端客户端适配（Tauri）
- 人物关系图谱
- 阅读数据统计

---

## 8. 剩余工作

### 短期可做

1. **前端对接后端存储层** — 把 Readest 的 `appService` 文件系统读写改成调我们的 REST API，这样上传→书库→阅读→进度全线打通
2. **完善 AI 体验** — 截断提示、拖拽弹窗、网络状态
3. **部署上线** — `pnpm build-web` + Nginx 反代

### 部署方式

```bash
# 1. 编译前端
cd frontend/apps/readest-app
pnpm build-web    # 输出到 .next/

# 2. 服务端配置
Nginx 托管静态文件 + 反代 /api/* 到 FastAPI
FastAPI + Uvicorn + SQLite
```

### Readest AI 配置

打开 http://localhost:3000 → 设置 → AI：
1. 勾选 "Enable AI Assistant"
2. 选择 "DeepSeek"
3. 填入 API Key：`sk-f891bb7519b54a9daf79ce87b9c97473`
4. Embedding Model 留空（DeepSeek 不支持）

---

*最后更新：2026-07-23*
