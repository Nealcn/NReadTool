# NReadTool 二期功能开发计划

> **背景：** Readest Fork 已内置大量二期功能组件。本计划的目标是**梳理现状 → 测试验证 → 自定义增强 → 与后端集成**，而非从零开发。

---

## 总体概览

| 功能 | Readest 内置程度 | 所需工作 |
|------|----------------|---------|
| **多角色 TTS 朗读** | ✅ 完整实现（WebSpeech/Edge/Native 3 种引擎） | 测试 Web 环境兼容性，确保 UI 唤起路径 |
| **AI 深度对话** | ✅ 完整实现（Reedy Agent + RAG 索引） | 适配 Web 模式（当前部分功能限 Tauri），与后端 DeepSeek 对接 |
| **笔记/批注系统** | ✅ 完整实现（高亮/下划线/笔记/导出） | 可选：后端同步（当前存本地 IndexedDB） |
| **阅读数据统计** | ✅ 完整实现（TrackerCore + StatisticsDb + StatsSync） | 需新增统计看板 UI 页面 |

**结论：** 这不是"开发"而是"适配 + 集成"工作。Readest 本身已经是一个成熟阅读器。

---

## 第一阶段：现状盘点与测试（3-5 天）

### 任务 1.1：阅读器功能大盘点

**目的：** 摸清 Readest 已有功能在 Web 环境（`pnpm dev-web`）中的可用性。

| 功能 | 入口 | 预计 Web 可用性 |
|------|------|----------------|
| TTS 播放栏 | 阅读页底部工具栏 TTS 按钮 → TTSPlayerSheet | ⚠️ Edge TTS 需 Tauri 原生能力，WebSpeech 可用 |
| TTS 语音选择 | TTSPlayerSheet 中 | ✅ |
| TTS 章节预览 | TTSChaptersView | ✅ |
| 段落 TTS | 段落后 TTS 按钮 | ✅ |
| RSVP（速读） | RSVPControl | ✅ |
| 高亮标注 | 选中文本 → 弹出工具栏 → HighlightOptions | ✅ |
| 笔记 | Annotator 中笔记弹窗 | ✅ |
| 笔记侧边栏 | Notebook 面板 | ✅ |
| 标注导出 | ExportMarkdownDialog | ✅ |
| AI 对话 (Notebook) | 右面板 → AI 标签页 | ⚠️ 需要调整配置适配 Web |
| RAG 索引 | AIAssistant 中 "Index This Book" | ⚠️ 需 OPFS/IndexedDB 后端 |
| 阅读统计 | 当前仅有数据收集，无前台展示 UI | ❌ 需新建看板 |
| 统计看板 UI | 不存在 | ❌ 需开发 |

**操作：**
1. 启动完整前后端
2. 逐项测试每个功能入口的可用性
3. 记录每个功能在 Web 环境下的状态（可用/需适配/不可用）

**涉及：** 人工测试 + 记录清单

---

### 任务 1.2：AI 深聊适配 — Web 模式

**目的：** 让 AIAssistant 的深度对话能在 Web 浏览器中工作（当前部分功能仅在 Tauri 中可用）。

**现状分析：**
- `AIAssistant.tsx` 中的 `useAgentRuntime` 分支限制在 `isTauriAppPlatform()`，否则用 `LegacyAIAssistant`
- `LegacyAIAssistant` 使用 `LegacyIdbBackend`（基于 IndexedDB），Web 上可用
- RAG 索引需要 embedding 模型，当前通过 `OllamaProvider` / `OpenRouterProvider` 等实现
- 我们的自研后端已有 `/ai/explain` 点对点划词接口，但深度对话需要全文感知

**实现方案：**

| 子任务 | 方案 | 涉及文件 |
|--------|------|---------|
| Web embedding 降级 | Web 环境用 `LegacyIdbBackend` + OpenAI-compatible embedding API | `AIAssistant.tsx` |
| DeepSeek 作为 chat 后端 | 配置 `aiSettings` 使用 DeepSeek API（OpenAI 兼容模式） | `settingsService.ts` |
| 后端新增 /ai/chat 接口 | 可选：将深聊代理到后端统一管理 | `backend/app/api/v1/ai.py` |
| Web RAG 索引 | 使用 Web Worker + IndexedDB 切片存储 | 复用 Readest 现有方案 |

**方案 A（推荐，改动最小）：** 通过 settings 直接配置 DeepSeek 为 AI 提供商，复用 Readest 现有 AI 适配层。仅需：在 AI 设置面板中添加 DeepSeek 选项；在 Web 环境下启用 `LegacyAIAssistant` 并连通 DeepSeek API。

**涉及文件：**
- `frontend/apps/readest-app/src/app/reader/components/notebook/AIAssistant.tsx`
- `frontend/apps/readest-app/src/services/ai/providers/`（新增 DeepSeek provider）
- `frontend/apps/readest-app/src/store/settingsStore.ts`

---

### 任务 1.3：统计看板 UI 开发

**目的：** 新增一个阅读统计可视化页面，展示读书记录。

**数据来源：**
- Readest 内置 `StatisticsDb`（OPFS SQLite）存储 `page_stat_data` 和 `book` 表
- 字段：阅读时长、阅读页数、打开次数、每页中位时长

**页面设计：**
```
统计看板 (Statistics Dashboard)
├── 总览卡片：总阅读时长 / 读完本数 / 总页数
├── 最近阅读列表（书籍 + 阅读时长）
├── 阅读趋势（周/月 柱状图）
└── 每本书详情（点击展开）
```

**技术选型：** 纯 CSS 柱状图（无额外依赖），与项目现有风格一致。

**实现方案：**
1. 创建统计算法层：`useReadingStats.ts` — 从 `StatisticsDb` 读取并聚合数据
2. 创建统计页面组件：`StatisticsDialog.tsx` / `StatisticsPage.tsx`
3. 在图书馆页面添加入口（菜单项或按钮）
4. 如果需要，在后端添加统计同步 API

**涉及文件：**
- 创建：`frontend/apps/readest-app/src/app/library/components/StatisticsDialog.tsx`
- 创建：`frontend/apps/readest-app/src/hooks/useReadingStats.ts`
- 修改：`frontend/apps/readest-app/src/app/library/page.tsx`（添加入口）
- 可选：`backend/app/api/v1/statistics.py`（后端统计接口）

---

## 第二阶段：自定义增强（按需，2-4 天）

### 任务 2.1：TTS 体验增强（Web 版）

**目标：** 确保 WebSpeech TTS 在浏览器中流畅工作。

| 子任务 | 说明 |
|--------|------|
| 测试 WebSpeech 语音列表加载 | `WebSpeechClient.getAllVoices()` |
| 确认中英文语音切换 | 中文用 `zh-CN` 语音，英文保持原语言 |
| 添加段落级 TTS 按钮 | Readest 已有 `paragraphTts.ts`，确认 Web 工作 |
| TTS 后台播放 | 确保切页后继续播放 |

**涉及文件：** 主要是测试验证，少量配置调整

---

### 任务 2.2：笔记/批注后端同步（可选）

**目标：** 将笔记和标注同步到自研后端，实现多端数据一致。

**现状：** Readest 笔记存储在 IndexedDB + 通过 Readest Cloud 同步（使用 Readest 自己的后端服务）。我们 fork 后已移除 cloud sync。

**方案选择：**
| 方案 | 工作量 | 说明 |
|------|--------|------|
| **A：本地存储（推荐 MVP）** | 小 | 笔记仅存 IndexedDB/OPFS，适合个人使用 |
| **B：后端 API 同步** | 中 | 后端新增笔记 CRUD API，前端增加同步逻辑 |
| **C：WebDAV/文件同步** | 中 | 复用 Readest 已有的文件同步能力 |

**推荐方案 A**（二期功能，本地存储已够用，等有多端需求再上云同步）。

---

### 任务 2.3：AI 划词弹窗集成到注解工具栏

**目标：** 将我们自研的 AI 划词（`/ai/explain`）集成到 Readest 现有的选中工具栏中。

**现状：**
- Readest 已有 `AnnotationToolButton` + `Annotator` 的选中工具栏
- 工具栏已有：高亮、下划线、字典查询等功能
- 我们的 `useAI` hook 已创建，但未接入工具栏

**实现方案：**
1. 在 `Annotator.tsx` 的选中工具栏中添加 AI 按钮
2. 按钮连接 `useAI` 的 `handleTextSelection`
3. 调用后端 `/ai/explain` 接口
4. 以弹窗形式展示 AI 解读结果

**涉及文件：**
- 修改：`frontend/apps/readest-app/src/app/reader/components/annotator/Annotator.tsx`
- 修改：`frontend/apps/readest-app/src/app/reader/components/annotator/AnnotationToolButton.tsx`（或新建 AI 按钮）

---

## 第三阶段：部署与优化（可选）

### 任务 3.1：构建优化

```bash
cd frontend && pnpm build
# 检查构建产出，优化体积
```

### 任务 3.2：Docker 部署

```dockerfile
# 后端 Docker
FROM python:3.11-slim
# ...
```

---

## 排期建议

```
第1周（核心）：
  ├── 1.1 功能大盘点（2天）
  ├── 1.2 AI深聊适配（2天）
  └── 1.3 统计看板UI（1天）

第2周（增强）：
  ├── 2.1 TTS体验测试（1天）
  ├── 2.3 AI划词接入工具栏（1-2天）
  └── 2.2 笔记同步评估（按需）

第3周（收尾）：
  ├── 3.1 构建测试（1天）
  ├── 3.2 部署Docker（1天）
  └── 文档更新（0.5天）
```

---

## 关键风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| Readest 的 TTS 深度依赖 Tauri 原生能力 | Web 上部分 TTS 功能不可用 | 以 WebSpeech 为主，Edge TTS 作为增强 |
| LegacyAIAssistant 需要 embedding 服务 | 非 Tauri 环境无内置 embedding | 配置使用 DeepSeek 或其他 OpenAI 兼容 embedding |
| StatisticsDb 使用 OPFS SQLite | Web 环境中可能受限 | 确认 OPFS 兼容性，准备 IndexedDB 回退 |
| Readest 上游版本更新 | 合并冲突 | 锁定 fork 版本，按需 cherry-pick |

---

## 文件变更总览

| 操作 | 文件 |
|------|------|
| **创建** | `frontend/apps/readest-app/src/app/library/components/StatisticsDialog.tsx` |
| **创建** | `frontend/apps/readest-app/src/hooks/useReadingStats.ts` |
| **创建** | `frontend/apps/readest-app/src/services/ai/providers/DeepSeekProvider.ts` |
| **修改** | `frontend/apps/readest-app/src/app/reader/components/notebook/AIAssistant.tsx` |
| **修改** | `frontend/apps/readest-app/src/app/reader/components/annotator/Annotator.tsx` |
| **修改** | `frontend/apps/readest-app/src/app/library/page.tsx` |
| **可选** | `backend/app/api/v1/statistics.py` |
| **可选** | `backend/app/api/v1/notes.py` |
