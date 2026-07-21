# NReadTool 后续开发计划

> **目标：** 完成 MVP 剩余工作，使项目可运行、可演示，为后续迭代打好基础。

**当前状态总览：**
| 模块 | 状态 |
|------|------|
| 后端 API (11 个接口) | ✅ 已完成 |
| EPUB 解析引擎 | ✅ 已完成 |
| 设备 UUID 管理 | ✅ 已完成 |
| DeepSeek AI 集成 | ✅ 已完成 |
| 云端书库 (上传/列表/导入) | ✅ 已完成 |
| 阅读进度同步 | ✅ 已完成 |
| 前端 API 通信层 | ✅ 已完成 |
| AI 划词解读 (useAI + AI组件) | ✅ 已完成 |
| 书籍重命名/删除操作 | ✅ 已完成 (CloudBooksDialog) |
| AI 深度对话侧边栏 | ✅ Readest 内置 |
| 无网络 AI 入口置灰 | ❌ 未连接 |
| 前端偏好本地缓存对接 | ❌ localCache 未接入设置系统 |
| AI 弹窗拖拽移动 | ❌ 当前居中模态框 |
| 闲置自动关闭 | ❌ 未实现 |
| 端到端可运行验证 | ❌ 未做 |
| .env 配置 | ❌ 未配置 |

---

## 第一阶段：MVP 收尾（优先级：高）

### 任务 1：环境配置与首次启动验证

**目的：** 确保后端可启动、数据库可初始化、前端可编译。

**操作：**
1. 复制 `.env.example` → `.env`，填入 DeepSeek API Key
2. 安装 Python 依赖：`pip install -r requirements.txt`
3. 运行数据库迁移：`alembic upgrade head`
4. 启动后端：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
5. 检查 `/health` 和 `/docs` 是否正常
6. 安装前端依赖：`pnpm install`
7. 启动前端：`pnpm dev-web`
8. 验证首页可访问

**涉及文件：** `backend/.env`, `backend/requirements.txt`, `frontend/package.json`

---

### 任务 2：AI 划词弹窗 UI 改造 — 拖拽 + 闲置关闭

**目的：** 将当前的居中模态 AI 弹窗改为可拖拽悬浮球，并支持闲置自动关闭。

**现状：** `useAI.ts` 已有 `position` 状态和 `setPosition` 方法，但前端缺少实际渲染组件的实现。在 Readest 选中工具栏里已有 AI 按钮，但弹窗组件未连接。

**实现方案：**
1. 创建 `frontend/apps/readest-app/src/app/reader/components/AIExplainPopup.tsx`
   - 基于选中位置渲染一个可拖拽的浮动面板
   - 支持 4 种解读类型切换（字词/句意/语法/背景）
   - 显示加载状态、解读结果、错误提示
   - 支持拖拽移动
   - 支持点击空白关闭 + 闲置 30 秒自动关闭
2. 修改 `useAI.ts` 新增 `idleAutoClose` 逻辑 (useEffect + setTimeout)
3. 将该组件集成到阅读页面的 Annotator 或 Reader 组件中

**涉及文件：**
- 创建：`frontend/apps/readest-app/src/app/reader/components/AIExplainPopup.tsx`
- 修改：`frontend/apps/readest-app/src/hooks/useAI.ts`
- 修改：`frontend/apps/readest-app/src/app/reader/components/annotator/Annotator.tsx`（连接 AI 按钮）

---

### 任务 3：无网络 AI 入口置灰

**目的：** 当浏览器离线时，AI 划词按钮显示为置灰不可用状态。

**现状：** `useNetwork.ts` 已实现可监听 `navigator.onLine`，但未与 AI 按钮连接。

**实现方案：**
1. 在 AI 按钮组件中调用 `useNetwork()` 获取 `isOnline`
2. 当 `!isOnline` 时，按钮添加 `opacity-50 cursor-not-allowed` 等禁用样式
3. 点击时提示「网络不可用，请检查网络连接」

**涉及文件：**
- 修改：`frontend/apps/readest-app/src/app/reader/components/annotator/Annotator.tsx`

---

### 任务 4：本地缓存对接 Readest 设置系统

**目的：** 将 `localCache.ts` 接入 Readest 的设置管理，实现阅读偏好（翻页模式、字体、背景色等）的本地持久化。

**现状：** `localCache.ts` 已封装完成，但 Readest 的设置系统 (zustand store + localStorage) 使用自己的方案，`localCache` 未被引用。

**实现方案：**
1. 分析 Readest 的 `settingsStore` 和 `useSettingsSync` 了解现有持久化机制
2. 将 `localCache` 作为备选持久化层，或在现有机制之外扩展自定义偏好存储
3. 确保设备 ID、阅读偏好等数据通过 `localCache` 统一管理

**涉及文件：**
- 修改：`frontend/apps/readest-app/src/utils/localCache.ts`
- 修改：`frontend/apps/readest-app/src/store/settingsStore.ts` 或相关文件
- 需进一步确认 Readest 设置架构后再定具体方案

---

### 任务 5：README 状态更新 & 代码清理

**目的：** 使文档与实际代码状态一致。

**操作：**
1. 更新 README.md 中的「书籍重命名/删除操作菜单」状态为 ✅
2. 确认所有 TODO 标记的准确性
3. 清理不必要的调试代码和注释

**涉及文件：** `README.md`

---

## 第二阶段：质量保障与可运行验证（优先级：中）

### 任务 6：端到端流程测试

**目的：** 验证核心用户流程完整可用。

**测试流程：**
1. 上传 test-book.epub → 验证云端书库显示
2. 导入书籍到阅读器 → 验证 EPUB 渲染
3. 翻页 → 验证进度自动保存
4. 划词 → 验证 AI 解读弹窗
5. 重命名/删除书籍 → 验证操作反馈
6. 离线场景 → 验证按钮置灰

**涉及：** 人工测试 + 记录修复项

---

### 任务 7：后端增加基础测试覆盖

**目的：** 为关键后端服务添加单元测试，保障核心逻辑稳定。

**测试目标：**
1. EPUB 解析服务 — 解析 test-book.epub 验证章节、字数、元数据
2. AI 服务 — 验证 Prompt 构造、截断逻辑
3. 阅读进度 — 验证 CRUD

**涉及文件：**
- 创建：`backend/tests/test_epub_service.py`
- 创建：`backend/tests/test_ai_service.py`
- 创建：`backend/tests/test_reading_service.py`
- 修改：`backend/pyproject.toml`（添加 pytest 配置）

---

### 任务 8：错误处理与边界场景完善

**目的：** 提升系统健壮性。

**要点：**
1. 文件上传：验证失败格式、超大小、重复上传的友好提示
2. AI 服务：API Key 未配置时的降级提示
3. 网络异常：前后端超时处理一致性
4. 空数据状态：书籍列表为空、无进度等场景的 UI

**涉及文件：** 各 API 路由 + 前端组件

---

## 第三阶段：体验优化（优先级：低，按需推进）

### 任务 9：UI/UX 细节优化

- 书籍封面加载骨架屏
- 上传进度条百分比动画
- AI 解读结果 Markdown 渲染优化
- 移动端手势适配
- 深色模式兼容性检查

### 任务 10：部署准备

- 前端构建优化 (`pnpm build`)
- 后端 Dockerfile 编写
- CORS 配置细化（允许指定域名）
- 环境变量检查启动脚本
- 数据库备份方案

---

## 二期功能（备选，待排期）

| 功能 | 说明 | 预估 |
|------|------|------|
| 多角色 TTS 朗读 | Edge TTS / Web Speech API 实现听书 | 中 |
| AI 深度对话 | 基于全书知识库的问答（需向量库） | 大 |
| 笔记/批注系统 | 高亮 + 笔记持久化 | 中 |
| 阅读数据统计 | 阅读时长、本数统计图表 | 小 |
| 多端适配 | 移动端 responsive 优化 | 中 |

---

## 技术债务 & 注意事项

1. **SQLite 并发问题：** 当前使用 SQLite WAL 模式，多用户场景需考虑迁移到 PostgreSQL
2. **文件去重校验：** 当前基于 SHA256 + 文件名+设备双重校验，未来可优化
3. **AI 限流：** 配置了 `AI_RATE_LIMIT` 但未实现实际限流中间件
4. **密钥管理：** `DEEPSEEK_API_KEY` 直接写在 .env，生产环境应使用密钥管理服务
5. **前端构建：** Readest 的 `pnpm dev-web` 依赖大量包，首次构建较慢

---

## 建议执行顺序

```
任务 1（环境配置） → 任务 6（端到端测试）→
  ├→ 发现 bug → 修复 → 继续
  ├→ 任务 2（AI 弹窗）→ 任务 3（置灰）→ 任务 4（缓存）
  ├→ 任务 7（后端测试）
  └→ 任务 8（错误处理）
```

**建议优先启动「任务 1（环境配置）」先让系统跑起来，然后根据实际运行效果确定后续优先级。**
