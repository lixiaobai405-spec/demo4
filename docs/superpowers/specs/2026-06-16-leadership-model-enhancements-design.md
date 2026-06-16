# 领导力建模智能体 — 维度与可视化增强设计

日期: 2026-06-16 | 状态: 已审计修订 (v1.1)

## 需求摘要

| # | 需求 | 类型 |
|---|------|------|
| 1 | 维度确定 — 手动添加编辑按钮，用户可自行增加维度 | 补充 |
| 2 | 每个维度标注来源（战略文档关键词/标准库映射/对话归纳）| 补充 |
| 3 | 知识库@LN匹配 — AI优先从预置领导力知识库匹配维度 | 优化 |
| 4 | 行为锚定保持现有三档BARS逻辑不变（优秀/达标/不达标）| 确认 |
| 5 | 最终领导力模型以雷达图呈现，点击维度展示对应详情 | 优化 |

---

## ID 前缀体系（全局约定）

所有维度的 `id` 字段携带生成来源前缀，不可混用：

| 前缀 | 含义 | 生成者 | 示例 |
|------|------|--------|------|
| `D` | AI 实时生成 | `ai_service.generate_dimensions()` | `D1`, `D2` |
| `LN-` | 知识库匹配 | `knowledge_base.search_knowledge_base()` 返回，由 `generate_dimensions()` 嵌入 | `LN-001`, `LN-015` |
| `U_` | 用户手动添加 | 前端 step2.html `openAdd()` | `U_lxhc3d` |

**规则**：
- 当 `use_kb=True` 时，后端在 prompt 中注入知识库条目ID(`LN-xxx`)，要求AI在输出的 recommended 维度中引用该ID。后端在 `generate_dimensions()` 返回前校验：若维度的 `sources.framework` 含知识库参考源名，自动将其 `id` 替换为对应 `LN-xxx`。
- 前端根据 `id` 前缀显示来源角标（📚/🤖/👤），不自行推断。

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
  rationale: d.rationale || '',        // 保留（后续步骤可能使用）
  sources: d.sources || {},            // 新增
  ok: false
}));
```

**渲染 (render)**: 维度卡片 `.dc-src` 区域渲染三色来源标签：
- 🔵 战略文档关键词 — `.src-tag.src-stg`
- 🟠 标准库映射 — `.src-tag.src-fwk`
- 🟢 对话归纳 — `.src-tag.src-int`
- 来源值为空字符串时不显示该标签
- 防御：`d.sources || {}` 确保API缺失sources时不报错

**编辑Modal扩展**: 新增3个来源输入框（editSrcStg / editSrcFwk / editSrcInt），编辑/新增时均可填写。

**localStorage同步**: saveEdit 后自动调用 `localStorage.setItem('lm_dims', JSON.stringify(dims.filter(d => d.ok)))`，确保手动维度刷新不丢失。

### CSS
```css
/* 来源标签容器 */
.dc-src { padding: 0 15px 11px; display: flex; flex-wrap: wrap; gap: 5px; }
/* 来源标签 */
.src-tag { font-size: 10.5px; padding: 2px 8px; border-radius: 100px; }
.src-stg { background: #E1EEF9; color: #1E5080; }
.src-fwk { background: #FFF0E5; color: #A05510; }
.src-int { background: #E1F5EE; color: #0F6E56; }
```

### 改动范围
- `frontend/step2.html`: 数据映射行（保留rationale）+ render() + modal编辑

### 验收标准
- [ ] GIVEN 维度含 `sources.strategy="数字化转型"` WHEN 渲染维度卡片 THEN 显示🔵「战略：数字化转型」来源标签
- [ ] GIVEN 维度 `sources: {}` WHEN 渲染 THEN 来源区域为空，不报错
- [ ] GIVEN 用户编辑维度 WHEN 修改来源字段并保存 THEN localStorage 和 dims 数组同步更新

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
| 维度名称 | input text | 必填，空值时保存按钮禁用 |
| 定义说明 | textarea | 必填 |
| 优先级 | select (core/important/supplementary) | 默认important |
| 战略来源 | input text | 可选 |
| 框架来源 | input text | 可选 |
| 访谈来源 | input text | 可选 |

### 新增维度属性
- `id`: `U_` + 时间戳base36（如 `U_lxhc3d`）
- `ok`: `true`（默认已确认）
- `manual`: `true`（标记手动添加，卡片显示「👤 手动」角标）
- `rationale`: `''`（空字符串）
- `sources`: 来自用户输入的3个字段

### 边界处理
- **重名检测**: 保存时检查 `dims.some(d => d.nm === newName)`，提示「已存在同名维度，是否继续？」（confirm）
- **空名拒绝**: 名称为空时保存按钮 disabled

### localStorage
```js
function saveEdit() {
  // ... 新增/编辑逻辑 ...
  // 保存后同步
  localStorage.setItem('lm_dims', JSON.stringify(dims.filter(d => d.ok)));
  render();
}
```

### 改动范围
- `frontend/step2.html`: modal扩展 + 按钮 + saveEdit逻辑（含localStorage + 重名检测）+ render角标

### 验收标准
- [ ] GIVEN 用户点击「＋手动添加」WHEN 填写名称「团队管理」并保存 THEN 维度列表新增一条 id 以 `U_` 开头的已确认维度
- [ ] GIVEN 用户新增维度「团队管理」WHEN 刷新页面 THEN 维度仍在列表中（localStorage持久化）
- [ ] GIVEN 已存在维度「团队管理」WHEN 用户再次新增同名维度 THEN 弹出重名确认提示
- [ ] GIVEN 名称为空 WHEN 点击保存 THEN 按钮disabled，不执行保存

---

## 层3: 领导力知识库 @LN

### 新增文件: `backend/knowledge_base.py`

包含：
- `LEADERSHIP_DIMENSIONS`: 30-40条预置维度，每条含 id(LN-xxx)/name/definition/industry_tags/level_range/sources/keywords
- `search_knowledge_base(company_info: str, level: str, top_n: int = 15) -> list[dict]`: 关键词+标签+层级匹配检索，返回top_n条。匹配算法：对company_info分词，与每条维度的keywords+name做交集，结合industry_tags和level_range加权打分
- `build_kb_context(company_info: str, level: str) -> str`: 调用search后格式化为prompt文本

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
4. **ID替换逻辑**: 生成后校验每个维度的 `sources.framework`，若匹配到知识库条目，自动将 `id` 替换为对应 `LN-xxx`
5. 重试时使用固定ID—name映射，防止AI更换编号

### 边界处理
- **知识库返回0条**: 退化到纯AI生成模式，`sources.framework` 为空，ID使用 `D` 前缀。前端无知识库角标。
- **知识库条目与AI生成重复**: ID替换逻辑自动去重，同一知识库条目只出现一次
- **检索异常**: `search_knowledge_base` 包裹try/catch，异常时返回空列表并log warning，不影响主流程

### 前端联动

维度卡片来源角标逻辑（仅依据ID前缀，不做额外推断）：
```js
function sourceBadge(d) {
  if (d.id.startsWith('LN-')) return '<span class="badge bg-a">📚 标准库</span>';
  if (d.id.startsWith('U_')) return '<span class="badge bg-gy">👤 手动</span>';
  return '<span class="badge bg-p">🤖 AI生成</span>';
}
```

### 改动范围
- 新建 `backend/knowledge_base.py`
- 修改 `backend/ai_service.py` (~40行：prompt注入 + ID替换 + 边界处理)
- 修改 `frontend/step2.html` (~15行来源角标)

### 验收标准
- [ ] GIVEN company_info含"互联网/快速扩张/中层" WHEN 调用generate_dimensions(use_kb=True) THEN 返回的recommended中至少3个维度id以"LN-"开头
- [ ] GIVEN company_info含高度小众描述（无知识库匹配）WHEN use_kb=True THEN 正常返回D前缀维度，无异常
- [ ] GIVEN use_kb=False WHEN 调用generate_dimensions THEN 所有维度id为D前缀（向后兼容）

---

## 层4: 雷达图可视化

### 技术选型
Chart.js v4.4.0，CDN引入，无构建依赖。
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### 布局

```
┌─ 完成横幅 + 导出按钮 ─┐
├─ 统计卡片行 (4列) ────┤
├─ 雷达图 (max-width 500px, 居中) ─┤
├─ 维度详情列表 (现有accordion, 每个含data-dim属性) ┤
└─ 底部操作 ─────────────┘
```

### 雷达图配置

- **labels**: 维度名称数组
- **data**: 优先级映射数值 (core=5.0, important=3.5, supplementary=2.0)

> ⚠️ **设计说明**: 优先级→数值映射仅用于可视化示意，不代表实际能力水平。雷达图的面积和形状差异反映的是维度重要性配置，非测评结果。未来接入真实测评数据后替换此映射。

- **配色**: 主色 `#6C216D`(rgba(108,33,109,0.15)填充，`rgba(108,33,109,1)`边框)
- **交互**: `onClick` → 滚动到对应维度详情卡片 + 高亮动画

### CDN降级策略

```js
function renderRadar() {
  if (typeof Chart === 'undefined') {
    // 降级：显示维度优先级表格代替雷达图
    document.getElementById('radarArea').innerHTML = buildFallbackTable();
    return;
  }
  // 正常渲染雷达图
  new Chart(ctx, radarConfig);
}
```

降级表格：3列表格（维度名称 | 优先级 | 来源），保持可用性。

### 高亮动画
```css
@keyframes highlightPulse {
  0% { box-shadow: 0 0 0 0 rgba(108,33,109,.4); }
  50% { box-shadow: 0 0 0 8px rgba(108,33,109,.1); }
  100% { box-shadow: 0 0 0 0 rgba(108,33,109,0); }
}
.ov-item.highlight { animation: highlightPulse 1.5s ease-out; border-color: var(--p); }
```

### 点击维度节点交互流

1. Chart.js `onClick` 事件 → 获取点击的 label index
2. 根据 index 找到对应维度 id
3. `document.querySelector(`[data-dim="${id}"]`).scrollIntoView({behavior:'smooth', block:'center'})`
4. 目标元素添加 `.highlight` class → 触发脉冲动画
5. 动画结束后（1.5s）移除 `.highlight` class
6. 若该维度折叠中 → 自动展开（设置 openMap[id]=true + 重渲染）

### 改动范围
- `frontend/step5.html`: 布局重构 + Chart.js CDN（含降级逻辑）+ 雷达图渲染 + 交互逻辑 (~90行)

### 验收标准
- [ ] GIVEN 模型含5个维度 WHEN 加载step5 THEN 雷达图显示5个轴，数值对应优先级
- [ ] GIVEN 雷达图已渲染 WHEN 点击"战略引领"节点 THEN 页面滚动到对应维度详情，卡片高亮闪烁
- [ ] GIVEN Chart.js CDN加载失败 WHEN 加载step5 THEN 显示降级表格而非空白
- [ ] GIVEN 维度详情折叠中 WHEN 点击雷达图节点 THEN 自动展开该维度

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
| 修改 | `frontend/step2.html` | 来源标注 + 手动添加 + 知识库标记 + localStorage同步 |
| 修改 | `frontend/step5.html` | 雷达图可视化 + CDN降级 |
| 新建 | `backend/knowledge_base.py` | 领导力知识库（~200行） |
| 修改 | `backend/ai_service.py` | 知识库集成 + ID替换逻辑 |

---

## 边界场景处理矩阵

| 场景 | 处理策略 |
|------|---------|
| Chart.js CDN 加载失败 | 降级为优先级表格 |
| 知识库检索返回0条 | 退化到纯AI生成，D前缀 |
| 用户新增维度与现有重名 | confirm提示，用户确认后允许 |
| API响应缺少sources字段 | `d.sources \|\| {}` 防御，不显示标签 |
| 手动维度刷新后丢失 | saveEdit后自动写localStorage |
| 知识库检索异常 | try/catch → 空列表 + log warning → 主流程不中断 |

---

## 设计约束

- 所有前端改动使用现有CSS变量系统，不引入新设计语言
- JS保持原生ES6，无框架依赖（与现有代码一致）
- 知识库数据使用Python原生数据结构，无数据库依赖
- 雷达图通过CDN加载Chart.js，离线环境自动降级为表格视图
- ID前缀体系遵循本文约定，前后端一致
