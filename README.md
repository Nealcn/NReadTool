# NReadTool — AI 陪伴阅读

**阅读优先、AI 辅助、轻量化、易操作**

基于 [Readest](https://github.com/readest/readest) (Next.js 15 + React + TypeScript + Tauri) Fork 并改造的前后端分离阅读平台。

---

## 项目架构

```
NReadTool/
├── backend/                    # Python FastAPI 自研后端
│   ├── app/
│   │   ├── api/v1/            # REST API 路由层
│   │   ├── models/            # SQLAlchemy ORM 模型
│   │   ├── schemas/           # Pydantic 数据校验
│   │   ├── services/          # 业务逻辑层
│   │   ├── core/              # 基础设施
│   │   └── utils/             # EPUB 解析引擎
│   └── storage/books/         # EPUB 文件存储
│
├── frontend/                   # Fork 自 Readest (v0.11.20)
│   ├── apps/readest-app/      # 主应用
│   │   └── src/
│   │       ├── services/api/  # ★ 自研后端 API 通信层
│   │       ├── hooks/         # ★ AI / 进度 / 网络 Hooks
│   │       └── components/    # Readest 现有组件 + 自定义
│   └── packages/              # foliate-js 等共享库
│
└── docs/
```

> ★ 标记的为自定义新增模块

---

## 当前实现状态 vs 需求

### ✅ 已实现的 MVP 功能

| 功能模块 | 状态 | 说明 |
|---------|------|------|
| **后端 API（全部 11 个接口）** | ✅ 已完成 | FastAPI + SQLite + SQLAlchemy |
| **EPUB 解析引擎** | ✅ 已完成 | 支持 EPUB 2/3，6 种异常处理 |
| **设备 UUID 管理** | ✅ 已完成 | 前端 `crypto.randomUUID()` + localStorage |
| **DeepSeek AI 集成** | ✅ 已完成 | 4 种 Prompt 模板（字词/句意/语法/背景） |
| **AI 划词解读** | ✅ 已完成 | 集成到 Readest 选中工具栏 ✨ 按钮 |
| **2000 字截断** | ✅ 已完成 | 后端 + 前端双重截断 |
| **账号体系** | ✅ 无需 | 全员游客模式，设备 UUID 标识 |
| **沉浸式阅读** | ✅ Readest 原生 | EPUB 渲染、翻页、样式、目录 |
| **阅读样式设置** | ✅ Readest 原生 | 字体、背景色、亮度、翻页模式 |
| **前端 API 封装层** | ✅ 已完成 | axios + X-Device-Id 拦截器 |

### ⏳ 已实现但未接入前端 UI

| 功能 | 后端 API | 前端 API 层 | 前端 UI 集成 |
|------|---------|------------|------------|
| EPUB 文件上传 | ✅ | ✅ | ⏳ 未接入 Readest 上传界面 |
| 书籍库管理（CRUD） | ✅ | ✅ | ⏳ 未接入 Readest 书库 |
| 阅读进度同步 | ✅ | ✅ | ⏳ 未接入 Readest 阅读器 |
| 书籍重命名/删除 | ✅ | ✅ | ⏳ 未接入 Readest 操作菜单 |

### ❌ 需求中标记但未实现

| 需求 | 说明 |
|------|------|
| 前端上传弹窗 | 未自建上传 UI，仍使用 Readest 原生文件导入 |
| 无网络 AI 入口置灰 | `NetworkIndicator` 组件已删除，未重新集成到工具栏 |
| 前端偏好本地缓存对接 | `localCache.ts` 已创建但未接入 Readest 设置系统 |
| AI 弹窗拖拽移动 | 当前为居中模态框，非可拖拽悬浮球 |
| 闲置自动关闭 | 当前 AI 弹窗无闲置自动关闭 |

### 🔮 二期规划（未实现）

- 多角色 TTS 朗读
- AI 深度对话讨论
- 笔记/批注系统
- 多端客户端适配
- 人物关系图谱
- 阅读数据统计

---

## 技术选型

| 层 | 技术 | 说明 |
|---|---|---|
| **前端** | Next.js 15 + React 19 + TypeScript | Fork 自 [Readest](https://github.com/readest/readest) v0.11.20 |
| **阅读引擎** | Foliate-js | EPUB 排版渲染 |
| **后端** | Python FastAPI | REST API |
| **数据库** | SQLite + SQLAlchemy ORM | WAL 模式 |
| **AI** | DeepSeek API（OpenAI 兼容模式） | 4 种 Prompt 模板 |
| **前后端通信** | REST + axios | 统一 X-Device-Id 标识 |

---

## 开发环境

### 前置条件

- Python 3.10+
- Node.js 20+
- pnpm 9+

### 启动后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env    # 填入 DEEPSEEK_API_KEY
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端

```bash
cd frontend
pnpm install
cd apps/readest-app
pnpm dev-web
```

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## 数据库表结构

| 表名 | 说明 |
|------|------|
| `devices` | 设备信息（device_id 唯一标识） |
| `books` | 书籍元信息（SHA256 哈希去重、软删除） |
| `book_contents` | 章节内容（html + plain_text 双字段） |
| `book_spine` | 阅读顺序索引 |
| `reading_progress` | 阅读进度（device_id + book_id 联合唯一） |

用户偏好（翻页模式、字体、背景色等）存储于前端 localStorage。

---

## Fork 说明

本项目前端基于 [Readest](https://github.com/readest/readest) (v0.11.20, MIT License) Fork 并改造：

- **保留**：EPUB 渲染引擎、翻页交互、样式配置、目录导航、文本选中
- **移除**：账号系统、书城、社区、同步服务、OPDS、Stripe 支付等非 MVP 模块
- **新增**：
  - `services/api/` — 自研后端 API 通信层
  - `hooks/useAI.ts` — AI 划词逻辑
  - `hooks/useReading.ts` — 阅读进度自动保存
  - `hooks/useNetwork.ts` — 网络状态监听
  - `utils/device.ts` — 设备 UUID 管理
  - `utils/localCache.ts` — 本地缓存封装
  - AI 解读按钮集成到选中工具栏
