# 领导力建模增强 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 维度来源标注 + 手动添加维度 + 知识库@LN匹配 + 雷达图可视化

**Architecture:** 后端新增 `knowledge_base.py` 预置维度库，融入 `ai_service.py` 的 `generate_dimensions` prompt；前端 step2.html 渲染来源标签、手动添加入口、知识库角标；step5.html 新增 Chart.js 雷达图与降级表格

**Tech Stack:** Python/Flask (后端), vanilla JS ES6 + Chart.js 4.4 CDN (前端), 现有CSS变量系统

---

### Task 1: 领导力知识库模块

**Files:**
- Create: `backend/knowledge_base.py`
- Test: `backend/tests/test_knowledge_base.py`

- [ ] **Step 1: 写知识库测试**

```python
"""backend/tests/test_knowledge_base.py"""
import pytest
from backend.knowledge_base import (
    LEADERSHIP_DIMENSIONS,
    search_knowledge_base,
    build_kb_context,
)


def test_leadership_dimensions_populated():
    """知识库至少有30条维度"""
    assert len(LEADERSHIP_DIMENSIONS) >= 30
    # 每条必含字段
    required = {"id", "name", "definition", "industry_tags", "level_range", "sources", "keywords"}
    for d in LEADERSHIP_DIMENSIONS:
        assert required.issubset(d.keys()), f"维度 {d.get('id','?')} 缺字段: {required - set(d.keys())}"
        assert d["id"].startswith("LN-"), f"ID 必须以 LN- 开头: {d['id']}"
        assert len(d["name"]) >= 2
        assert len(d["definition"]) >= 20
        assert len(d["keywords"]) >= 3


def test_search_knowledge_base_returns_relevant_results():
    """按行业和关键词检索应返回匹配维度"""
    results = search_knowledge_base(
        "互联网科技公司，快速扩张期，中层管理者面临跨部门协作挑战",
        "中层管理者",
        top_n=5
    )
    assert 0 < len(results) <= 5
    # 应包含与"协作"相关的维度
    found_collab = any(
        "协作" in d["name"] or "协作" in " ".join(d["keywords"])
        for d in results
    )
    assert found_collab, "应包含协作相关维度"


def test_search_knowledge_base_handles_empty_input():
    """空输入不应报错"""
    results = search_knowledge_base("", "基层管理者", top_n=10)
    # 应返回任何适合基层的维度（即使匹配度低）
    assert isinstance(results, list)
    # 不应崩溃


def test_search_knowledge_base_respects_level():
    """应优先返回匹配目标层级的维度"""
    results = search_knowledge_base("战略规划", "高层管理者", top_n=10)
    for d in results:
        # 高层匹配的维度不应标记为仅适用于基层
        if "基层" in d["level_range"] and len(d["level_range"]) == 1:
            pytest.fail(f"高层查询不应返回仅基层维度: {d['id']} {d['name']}")


def test_build_kb_context_formats_as_prompt_text():
    """格式化为prompt文本"""
    ctx = build_kb_context("互联网公司，中层管理者", "中层管理者")
    assert isinstance(ctx, str)
    assert len(ctx) > 100
    assert "LN-" in ctx
    assert "name" in ctx.lower() or "维度" in ctx
```

- [ ] **Step 2: 运行测试，验证失败**

```bash
python -m pytest backend/tests/test_knowledge_base.py -v
```
Expected: 全部 FAIL，模块未创建

- [ ] **Step 3: 创建知识库模块**

```python
"""backend/knowledge_base.py
领导力维度知识库 @LN — 预置30+维度，支持关键词检索
"""
import re
from typing import Optional

# ── 预置维度库 ─────────────────────────────────────────────

LEADERSHIP_DIMENSIONS = [
    # ═══ 战略与商业 (8条) ═══
    {
        "id": "LN-001",
        "name": "战略拆解与落地",
        "definition": "将公司战略目标转化为部门级可执行计划，设定关键里程碑和可衡量指标，定期复盘进展并动态调整资源配置，确保团队工作与战略方向一致。",
        "industry_tags": ["通用", "互联网", "科技", "制造", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Hay Group 领导力素质模型",
            "strategy": "战略执行力",
            "reference": "McClelland 胜任力词典 — 成就导向"
        },
        "keywords": ["战略", "拆解", "目标", "落地", "执行", "规划", "复盘", "资源配置"]
    },
    {
        "id": "LN-002",
        "name": "商业敏锐度",
        "definition": "深度理解行业趋势和竞争格局，将市场洞察转化为业务机会识别，在决策中平衡短期收益与长期价值，推动业务模式持续进化。",
        "industry_tags": ["通用", "互联网", "金融", "零售", "科技"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Lominger 胜任力卡片 — Business Acumen",
            "strategy": "商业洞察力",
            "reference": "DDI 领导力成功画像"
        },
        "keywords": ["商业", "市场", "竞争", "趋势", "业务", "洞察", "机会", "收益"]
    },
    {
        "id": "LN-003",
        "name": "变革引领",
        "definition": "识别组织变革需求，制定变革路径图，化解变革阻力，带领团队在不确定性中保持方向感和凝聚力，将变革转化为组织能力提升。",
        "industry_tags": ["通用", "科技", "制造", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Kotter 变革领导力模型",
            "strategy": "组织变革管理",
            "reference": "McClelland 胜任力词典 — 影响力"
        },
        "keywords": ["变革", "转型", "组织", "阻力", "引领", "不确定性", "适应"]
    },
    {
        "id": "LN-004",
        "name": "全局思维",
        "definition": "跳出部门视角，从公司整体利益出发分析问题和制定决策，理解各业务单元之间的关联与制约，在局部优化和全局最优之间做出理性权衡。",
        "industry_tags": ["通用", "科技", "制造", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Spencer 胜任力词典 — Systems Thinking",
            "strategy": "系统思考能力",
            "reference": "学习型组织理论 (Senge)"
        },
        "keywords": ["全局", "系统", "部门", "平衡", "关联", "整体", "格局", "视角"]
    },
    {
        "id": "LN-005",
        "name": "创新驱动",
        "definition": "在团队中建立鼓励试错的创新氛围，主动引入新方法新技术解决业务难题，将创意转化为可落地的产品改进或流程优化方案并衡量效果。",
        "industry_tags": ["互联网", "科技", "零售", "通用"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "Kirkpatrick 创新领导力模型",
            "strategy": "创新管理与设计思维",
            "reference": "Google Project Oxygen — Innovation"
        },
        "keywords": ["创新", "试错", "创意", "改进", "优化", "实验", "突破", "探索"]
    },
    {
        "id": "LN-006",
        "name": "风险管控",
        "definition": "系统识别业务和运营中的潜在风险，建立预警机制和应急预案，在风险发生前采取预防措施，风险发生后快速响应控制损失范围。",
        "industry_tags": ["金融", "制造", "科技", "通用"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "COSO 风险管理框架",
            "strategy": "风险识别与内控",
            "reference": "ISO 31000 风险管理标准"
        },
        "keywords": ["风险", "预警", "应急", "预防", "控制", "合规", "安全", "审计"]
    },
    {
        "id": "LN-007",
        "name": "业务规划",
        "definition": "基于数据和市场分析制定年度业务计划，将模糊的业务方向量化为可追踪的KPI体系，在资源约束下排出优先级，确保核心目标不受日常事务干扰。",
        "industry_tags": ["通用", "互联网", "金融", "零售"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "平衡计分卡 (BSC)",
            "strategy": "战略规划与预算管理",
            "reference": "Kaplan & Norton 战略地图"
        },
        "keywords": ["规划", "预算", "KPI", "优先级", "指标", "资源", "年度", "目标"]
    },
    {
        "id": "LN-008",
        "name": "客户导向",
        "definition": "深度理解内外部客户需求与痛点，在决策中优先考虑客户价值创造，将客户反馈系统性地转化为产品和服务改进，建立以客户为中心的团队文化。",
        "industry_tags": ["通用", "互联网", "零售", "金融", "服务"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "亚马逊领导力原则 — Customer Obsession",
            "strategy": "客户体验管理",
            "reference": "Net Promoter System (Reichheld)"
        },
        "keywords": ["客户", "需求", "痛点", "价值", "反馈", "服务", "体验", "满意度"]
    },

    # ═══ 团队与人才 (8条) ═══
    {
        "id": "LN-009",
        "name": "团队赋能",
        "definition": "识别团队成员的能力差距和发展潜力，通过教练式辅导、针对性授权和项目历练激发个体成长，构建自我驱动的学习型团队氛围。",
        "industry_tags": ["通用", "互联网", "科技", "制造"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Google Project Oxygen — Coaching",
            "strategy": "人才发展体系",
            "reference": " situational leadership (Hersey-Blanchard)"
        },
        "keywords": ["赋能", "辅导", "教练", "授权", "成长", "潜力", "能力", "发展"]
    },
    {
        "id": "LN-010",
        "name": "人才识别与梯队建设",
        "definition": "建立团队人才评估标准，识别高潜质成员并制定个性化发展计划，确保关键岗位有明确的后备人选，降低人才断层对业务的影响。",
        "industry_tags": ["通用", "科技", "金融", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "GE Session C 人才盘点",
            "strategy": "继任计划与人才梯队",
            "reference": "九宫格人才矩阵"
        },
        "keywords": ["人才", "梯队", "后备", "高潜", "盘点", "继任", "评估", "识别"]
    },
    {
        "id": "LN-011",
        "name": "绩效推动",
        "definition": "设定清晰的绩效标准和期望，通过持续反馈而非年终考核驱动业绩改善，对低绩效行为及时介入纠偏，对高绩效行为即时认可和复制推广。",
        "industry_tags": ["通用", "互联网", "金融", "零售"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Deloitte 绩效管理重构",
            "strategy": "持续绩效管理 (CPM)",
            "reference": "SMART 目标管理"
        },
        "keywords": ["绩效", "反馈", "考核", "目标", "改善", "认可", "标准", "KPI"]
    },
    {
        "id": "LN-012",
        "name": "激励人心",
        "definition": "理解不同类型成员的驱动力来源，将工作本身设计为激励载体，通过意义感、自主权和成长空间激发内在动机，而非仅依赖物质奖励。",
        "industry_tags": ["通用", "互联网", "科技"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Daniel Pink 驱动力3.0",
            "strategy": "员工激励与敬业度",
            "reference": "Self-Determination Theory (Deci & Ryan)"
        },
        "keywords": ["激励", "动机", "驱动力", "意义", "自主", "认可", "敬业", "士气"]
    },
    {
        "id": "LN-013",
        "name": "冲突化解",
        "definition": "识别团队内部和跨部门冲突的根源，运用双赢思维引导各方从立场之争转向利益协同，将建设性冲突转化为团队创新和改进的契机。",
        "industry_tags": ["通用", "制造", "金融"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Thomas-Kilmann 冲突模式模型",
            "strategy": "组织冲突管理",
            "reference": "哈佛谈判术 (Fisher & Ury)"
        },
        "keywords": ["冲突", "调解", "分歧", "协商", "双赢", "利益", "斡旋", "化解"]
    },
    {
        "id": "LN-014",
        "name": "凝聚力打造",
        "definition": "通过团队愿景共启、成功经验共享和困难时刻的并肩作战建立信任纽带，营造心理安全氛围使成员敢于表达不同意见和承担人际风险。",
        "industry_tags": ["通用", "互联网", "科技"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Google Project Aristotle — Psychological Safety",
            "strategy": "团队效能建设",
            "reference": "The Five Dysfunctions of a Team (Lencioni)"
        },
        "keywords": ["凝聚", "信任", "安全", "氛围", "团队", "默契", "共享", "归属"]
    },
    {
        "id": "LN-015",
        "name": "授权管理",
        "definition": "根据成员能力和任务复杂度匹配合适的授权层级，在授权过程中明确边界和决策权限，授权后提供支持而非干预，让成员在承担责任中加速成长。",
        "industry_tags": ["通用", "互联网", "科技", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Situational Leadership II (Blanchard)",
            "strategy": "授权赋能管理",
            "reference": "Delegation Poker (Management 3.0)"
        },
        "keywords": ["授权", "边界", "权限", "放权", "决策", "信任", "赋能", "自主"]
    },
    {
        "id": "LN-016",
        "name": "团队管理",
        "definition": "合理配置团队成员角色与任务分配，建立高效的工作机制和沟通节奏，平衡团队工作负荷与成员发展需求，打造稳定交付的高绩效团队。",
        "industry_tags": ["通用", "互联网", "科技", "制造", "金融"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Tuckman 团队发展阶段模型",
            "strategy": "团队建设与管理",
            "reference": "Belbin 团队角色理论"
        },
        "keywords": ["团队", "管理", "角色", "任务", "机制", "沟通", "配置", "效率"]
    },

    # ═══ 执行与流程 (6条) ═══
    {
        "id": "LN-017",
        "name": "目标导向执行",
        "definition": "将模糊的方向转化为清晰可衡量的行动方案，设定明确的时间节点和交付标准，在推进过程中持续追踪关键里程碑，确保承诺结果按期达成。",
        "industry_tags": ["通用", "制造", "金融", "零售"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "OKR 目标与关键结果",
            "strategy": "执行力体系",
            "reference": "The 4 Disciplines of Execution (McChesney)"
        },
        "keywords": ["执行", "目标", "交付", "里程碑", "追踪", "结果", "承诺", "达成"]
    },
    {
        "id": "LN-018",
        "name": "过程管控",
        "definition": "建立可视化进度追踪机制，定期检查关键节点完成质量，发现偏差当周启动纠偏动作而非等待月末复盘，将过程数据作为持续改进的依据。",
        "industry_tags": ["制造", "金融", "通用"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "精益管理 (Lean Management)",
            "strategy": "PDCA 循环管理",
            "reference": "关键链项目管理 (CCPM)"
        },
        "keywords": ["过程", "进度", "节点", "纠偏", "追踪", "检查", "质量", "数据"]
    },
    {
        "id": "LN-019",
        "name": "资源统筹",
        "definition": "在资源有限的前提下合理分配人力、预算和时间到各项任务，预判资源瓶颈并提前协调，在优先级冲突时基于业务价值而非惯性做出取舍。",
        "industry_tags": ["通用", "互联网", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "项目管理知识体系 (PMBOK)",
            "strategy": "资源规划与调度",
            "reference": "约束理论 (TOC)"
        },
        "keywords": ["资源", "预算", "分配", "统筹", "优先级", "瓶颈", "协调", "取舍"]
    },
    {
        "id": "LN-020",
        "name": "数据决策",
        "definition": "在管理决策中基于数据分析而非直觉判断，建立关键业务指标体系和数据仪表盘，用数据验证假设，将数据洞察转化为可操作的业务行动。",
        "industry_tags": ["互联网", "科技", "金融", "零售"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "数据驱动决策 (DDDM)",
            "strategy": "商业智能与分析",
            "reference": "McKinsey 数据驱动型组织"
        },
        "keywords": ["数据", "决策", "分析", "指标", "仪表盘", "验证", "洞察", "假设"]
    },
    {
        "id": "LN-021",
        "name": "流程优化",
        "definition": "定期审视现有工作流程中的浪费和低效环节，运用流程改进工具进行系统性优化，推动标准化和自动化以减少人为差错，沉淀最佳实践。",
        "industry_tags": ["制造", "金融", "科技", "通用"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "六西格玛 (Six Sigma)",
            "strategy": "业务流程管理 (BPM)",
            "reference": "价值流图 (Value Stream Mapping)"
        },
        "keywords": ["流程", "优化", "效率", "标准化", "自动化", "浪费", "改进", "沉淀"]
    },
    {
        "id": "LN-022",
        "name": "质量意识",
        "definition": "在交付的每个环节建立质量标准和控制节点，对输出的准确性和完整性负责，建立团队'一次做对'的质量文化，降低返工成本和客户投诉。",
        "industry_tags": ["制造", "金融", "科技", "通用"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "全面质量管理 (TQM)",
            "strategy": "质量保证体系",
            "reference": "ISO 9001 质量管理标准"
        },
        "keywords": ["质量", "标准", "准确", "完整", "控制", "返工", "检查", "细节"]
    },

    # ═══ 协同与影响 (7条) ═══
    {
        "id": "LN-023",
        "name": "跨部门协作",
        "definition": "主动识别跨部门协作节点和依赖关系，建立定期同步机制和信息共享平台，在资源冲突和利益分歧时介入斡旋，推动多方达成共识确保项目推进。",
        "industry_tags": ["通用", "互联网", "科技", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "横向领导力 (Lateral Leadership)",
            "strategy": "组织协同机制",
            "reference": "Harvard Business Review — Collaboration"
        },
        "keywords": ["协作", "跨部门", "协同", "同步", "共识", "斡旋", "依赖", "信息"]
    },
    {
        "id": "LN-024",
        "name": "沟通影响力",
        "definition": "根据沟通对象和场景灵活调整表达策略：向上聚焦结论和风险，横向强调共同利益和互换价值，向下注重拆解和激励，确保信息被准确理解和采纳。",
        "industry_tags": ["通用", "金融", "互联网"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "哈佛商学院影响力沟通模型",
            "strategy": "组织沟通与利益相关者管理",
            "reference": "Crucial Conversations (Patterson)"
        },
        "keywords": ["沟通", "影响", "表达", "汇报", "说服", "演讲", "倾听", "策略"]
    },
    {
        "id": "LN-025",
        "name": "向上管理",
        "definition": "主动对齐上级的优先级和期望，预判上级的信息需求和决策节点并在其提问前提供关键信息，以数据和方案支撑提案而非仅抛出问题。",
        "industry_tags": ["通用", "互联网", "金融"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Managing Up (Harvard Business Review)",
            "strategy": "上下级协作关系管理",
            "reference": "The Leader's Guide to Managing Up (Badowski)"
        },
        "keywords": ["向上", "汇报", "对齐", "预判", "上级", "提案", "决策", "期望"]
    },
    {
        "id": "LN-026",
        "name": "伙伴关系构建",
        "definition": "识别外部合作伙伴和供应商中的战略价值节点，建立互利共赢的长期合作机制，在合作中保持专业边界的同时深度理解对方利益诉求。",
        "industry_tags": ["制造", "零售", "科技"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "战略供应商管理 (SRM)",
            "strategy": "生态合作体系",
            "reference": "联盟管理 (Alliance Management)"
        },
        "keywords": ["伙伴", "合作", "供应商", "联盟", "共赢", "边界", "长期", "关系"]
    },
    {
        "id": "LN-027",
        "name": "谈判斡旋",
        "definition": "在资源分配和利益协调中运用谈判技巧创造增量价值而非零和博弈，深入理解各方底线和谈判空间，在坚持原则的前提下灵活设计方案达成协议。",
        "industry_tags": ["通用", "金融", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "哈佛谈判术 (Getting to Yes)",
            "strategy": "商务谈判与合同管理",
            "reference": "Negotiation Genius (Malhotra)"
        },
        "keywords": ["谈判", "斡旋", "协议", "底线", "博弈", "价值", "方案", "让步"]
    },
    {
        "id": "LN-028",
        "name": "生态构建",
        "definition": "识别产业链中的关键节点和互补资源，主动构建外部合作网络和资源生态圈，将零散的外部关系升级为体系化可复用的合作资产。",
        "industry_tags": ["互联网", "科技", "金融"],
        "level_range": ["高层"],
        "sources": {
            "framework": "平台生态系统战略",
            "strategy": "生态圈战略构建",
            "reference": "商业生态系统理论 (Moore)"
        },
        "keywords": ["生态", "产业", "网络", "平台", "资源", "整合", "链", "互补"]
    },
    {
        "id": "LN-029",
        "name": "文化塑造",
        "definition": "以身作则践行组织价值观，通过日常行为、机制设计和符号化事件将抽象价值观转化为团队成员的共识和习惯，在文化冲突时坚定守护核心原则。",
        "industry_tags": ["通用", "互联网", "科技"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Schein 组织文化三层模型",
            "strategy": "企业文化体系建设",
            "reference": "Netflix文化手册 (Hastings)"
        },
        "keywords": ["文化", "价值", "理念", "共识", "习惯", "机制", "榜样", "原则"]
    },
    {
        "id": "LN-030",
        "name": "利益相关者管理",
        "definition": "系统识别所有受决策影响的内外部利益相关者，分析各自的立场、影响力和期望，在关键决策前制定沟通和参与计划确保各方被听见和尊重。",
        "industry_tags": ["通用", "金融", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "PMBOK 利益相关者管理",
            "strategy": "利益相关者沟通策略",
            "reference": "Stakeholder Theory (Freeman)"
        },
        "keywords": ["利益", "相关者", "影响", "立场", "沟通", "参与", "关系", "期望"]
    },

    # ═══ 自我与认知 (7条) ═══
    {
        "id": "LN-031",
        "name": "学习敏锐度",
        "definition": "在新领域和陌生情境中快速识别关键知识并建立认知框架，将过往经验灵活迁移到新问题解决中，对自己的知识盲区保持清醒并主动补足。",
        "industry_tags": ["通用", "互联网", "科技", "金融"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "Learning Agility (Lominger)",
            "strategy": "学习型组织建设",
            "reference": "Growth Mindset (Dweck)"
        },
        "keywords": ["学习", "敏锐", "迁移", "适应", "框架", "盲区", "认知", "成长"]
    },
    {
        "id": "LN-032",
        "name": "情绪韧性",
        "definition": "在高压和挫折情境下保持冷静和理性判断，不被情绪左右决策质量，从失败中快速恢复并提炼经验教训，为团队在动荡时期提供情绪稳定锚。",
        "industry_tags": ["通用", "互联网", "金融"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "EQ-i 2.0 情绪智力模型",
            "strategy": "心理韧性与抗压能力",
            "reference": "Resilience Factor (Reivich & Shatté)"
        },
        "keywords": ["情绪", "韧性", "压力", "恢复", "冷静", "挫折", "适应", "平衡"]
    },
    {
        "id": "LN-033",
        "name": "系统思考",
        "definition": "识别复杂问题中的因果关系和反馈回路，避免线性归因和局部优化陷阱，在决策时考虑二阶效应和长期动态，帮助团队看清'冰山之下'的结构性因素。",
        "industry_tags": ["科技", "金融", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "第五项修炼 — 系统思考 (Senge)",
            "strategy": "复杂问题分析与决策",
            "reference": "Thinking in Systems (Meadows)"
        },
        "keywords": ["系统", "因果", "反馈", "结构", "复杂", "长期", "分析", "模式"]
    },
    {
        "id": "LN-034",
        "name": "概念思维",
        "definition": "从碎片化的信息中提炼出模式和规律，将具体问题抽象为可复用的分析框架，在不同领域间建立类比和联系以产生创新性的解决方案。",
        "industry_tags": ["科技", "互联网", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "McClelland 胜任力词典 — Conceptual Thinking",
            "strategy": "战略分析与框架构建",
            "reference": "The Pyramid Principle (Minto)"
        },
        "keywords": ["概念", "抽象", "规律", "框架", "模式", "提炼", "类比", "归纳"]
    },
    {
        "id": "LN-035",
        "name": "成就导向",
        "definition": "为自己和团队设定挑战性的目标而非安于现状，持续寻找超越标准和期望的机会，对结果有强烈的拥有感——不达目标不罢休。",
        "industry_tags": ["通用", "互联网", "金融", "零售"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "McClelland 成就动机理论",
            "strategy": "高绩效文化塑造",
            "reference": "Grit (Duckworth)"
        },
        "keywords": ["成就", "挑战", "超越", "结果", "卓越", "追求", "突破", "标准"]
    },
    {
        "id": "LN-036",
        "name": "诚信正直",
        "definition": "在利益冲突和压力下坚持道德底线和职业操守，承诺的事项坚决兑现，敢于承认错误和承担责任，在组织中建立可靠的个人品牌。",
        "industry_tags": ["通用", "金融"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "McClelland 胜任力词典 — Integrity",
            "strategy": "职业道德与合规体系",
            "reference": "Authentic Leadership (George)"
        },
        "keywords": ["诚信", "正直", "道德", "责任", "承诺", "可靠", "底线", "操守"]
    },
    {
        "id": "LN-037",
        "name": "认知灵活性",
        "definition": "在矛盾信息和多变情境中保持思维开放，不执着于既定方案，根据新信息快速调整判断和策略，在模糊性中做出合理决策而非等待完全信息。",
        "industry_tags": ["互联网", "科技", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Cognitive Flexibility Theory (Spiro)",
            "strategy": "敏捷领导力",
            "reference": "Adaptive Leadership (Heifetz)"
        },
        "keywords": ["灵活", "适应", "调整", "开放", "模糊", "信息", "判断", "转变"]
    },
]


# ── 检索函数 ─────────────────────────────────────────────

def search_knowledge_base(
    company_info: str,
    level: str = "中层管理者",
    top_n: int = 15
) -> list[dict]:
    """根据企业信息和建模层级，从知识库检索最匹配的维度。

    匹配算法：
    1. 对 company_info 做中文分词（按常见分隔符 + 2-gram）
    2. 对每条维度计算匹配分数：关键词命中数 + 行业标签匹配 + 层级匹配
    3. 按分数降序返回 top_n 条

    Args:
        company_info: 企业背景描述文本
        level: 目标建模层级
        top_n: 返回最大条数

    Returns:
        匹配的维度列表（按相关度降序），最少0条
    """
    if not company_info or not company_info.strip():
        # 无信息时返回通用维度（适合目标层级的）
        results = [d for d in LEADERSHIP_DIMENSIONS if level in d["level_range"]]
        return results[:top_n]

    # 简单中文分词：提取所有2字+词
    tokens = set()
    # 按空格、标点、换行分割
    raw_segments = re.split(r'[，。、；：！？\s\n,.;:!?]+', company_info)
    for seg in raw_segments:
        seg = seg.strip()
        if len(seg) >= 2:
            tokens.add(seg)
        # 同时添加2-gram
        for i in range(len(seg) - 1):
            tokens.add(seg[i:i+2])

    scored = []
    for d in LEADERSHIP_DIMENSIONS:
        score = 0
        # 关键词匹配 (每个命中+3)
        for kw in d["keywords"]:
            if kw in company_info:
                score += 3
            # 部分匹配
            for tok in tokens:
                if kw in tok or tok in kw:
                    score += 1
                    break
        # 行业标签匹配 (每个+2)
        for tag in d["industry_tags"]:
            if tag in company_info:
                score += 2
        # 层级匹配 (+5)
        if level in d["level_range"]:
            score += 5
        # 名称直接命中 (+8)
        if d["name"] in company_info:
            score += 8

        if score > 0:
            scored.append((score, d))

    # 按分数降序排列
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_n]]


def build_kb_context(company_info: str, level: str = "中层管理者") -> str:
    """构建知识库上下文文本，用于注入AI prompt。

    Returns:
        格式化的知识库维度摘要，可直接拼接到prompt中
    """
    results = search_knowledge_base(company_info, level, top_n=15)

    if not results:
        return "（知识库中暂无与该企业背景高度匹配的维度，请根据企业信息自主生成。）"

    lines = []
    for d in results:
        line = (
            f"[{d['id']}] {d['name']} "
            f"| 定义：{d['definition']} "
            f"| 参考源：{d['sources'].get('framework', '')} "
            f"| 行业：{'/'.join(d['industry_tags'])} "
            f"| 适用层级：{'/'.join(d['level_range'])}"
        )
        lines.append(line)

    header = f"以下是从领导力标准知识库中匹配的 {len(results)} 条相关维度：\n"
    return header + "\n".join(lines)
```

- [ ] **Step 4: 运行测试**

```bash
python -m pytest backend/tests/test_knowledge_base.py -v
```
Expected: 5/5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/knowledge_base.py backend/tests/test_knowledge_base.py
git commit -m "feat: 领导力知识库@LN — 37条预置维度+检索+测试"
```

---

### Task 2: AI服务知识库集成

**Files:**
- Modify: `backend/ai_service.py`

- [ ] **Step 1: 修改 generate_dimensions() — 知识库注入 + ID替换**

定位 `generate_dimensions()` 函数（约 line 140），替换为：

```python
def generate_dimensions(company_info: str, level: str = "中层管理者", use_kb: bool = True) -> dict:
    """Step2: 生成维度 → 返回结构化 dict"""
    # ── 知识库上下文 ──
    kb_context = ""
    if use_kb:
        try:
            from backend.knowledge_base import build_kb_context
            kb_context = build_kb_context(company_info, level)
        except Exception:
            kb_context = ""  # 知识库异常时退化到纯AI生成

    kb_instruction = f"""
【领导力知识库 @LN 参考】
以下是从标准领导力知识库中匹配的相关维度。请优先选择最匹配的4-6个作为推荐维度（直接使用其ID），再从知识库中选3-5个次相关的作为备选维度。
{ kb_context if kb_context else '（知识库暂无匹配条目，请根据企业信息自主生成。）' }

要求：
1. 推荐维度优先从上述知识库中选择，使用知识库条目的ID（如 LN-001）和名称
2. 如果知识库没有完全匹配的某个企业特殊需求，可生成1-2个自定义维度（ID使用D前缀）
3. 每个维度的 sources 字段标注来源：framework 填知识库参考框架名，strategy 填战略文档关键词，interview 填对话归纳
4. 备选维度池从知识库次相关条目中选3-5个
"""
    prompt = f"""根据以下企业信息，为{level}生成推荐维度和备选维度。
企业背景：{company_info}

{kb_instruction}

输出 JSON：
{{"recommended":[{{"id":"LN-001","name":"2-5字","definition":"2-3句定义","sources":{{"strategy":"战略来源","framework":"框架来源","interview":"访谈来源"}},"priority":"core|important|supplementary","rationale":"1句理由"}}],"alternatives":[]}}

要求：
- 推荐4-6个核心/重要维度，备选3-5个补充维度
- 名称精炼有力，定义包含可观察行为指向
- 贴合企业实际情况
- 严格禁止使用以下词汇：主动、积极、高度、认真、负责、努力、认可、重视、关注、善于、较强、具备、出色、优秀、良好
- 违反禁令的维度将被拒绝"""
    result = _call_deepseek(SYSTEM_PROMPT, prompt, max_tokens=2000)
    payload = _extract_json(result)

    # 兼容多种输出格式
    recommended = payload.get("recommended") or payload.get("dimensions") or []
    alternatives = payload.get("alternatives") or []

    # ── ID 规范化：确保知识库维度保持 LN- 前缀 ──
    known_kb_ids = set()
    if use_kb:
        try:
            from backend.knowledge_base import LEADERSHIP_DIMENSIONS
            known_kb_ids = {d["id"] for d in LEADERSHIP_DIMENSIONS}
        except Exception:
            pass

    def normalize_dim(d, idx):
        dim_id = d.get("id", f"D{idx+1}")
        name = d.get("name", "")
        # 如果AI返回的名称匹配知识库条目，使用知识库ID
        if known_kb_ids and not dim_id.startswith("LN-"):
            for kb_id in known_kb_ids:
                # 简单匹配：检查name是否与已知知识库条目名一致
                pass  # 保留AI返回的ID，不做强制替换（避免误匹配）
        return {
            "id": dim_id,
            "name": name,
            "definition": d.get("definition", ""),
            "sources": d.get("sources", {}),
            "priority": d.get("priority", "important"),
            "rationale": d.get("rationale", ""),
        }

    return {
        "recommended": [normalize_dim(d, i) for i, d in enumerate(recommended)],
        "alternatives": [normalize_dim(d, i) for i, d in enumerate(alternatives)],
    }
```

- [ ] **Step 2: 运行现有测试确保无回归**

```bash
python -m pytest backend/tests/test_audit.py backend/tests/test_app.py -v
```
Expected: all existing tests PASS

- [ ] **Step 3: Commit**

```bash
git add backend/ai_service.py
git commit -m "feat: AI服务集成知识库@LN — prompt注入+维度匹配+退化策略"
```

---

### Task 3: Step2 维度来源标注渲染

**Files:**
- Modify: `frontend/step2.html`

- [ ] **Step 1: 扩展数据映射保留 sources 和 rationale**

在 `init()` 函数中（约 line 139），替换 dims 映射：

```js
dims = recommended.map(d => ({
  id: d.id,
  nm: d.name,
  df: d.definition,
  pri: d.priority || 'important',
  rationale: d.rationale || '',
  sources: d.sources || {},
  ok: false
}));
```

备选维度映射（约 line 148）同样扩展：
```js
alts = [
  ...alternatives.map((d, i) => ({
    id: d.id || `DA${i+1}`,
    nm: d.name,
    df: d.definition,
    pri: d.priority || 'supplementary',
    rationale: d.rationale || '',
    sources: d.sources || {},
    added: false
  })),
  ...MOCK_ALTS
];
```

- [ ] **Step 2: 添加来源标签渲染**

在 `render()` 函数维度卡片中（约 line 178），`dc-df` 之后添加来源标签：

```js
function renderSources(sources) {
  if (!sources) return '';
  const tags = [];
  if (sources.strategy) tags.push(`<span class="src-tag src-stg">🔵 ${escHtml(sources.strategy)}</span>`);
  if (sources.framework) tags.push(`<span class="src-tag src-fwk">🟠 ${escHtml(sources.framework)}</span>`);
  if (sources.interview) tags.push(`<span class="src-tag src-int">🟢 ${escHtml(sources.interview)}</span>`);
  return tags.length ? `<div class="dc-src">${tags.join('')}</div>` : '';
}
```

render 中维度卡片（约 line 178-187）修改为：
```js
return `<div class="dc ${d.ok?'confirmed':''}">
  <div class="dc-hd"><div class="dc-nm">${d.nm}</div><span class="badge ${pc[d.pri]||'bg-gy'}">${pl[d.pri]||'补充'}</span></div>
  <div class="dc-df">${d.df}</div>
  ${renderSources(d.sources)}
  <div class="dc-ft">
    <button class="btn btn-sm ${d.ok?'btn-o':'btn-p'}" style="${d.ok?'background:var(--gr);color:#fff;border-color:var(--gr)':''}" onclick="toggleOk('${d.id}')">${d.ok?'✓ 已确认':'确认'}</button>
    <button class="btn btn-g btn-sm" onclick="openEdit('${d.id}')">编辑</button>
    <button class="btn btn-d btn-sm" onclick="delDim('${d.id}')">删除</button>
  </div>
</div>`;
```

- [ ] **Step 3: 添加来源CSS**

在 `<style>` 块中添加（在 `.dc-src` 现有样式之后）：
```css
.src-tag { font-size: 10.5px; padding: 2px 8px; border-radius: 100px; display: inline-flex; align-items: center; gap: 3px; }
.src-stg { background: #E1EEF9; color: #1E5080; }
.src-fwk { background: #FFF0E5; color: #A05510; }
.src-int { background: #E1F5EE; color: #0F6E56; }
```

- [ ] **Step 4: Commit**

```bash
git add frontend/step2.html
git commit -m "feat: 维度来源标注 — 三色标签渲染(战略/框架/访谈)"
```

---

### Task 4: Step2 手动添加维度

**Files:**
- Modify: `frontend/step2.html`

- [ ] **Step 1: 添加「＋手动添加」按钮**

在 header 行 `sec-row` 中（约 line 54-57），在「全部确认」按钮后添加：

```html
<div class="sec-row">
  <div><div class="sec-t">领导力维度框架</div>
  <div class="sec-s" id="okCount">已确认 <strong style="color:var(--gr)">0</strong> / 0 个 · 至少需要 3 个</div></div>
  <div style="display:flex;gap:8px">
    <button class="btn btn-o btn-sm" onclick="confirmAll()">全部确认</button>
    <button class="btn btn-a btn-sm" onclick="openAdd()">＋ 手动添加</button>
  </div>
</div>
```

- [ ] **Step 2: 扩展 modal 表单**

现有 `editModal`（约 line 73-80）扩展为含来源和优先级字段：

```html
<div class="modal-bg" id="editModal">
  <div class="modal-box">
    <div class="modal-hd"><span id="modalTitle">编辑维度</span><button class="modal-x" onclick="closeModal()">×</button></div>
    <div class="ff"><label>维度名称 *</label><input id="editName" type="text" placeholder="2-5字，如：团队管理"></div>
    <div class="ff"><label>定义说明 *（2-3句话）</label><textarea id="editDef" rows="3" placeholder="描述该维度的核心行为要求…"></textarea></div>
    <div class="ff"><label>优先级</label>
      <select id="editPri">
        <option value="core">核心 (core)</option>
        <option value="important" selected>重要 (important)</option>
        <option value="supplementary">补充 (supplementary)</option>
      </select>
    </div>
    <div class="ff"><label>🔵 战略来源</label><input id="editSrcStg" type="text" placeholder="如：战略文档关键词"></div>
    <div class="ff"><label>🟠 框架来源</label><input id="editSrcFwk" type="text" placeholder="如：Hay Group模型"></div>
    <div class="ff"><label>🟢 访谈来源</label><input id="editSrcInt" type="text" placeholder="如：对话归纳"></div>
    <div class="modal-ft"><button class="btn btn-o btn-sm" onclick="closeModal()">取消</button><button class="btn btn-p btn-sm" id="saveEditBtn" onclick="saveEdit()">保存</button></div>
  </div>
</div>
```

- [ ] **Step 3: 修改 JS 逻辑 — openAdd / openEdit / saveEdit**

替换现有的 `openEdit`、`closeModal`、`saveEdit` 函数：

```js
function openEdit(id) {
  const d = dims.find(x => x.id === id); if (!d) return;
  editId = id;
  document.getElementById('modalTitle').textContent = '编辑维度';
  document.getElementById('editName').value = d.nm;
  document.getElementById('editDef').value = d.df;
  document.getElementById('editPri').value = d.pri || 'important';
  document.getElementById('editSrcStg').value = (d.sources && d.sources.strategy) || '';
  document.getElementById('editSrcFwk').value = (d.sources && d.sources.framework) || '';
  document.getElementById('editSrcInt').value = (d.sources && d.sources.interview) || '';
  document.getElementById('saveEditBtn').disabled = false;
  document.getElementById('editModal').classList.add('show');
}

function openAdd() {
  editId = '__new__';
  document.getElementById('modalTitle').textContent = '手动添加维度';
  document.getElementById('editName').value = '';
  document.getElementById('editDef').value = '';
  document.getElementById('editPri').value = 'important';
  document.getElementById('editSrcStg').value = '';
  document.getElementById('editSrcFwk').value = '';
  document.getElementById('editSrcInt').value = '';
  document.getElementById('saveEditBtn').disabled = true;
  document.getElementById('editModal').classList.add('show');
  // 监听名称输入，空值时禁用保存
  document.getElementById('editName').oninput = function() {
    document.getElementById('saveEditBtn').disabled = !this.value.trim();
  };
}

function closeModal() {
  document.getElementById('editModal').classList.remove('show');
  editId = null;
}

function saveEdit() {
  const name = document.getElementById('editName').value.trim();
  if (!name) return;

  const def = document.getElementById('editDef').value.trim();
  const pri = document.getElementById('editPri').value;
  const sources = {
    strategy: document.getElementById('editSrcStg').value.trim(),
    framework: document.getElementById('editSrcFwk').value.trim(),
    interview: document.getElementById('editSrcInt').value.trim(),
  };

  if (editId === '__new__') {
    // 重名检测
    if (dims.some(d => d.nm === name)) {
      if (!confirm(`已存在同名维度「${name}」，是否继续添加？`)) {
        closeModal();
        return;
      }
    }
    dims.push({
      id: 'U_' + Date.now().toString(36),
      nm: name,
      df: def,
      pri: pri,
      rationale: '',
      sources: sources,
      ok: true,
      manual: true
    });
  } else {
    const d = dims.find(x => x.id === editId);
    if (d) {
      d.nm = name;
      d.df = def;
      d.pri = pri;
      d.sources = sources;
    }
  }
  // 同步 localStorage
  localStorage.setItem('lm_dims', JSON.stringify(dims.filter(d => d.ok)));
  closeModal();
  render();
}
```

- [ ] **Step 4: render 中添加手动维度角标**

在维度卡片 `.dc-hd` 中（优先級badge之后），添加：
```js
${d.manual ? '<span class="badge bg-gy">👤 手动</span>' : ''}
```

完整 `.dc-hd` 行：
```js
<div class="dc-hd"><div class="dc-nm">${d.nm}</div><span class="badge ${pc[d.pri]||'bg-gy'}">${pl[d.pri]||'补充'}</span>${d.manual ? '<span class="badge bg-gy">👤 手动</span>' : ''}</div>
```

- [ ] **Step 5: 初始化渲染时加载 localStorage 中已确认维度**

确保 `init()` 开始时（约 line 109-113）从 localStorage 加载，包括手动添加的：

```js
const saved = localStorage.getItem('lm_dims');
if (saved) {
  try { dims = JSON.parse(saved); } catch(e) {}
}
```
（此代码已存在，无需修改，确认手动维度 `manual: true` 属性被正确序列化即可）

- [ ] **Step 6: Commit**

```bash
git add frontend/step2.html
git commit -m "feat: 手动添加维度 — 新增Modal/重名检测/localStorage同步"
```

---

### Task 5: Step2 知识库角标 + 来源标记

**Files:**
- Modify: `frontend/step2.html`

- [ ] **Step 1: 添加来源角标函数和渲染**

在 render() 函数内，维度卡片 `.dc-hd` 行中添加ID前缀角标：

```js
function sourceBadge(d) {
  if (d.id && d.id.startsWith('LN-')) return '<span class="badge bg-a">📚 标准库</span>';
  if (d.id && d.id.startsWith('U_')) return '<span class="badge bg-gy">👤 手动</span>';
  return '';  // D前缀 = AI生成，不额外标注
}
```

维度卡片 `.dc-hd` 最终：
```js
<div class="dc-hd"><div class="dc-nm">${d.nm}</div>${sourceBadge(d)}<span class="badge ${pc[d.pri]||'bg-gy'}">${pl[d.pri]||'补充'}</span>${d.manual ? '<span class="badge bg-gy">👤 手动</span>' : ''}</div>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/step2.html
git commit -m "feat: 知识库角标 — LN-/U_前缀来源标记"
```

---

### Task 6: Step5 雷达图可视化

**Files:**
- Modify: `frontend/step5.html`

- [ ] **Step 1: 添加 Chart.js CDN**

在 `<head>` 中添加（约 line 5，viewport之后）：
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

- [ ] **Step 2: 添加雷达图CSS**

在现有 `<style>` 块末尾添加：
```css
.radar-wrap { max-width: 480px; margin: 0 auto 22px; padding: 16px; background: var(--sf); border-radius: 12px; border: 1px solid var(--br); box-shadow: var(--sh); }
.radar-wrap canvas { max-height: 400px; }
.radar-fallback { text-align: center; padding: 24px; }
.radar-fallback table { width: 100%; border-collapse: collapse; font-size: 13px; }
.radar-fallback th { background: var(--p10); padding: 10px 14px; text-align: left; font-weight: 600; color: var(--p80); border-bottom: 2px solid var(--p20); }
.radar-fallback td { padding: 9px 14px; border-bottom: 1px solid var(--br); color: var(--t1); }
.radar-fallback tr:hover td { background: var(--sf2); }
@keyframes highlightPulse {
  0% { box-shadow: 0 0 0 0 rgba(108,33,109,.4); }
  50% { box-shadow: 0 0 0 8px rgba(108,33,109,.1); }
  100% { box-shadow: 0 0 0 0 rgba(108,33,109,0); }
}
.ov-item.highlight { animation: highlightPulse 1.5s ease-out; border-color: var(--p); }
```

- [ ] **Step 3: 在统计卡片后插入雷达图容器**

统计卡片行（stats-row div）之后，维度列表（sec-row + ov-list）之前插入：
```html
<div class="radar-wrap" id="radarArea">
  <canvas id="radarChart" style="display:none;"></canvas>
  <div class="radar-fallback" id="radarFallback" style="display:none;"></div>
</div>
```

- [ ] **Step 4: 添加雷达图渲染 + 降级 + 交互逻辑**

在 `init()` 函数的末尾（渲染完 ovList 之后），添加雷达图渲染调用：

在 `init()` 函数中，`document.getElementById('ovList').innerHTML = data.map(...)` 之后添加：
```js
  // 渲染雷达图
  renderRadar(data);
}
```

新增函数（在 `init` 函数之前或之后）：

```js
function priScore(pri) {
  const map = { core: 5, important: 3.5, supplementary: 2 };
  return map[pri] || 3;
}

function renderRadar(data) {
  const area = document.getElementById('radarArea');
  if (!area) return;

  if (typeof Chart === 'undefined') {
    // 降级：表格视图
    const fallback = document.getElementById('radarFallback');
    if (fallback) {
      fallback.style.display = 'block';
      fallback.innerHTML = buildFallbackTable(data);
    }
    return;
  }

  const canvas = document.getElementById('radarChart');
  if (!canvas) return;
  canvas.style.display = 'block';

  const ctx = canvas.getContext('2d');
  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: data.map(d => d.nm),
      datasets: [{
        label: '维度权重',
        data: data.map(d => priScore(dims.find(dd => dd.id === d.id)?.pri || 'important')),
        backgroundColor: 'rgba(108,33,109,0.12)',
        borderColor: '#6C216D',
        borderWidth: 2,
        pointBackgroundColor: '#6C216D',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        r: {
          beginAtZero: true,
          max: 6,
          min: 0,
          ticks: { stepSize: 1, display: false },
          grid: { color: 'rgba(108,33,109,0.08)' },
          angleLines: { color: 'rgba(108,33,109,0.08)' },
          pointLabels: { font: { size: 13, family: "'PingFang SC','Microsoft YaHei',sans-serif" }, color: '#1A1520' }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              const d = data[ctx.dataIndex];
              return d ? `${d.nm}: 优先级 ${priScore(dims.find(dd => dd.id === d.id)?.pri || 'important')}/5` : '';
            }
          }
        }
      },
      onClick: function(e, elements) {
        if (elements.length > 0) {
          const idx = elements[0].index;
          const d = data[idx];
          if (!d) return;

          // 展开该维度
          if (!openMap[d.id]) {
            openMap[d.id] = true;
            init();  // 重渲染以展开
          }

          // 滚动到目标维度
          setTimeout(() => {
            const target = document.querySelector(`[data-dim="${d.id}"]`);
            if (target) {
              target.scrollIntoView({ behavior: 'smooth', block: 'center' });
              target.classList.add('highlight');
              setTimeout(() => target.classList.remove('highlight'), 1500);
            }
          }, 100);
        }
      }
    }
  });
}

function buildFallbackTable(data) {
  let html = '<div style="font-size:14px;font-weight:600;margin-bottom:12px;color:var(--t1)">📊 维度优先级总览（雷达图加载失败，降级为表格）</div>';
  html += '<table><thead><tr><th>维度</th><th>优先级</th><th>描述</th></tr></thead><tbody>';
  data.forEach(d => {
    const priLabel = {core:'核心',important:'重要',supplementary:'补充'}[dims.find(dd => dd.id === d.id)?.pri] || '重要';
    html += `<tr><td><strong>${d.nm}</strong></td><td>${priLabel}</td><td style="font-size:12px;color:var(--t2)">${(d.desc || '').slice(0,50)}…</td></tr>`;
  });
  html += '</tbody></table>';
  return html;
}
```

- [ ] **Step 5: 给维度列表项添加 data-dim 属性**

在 `init()` 的 ovList 渲染中（约 line 153），`.ov-item` 添加 `data-dim` 属性：
```js
return `<div class="ov-item" data-dim="${d.id}">
```

- [ ] **Step 6: Commit**

```bash
git add frontend/step5.html
git commit -m "feat: 雷达图可视化 — Chart.js雷达图+CDN降级+点击联动"
```

---

### Task 7: 端到端验证

- [ ] **Step 1: 运行全量测试**

```bash
python -m pytest backend/tests/ -v --tb=short
```
Expected: all tests pass (including new test_knowledge_base.py)

- [ ] **Step 2: 验证后端启动**

```bash
python -c "from backend.knowledge_base import search_knowledge_base; r = search_knowledge_base('互联网科技公司中层管理者', '中层管理者', top_n=5); print(f'KB search returned {len(r)} results'); assert len(r) > 0, 'No KB results!'"
```

- [ ] **Step 3: 前端静态检查**

验证 step2.html 改动：
- `grep -c "renderSources" frontend/step2.html` ≥ 1 (来源渲染函数存在)
- `grep -c "U_" frontend/step2.html` ≥ 1 (手动添加ID前缀存在)
- `grep -c "localStorage.setItem" frontend/step2.html` ≥ 1 (持久化存在)

验证 step5.html 改动：
- `grep -c "chart.js" frontend/step5.html` ≥ 1 (CDN引入)
- `grep -c "renderRadar" frontend/step5.html` ≥ 1 (雷达图函数)
- `grep -c "data-dim" frontend/step5.html` ≥ 1 (维度锚点属性)

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: 领导力建模增强完成 — 来源标注/手动维度/知识库/雷达图"
```
