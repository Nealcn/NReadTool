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

- **18 个 REST API 接口**：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/devices/register` | 设备注册 |
| POST | `/api/v1/books/upload` | 上传 EPUB |
| GET | `/api/v1/books` | 书籍列表 |
| GET | `/api/v1/books/{id}` | 书籍详情 |
| PUT | `/api/v1/books/{id}` | 重命名 |
| PUT | `/api/v1/books/{id}/metadata` | 更新元数据 |
| DELETE | `/api/v1/books/{id}` | 删除（软删除） |
| GET | `/api/v1/books/{id}/toc` | 章节目录 |
| GET | `/api/v1/books/{id}/contents/{cid}` | 章节内容 |
| GET | `/api/v1/books/{id}/download` | 下载 EPUB |
| POST | `/api/v1/ai/explain` | AI 划词解读 |
| GET | `/api/v1/ai/health` | AI 健康检查 |
| GET/PUT/DELETE | `/api/v1/reading/progress/{id}` | 阅读进度 |
| POST/GET/PUT/DELETE | `/api/v1/books/{id}/annotations` | 标注 CRUD |
| GET/PUT | `/api/v1/settings` | 阅读设置 |
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| GET | `/api/v1/auth/me` | 当前用户 |

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

### P5: 云端同步 + 用户认证（3天）

**标注同步（2026-07-23）**
- `useCloudAnnotationSync` — 启动时拉取云端标注，合并到本地 booknotes 渲染到阅读器
- 按 CFI + type 去重，不会覆盖本地已有标注
- 自动推送本地新增标注到后端（8s 轮询）

**云端书库同步（2026-07-23）**
- `useCloudLibrarySync` — 双向同步：本地→云端（自动上传新书），云端→本地（自动下载导入）
- 每本书封面增加 ↑ 上传按钮，点击上传到后端 API
- `BookItem.tsx` — 新增 ↑ 图标按钮，调用 `getLocalBookFilename()` 获取文件路径

**OPFS 并发修复（2026-07-23）**
- `webAppService.ts` — `openDatabase` 换用 window 级缓存（`window.__READEST_DB_CACHE__`），解决 HMR 热更新导致类重置的问题
- 串行队列（Promise chain）防止并发注册 OPFS 文件句柄
- 出错重试（5 次，最长 6 秒），处理浏览器页面重载后的句柄残留

**清理 Supabase / 付费功能（2026-07-26）**
- 删除 `libs/payment/`、`pages/api/`、`utils/supabase.ts` 等 ~30 个文件
- 移除 npm 依赖 `@supabase/*`、`@stripe/*`、`stripe`
- 简化 `utils/access.ts` — 所有功能默认可用，移除配额/付费门控
- 简化 `AuthContext.tsx` — 去掉 Supabase，改用本地 JWT
- 保留必要存根（`nativeAuth.ts`、`conversionWorker.ts`）供 OAuth 流程引用

**后端用户认证（2026-07-26）**
- `User` 模型（id, email, username, password_hash, timestamps）
- `POST /api/v1/auth/register` — 注册，bcrypt 加密密码
- `POST /api/v1/auth/login` — 登录，返回 JWT（30 天过期）
- `GET /api/v1/auth/me` — 获取当前用户信息
- JWT 使用 `python-jose`，密钥从 config 读取

**前端登录页（2026-07-26）**
- `app/auth/page.tsx` — 登录/注册页面，Tailwind + DaisyUI 风格
- `services/api/auth.ts` — 认证 API 封装
- `api.ts` 请求拦截器 — 自动注入 `Authorization: Bearer` 和 `X-Device-Id`
- 登录/注册模式切换，成功后重定向回 `/library`

**书籍元数据编辑 API（2026-07-26）**
- `PUT /api/v1/books/{book_hash}/metadata` — 更新书名、作者、出版社、语言、ISBN、描述
- `BookMetadataUpdate` schema + `EpubService.update_metadata()`
- 前端编辑元数据保存后自动同步到后端

---



## 5. 所有改动清单

### 后端（自研，~35 个文件）

```
backend/
├── app/
│   ├── main.py                    # FastAPI 入口
│   ├── config.py                  # 全局配置（含 JWT 配置）
│   ├── dependencies.py            # 依赖注入（device_id + JWT）
│   ├── core/
│   │   ├── database.py            # SQLite WAL 模式
│   │   ├── exceptions.py          # 全局异常（含 auth 异常）
│   │   ├── response.py            # 统一响应格式
│   │   └── security.py            # 🆕 JWT + bcrypt 工具
│   ├── api/v1/
│   │   ├── books.py               # 书籍 CRUD + 元数据更新
│   │   ├── reading.py             # 阅读进度 API
│   │   ├── ai.py                  # AI 划词 API
│   │   ├── ai_chat.py             # AI 对话 API
│   │   ├── annotations.py         # 🆕 标注 CRUD API
│   │   ├── devices.py             # 设备注册 API
│   │   ├── settings.py            # 🆕 阅读设置 API
│   │   ├── auth.py                # 🆕 注册/登录/用户 API
│   │   ├── tts.py                 # TTS 代理 API
│   │   └── router.py              # 路由聚合
│   ├── models/
│   │   ├── device.py              # 设备模型
│   │   ├── book.py                # 书籍模型
│   │   ├── book_content.py        # 章节内容 + Spine 模型
│   │   ├── reading_progress.py    # 阅读进度模型
│   │   ├── annotation.py          # 🆕 标注模型
│   │   ├── ai.py                  # 🆕 AI 对话模型
│   │   ├── reading_setting.py     # 🆕 阅读设置模型
│   │   └── user.py                # 🆕 用户模型
│   ├── schemas/                   # Pydantic 校验模型（8个文件）
│   ├── services/
│   │   ├── device_service.py      # 设备管理
│   │   ├── epub_service.py        # EPUB 解析入库 + 元数据更新
│   │   ├── reading_service.py     # 阅读进度 UPSERT
│   │   ├── ai_service.py          # DeepSeek 调用 + Prompt 模板
│   │   ├── annotation_service.py  # 🆕 标注服务
│   │   ├── auth_service.py        # 🆕 用户认证服务
│   │   ├── reading_setting_service.py # 🆕 阅读设置服务
│   │   └── ai_chat_service.py     # 🆕 AI 对话服务
│   └── utils/
│       ├── epub_parser.py         # EPUB 解析引擎
│       └── file_utils.py          # SHA256 + 校验
├── alembic/                       # 数据库迁移
├── requirements.txt
└── .env
```

### 前端（新增/修改，~30 个文件）

```
frontend/apps/readest-app/src/
├── services/api/                  # 7个文件（自研 API 通信层）
│   ├── api.ts                     # axios 封装 + X-Device-Id + Bearer token
│   ├── books.ts                   # 书籍 CRUD + 元数据更新 API
│   ├── reading.ts                 # 进度 API
│   ├── ai.ts                      # AI 划词 + 对话 API
│   ├── auth.ts                    # 🆕 注册/登录 API
│   ├── annotations.ts             # 🆕 标注 API
│   └── devices.ts                 # 设备注册 API
├── hooks/
│   ├── useCloudLibrarySync.ts     # 🆕 云端书库双向同步（上传+下载）
│   ├── useAI.ts                   # AI 划词状态管理
│   ├── useReading.ts              # 阅读进度自动保存
│   └── useNetwork.ts              # 网络状态监听
├── app/reader/hooks/
│   ├── useCloudProgress.ts        # 云端进度同步
│   └── useCloudAnnotationSync.ts  # 🆕 云端标注同步（拉取+推送+合并）
├── app/auth/
│   └── page.tsx                   # 🆕 登录/注册页（Tailwind + DaisyUI）
├── app/library/components/
│   ├── CloudBooksDialog.tsx       # 云端书库对话框
│   └── BookItem.tsx               # 修改：↑ 上传按钮
├── app/reader/components/annotator/
│   ├── Annotator.tsx              # 修改：AI 解读
│   ├── AnnotationTools.tsx        # 修改：ai_explain 按钮
│   └── AIChatDialog.tsx           # 修改：预填不自动发送
├── services/ai/
│   ├── types.ts                   # 添加 deepseek 类型
│   ├── constants.ts               # 添加 DeepSeek 默认值
│   ├── providers/
│   │   ├── DeepSeekProvider.ts    # 🆕 DeepSeek Provider
│   │   └── index.ts              # 修改：注册 DeepSeek
│   └── adapters/
│       └── ReedyBackend.ts        # 修改：适配 DeepSeek
├── components/settings/
│   └── AIPanel.tsx                # DeepSeek 配置界面
├── context/
│   ├── AuthContext.tsx             # 🆕 重写：去掉 Supabase，用 JWT
│   ├── PHContext.tsx              # 修复 atob undefined
│   └── supabase.ts               # 已删除
├── services/webAppService.ts     # 修改：OPFS 并发修复
└── utils/
    ├── device.ts                  # 设备 UUID
    ├── access.ts                  # 🆕 简化：移除所有付费门控
    ├── fetch.ts                   # 🆕 简化：去掉 Supabase
    └── localCache.ts              # localStorage 封装
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

### ✅ 已完成（新增）

| 需求 | 说明 |
|------|------|
| 用户注册/登录 | JWT + bcrypt，登录页风格与主应用一致 |
| 云端标注同步 | 双向同步：拉取云端标注渲染到阅读器 + 推送本地新标注 |
| 云端书库同步 | 本地书自动上传到后端，云端书自动下载到本地 |
| 书籍元数据编辑 API | `PUT /metadata`，编辑保存后同步到后端 |
| OPFS 并发修复 | window 级缓存 + 串行队列 + 重试，解决 HMR 句柄冲突 |
| 付费功能清理 | 移除所有 Supabase/Stripe/配额相关代码 |

### ❌ 未实现

| 需求 | 优先级 |
|------|--------|
| 闲置自动关闭 | 低 |
| 无网络 AI 置灰 | 低 |
| 超出 2000 字友好提示 | 低 |
| 前端偏好缓存对接 | 低 |
| 阅读器对接后端存储层 | 中（核心体验提升） |
| Readest 原生 AI（RAG/全书搜索） | 中（需配置提供者） |
| 阅读统计 API | 中（跨设备聚合阅读时长） |
| 备份/恢复 API | 中（云端存储备份） |

### 🔮 二期规划

- 多角色 TTS 朗读
- AI 深度对话讨论（整书）
- 笔记/批注系统完善（跨设备合并、PDF 标注）
- 多端客户端适配（Tauri）
- 人物关系图谱
- 阅读数据统计

---

## 8. 剩余工作

### 短期可做

1. **前端对接后端存储层** — 把 Readest 的 `appService` 文件系统读写改成调 REST API
2. **登录/登出 UI** — 书库页面头部加登录按钮（现在只能直接访问 `/auth`）
3. **部署上线** — `pnpm build-web` + Nginx 反代
4. **清理存根文件** — Supabase 遗留的 `nativeAuth.ts`、`conversionWorker.ts` 等空存根（已部分完成）
5. **修复登录提交报错** — API 请求返回 HTML 格式的诊断和修复

### 后续方向

| 方向 | 说明 |
|------|------|
| **AI 深度对话（整书）** | 基于 RAG 的全书问答（Readest 原生 Reedy AI 已带，需向量库支持） |
| **TTS 朗读** | 后端已有 edge-tts 代理，前端集成读屏功能 |
| **书籍分享 API** | `POST /books/share` 生成公开分享链接 |
| **阅读统计 API** | `/stats` 端点聚合阅读时间、本数等 |
| **OPDS 订阅管理** | 后端代理 OPDS 请求，缓存 feed 列表 |
| **全文搜索 API** | 后端索引书籍内容，支持跨书搜索 |

### 部署方式

```bash
# 1. 编译前端
cd frontend/apps/readest-app
pnpm build-web    # 输出到 .next/

# 2. 后端启动
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. 或使用一键启动脚本
start.bat
```

### Readest AI 配置

打开 http://localhost:3000 → 设置 → AI：
1. 勾选 "Enable AI Assistant"
2. 选择 "DeepSeek"
3. 填入 API Key：`sk-f891bb7519b54a9daf79ce87b9c97473`
4. Embedding Model 留空（DeepSeek 不支持）

---

*最后更新：2026-07-26*
