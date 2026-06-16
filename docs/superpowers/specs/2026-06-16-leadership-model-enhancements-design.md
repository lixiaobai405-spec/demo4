# 领导力建模智能体 — 维度与可视化增强设计

日期: 2026-06-16 | 状态: 设计已确认

## 需求摘要

| # | 需求 | 类型 |
|---|------|------|
| 1 | 维度确定 — 手动添加编辑按钮，用户可自行增加维度 | 补充 |
| 2 | 每个维度标注来源（战略文档关键词/标准库映射/对话归纳）| 补充 |
| 3 | 知识库@LN匹配 — AI优先从预置领导力知识库匹配维度 | 优化 |
| 4 | 行为锚定保持BARS（分级分档描述暂不实现）| 确认 |
| 5 | 最终领导力模型以雷达图呈现，点击维度展示对应详情 | 优化 |

---

## 层1: 维度来源标注

### 现状
`ai_service.py` → `generate_dimensions()` 已返回 `sources: {strategy, framework, interview}`，前端未渲染。

### 后端
无需改动。`sources` 字段已存在于API返回中。

### 前端 — step2.html

**数据映射 (init)**:
```js
dims = recommended.map(d => ({
  id: d.id, nm: d.name, df: d.definition,
  pri: d.priority || 'important',
  sources: d.sources || {},  // 新增
  ok: false
}));
```

**渲染 (render)**: 维度卡片 `.dc-src` 区域渲染三色来源标签：
- 🔵 战略文档关键词 — `.src-tag.src-stg`
- 🟠 标准库映射 — `.src-tag.src-fwk`
- 🟢 对话归纳 — `.src-tag.src-int`
- 来源值为空字符串时不显示

**编辑Modal扩展**: 新增3个来源输入框（editSrcStg / editSrcFwk / editSrcInt），编辑/新增时均可填写。

### CSS
```css
.src-tag { font-size: 10.5px; padding: 2px 8px; border-radius: 100px; }
.src-stg { background: #E1EEF9; color: #1E5080; }
.src-fwk { background: #FFF0E5; color: #A05510; }
.src-int { background: #E1F5EE; color: #0F6E56; }
```

### 改动范围
- `frontend/step2.html`: 数据映射行 + render() + modal编辑

---

## 层2: 手动添加维度

### 入口
推荐维度区 header 行增加「＋ 手动添加」按钮。

### Modal复用
复用现有 `editModal`，`editId === '__new__'` 表示新增模式：
- 新增模式：字段清空，保存时 push 到 dims 数组
- 编辑模式：已有逻辑不变

### 新增字段集合
| 字段 | 组件 | 备注 |
|------|------|------|
| 维度名称 | input text | 必填 |
| 定义说明 | textarea | 必填 |
| 优先级 | select (core/important/supplementary) | 默认important |
| 战略来源 | input text | 可选 |
| 框架来源 | input text | 可选 |
| 访谈来源 | input text | 可选 |

### 新增维度属性
- `id`: `U` + 时间戳base36（如 `U1234ab`）
- `ok`: `true`（默认已确认）
- `manual`: `true`（标记手动添加，卡片显示「👤 手动」角标）

### 改动范围
- `frontend/step2.html`: modal扩展 + 按钮 + saveEdit逻辑 + render角标

---

## 层3: 领导力知识库 @LN

### 新增文件: `backend/knowledge_base.py`

包含：
- `LEADERSHIP_DIMENSIONS`: 30-40条预置维度，每条含 id/name/definition/industry_tags/level_range/sources/keywords
- `search_knowledge_base(company_info, level, top_n)`: 关键词+标签+层级匹配检索，返回top_n条
- `build_kb_context(company_info, level)`: 格式化检索结果为prompt文本

### 维度分类（5个能力簇，目标35条）

| 能力簇 | 计划条目数 |
|--------|-----------|
| 战略与商业 | 8 |
| 团队与人才 | 8 |
| 执行与流程 | 6 |
| 协同与影响 | 7 |
| 自我与认知 | 7 |

### AI服务集成

`ai_service.py` — `generate_dimensions()` 修改：

1. 新增 `use_kb: bool = True` 参数
2. 当 `use_kb=True` 时调用 `build_kb_context()` 获取知识库上下文
3. prompt中注入知识库指令，要求AI优先从知识库匹配维度
4. 知识库匹配的维度 sources.framework 标注知识库参考源

### 前端联动

维度卡片上区分知识库来源：
- id前缀 `LN-` → 📚 标准库映射
- id前缀 `D` → 🤖 AI生成
- id前缀 `U` → 👤 手动添加

### 改动范围
- 新建 `backend/knowledge_base.py`
- 修改 `backend/ai_service.py` (~30行)
- 修改 `frontend/step2.html` (~10行来源标记)

---

## 层4: 雷达图可视化

### 技术选型
Chart.js v4.4.0，CDN引入，无构建依赖。

### 布局

```
┌─ 完成横幅 + 导出按钮 ─┐
├─ 统计卡片行 ─────────┤
├─ 雷达图 (max-width 500px, 居中) ─┤
├─ 维度详情列表 (现有accordion) ─────┤
└─ 底部操作 ─────────────┘
```

### 雷达图配置

- **labels**: 维度名称数组
- **data**: 优先级映射数值 (core=5.0, important=3.5, supplementary=2.0)
- **配色**: 主色 `#6C216D`，半透明填充
- **交互**: `onClick` → 滚动到对应维度详情卡片 + 高亮动画

### 高亮动画
```css
@keyframes highlightPulse {
  0% { box-shadow: 0 0 0 0 rgba(108,33,109,.4); }
  50% { box-shadow: 0 0 0 8px rgba(108,33,109,.1); }
  100% { box-shadow: 0 0 0 0 rgba(108,33,109,0); }
}
.ov-item.highlight { animation: highlightPulse 1.5s ease-out; border-color: var(--p); }
```

### 改动范围
- `frontend/step5.html`: 布局重构 + Chart.js CDN + 雷达图渲染 + 交互逻辑 (~80行)

---

## 不改动的范围

- 后端 `/api/generate-anchors` 接口和BARS逻辑不变（需求4确认）
- Step1/Step3/Step4 功能逻辑不变
- 认证系统不变
- 导出服务不变

---

## 文件变更清单

| 操作 | 文件 | 说明 |
|------|------|------|
| 修改 | `frontend/step2.html` | 来源标注 + 手动添加 + 知识库标记 |
| 修改 | `frontend/step5.html` | 雷达图可视化 |
| 新建 | `backend/knowledge_base.py` | 领导力知识库 |
| 修改 | `backend/ai_service.py` | 知识库集成 |
| 修改 | `backend/app.py` | (必要时调整路由) |

---

## 设计约束

- 所有前端改动使用现有CSS变量系统，不引入新设计语言
- JS保持原生ES6，无框架依赖（与现有代码一致）
- 知识库数据使用Python原生数据结构，无数据库依赖
- 雷达图通过CDN加载Chart.js，离线环境可降级为表格视图
