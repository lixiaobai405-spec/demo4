"""
领导力知识库 — 37 条预置领导力维度
"""
import re

# ─────────────────────────────────────────────────────────
# LEADERSHIP_DIMENSIONS
# 37 条预置维度，分为 5 个集群
#   LN-001~LN-008  战略与商业 (8)
#   LN-009~LN-016  团队与人才 (8)
#   LN-017~LN-022  执行与流程 (6)
#   LN-023~LN-030  协同与影响 (7)
#   LN-031~LN-037  自我与认知 (7)
# ─────────────────────────────────────────────────────────

LEADERSHIP_DIMENSIONS = [
    # ═══════════════════════════════════════════════════════
    # 战略与商业 (8)
    # ═══════════════════════════════════════════════════════
    {
        "id": "LN-001",
        "name": "战略拆解与落地",
        "definition": "将公司战略目标转化为部门级可执行计划，设定关键里程碑和可衡量指标，定期复盘进展并动态调整资源配置，确保团队工作与战略方向一致。",
        "industry_tags": ["通用", "互联网", "科技", "制造", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Hay Group 领导力素质模型",
            "strategy": "素质模型策略",
            "reference": "Hay Group",
        },
        "keywords": ["战略", "拆解", "目标", "落地", "执行", "规划", "复盘", "资源配置"],
    },
    {
        "id": "LN-002",
        "name": "商业敏锐度",
        "definition": "深度理解行业趋势和竞争格局，将市场洞察转化为业务机会识别，在决策中平衡短期收益与长期价值，推动业务模式持续进化。",
        "industry_tags": ["通用", "互联网", "金融", "零售", "科技"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Lominger 胜任力卡片",
            "strategy": "胜任力评估策略",
            "reference": "Lominger",
        },
        "keywords": ["商业", "市场", "竞争", "趋势", "业务", "洞察", "机会", "收益"],
    },
    {
        "id": "LN-003",
        "name": "变革引领",
        "definition": "识别组织变革需求，制定变革路径图，化解变革阻力，带领团队在不确定性中保持方向感和凝聚力，将变革转化为组织能力提升。",
        "industry_tags": ["通用", "科技", "制造", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Kotter 变革领导力模型",
            "strategy": "变革管理策略",
            "reference": "Kotter",
        },
        "keywords": ["变革", "转型", "组织", "阻力", "引领", "不确定性", "适应"],
    },
    {
        "id": "LN-004",
        "name": "全局思维",
        "definition": "跳出部门视角，从公司整体利益出发分析问题和制定决策，理解各业务单元之间的关联与制约，在局部优化和全局最优之间做出理性权衡。",
        "industry_tags": ["通用", "科技", "制造", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Spencer 胜任力词典",
            "strategy": "胜任力词典策略",
            "reference": "Spencer",
        },
        "keywords": ["全局", "系统", "部门", "平衡", "关联", "整体", "格局", "视角"],
    },
    {
        "id": "LN-005",
        "name": "创新驱动",
        "definition": "在团队中建立鼓励试错的创新氛围，主动引入新方法新技术解决业务难题，将创意转化为可落地的产品改进或流程优化方案并衡量效果。",
        "industry_tags": ["互联网", "科技", "零售", "通用"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "Kirkpatrick 创新领导力模型",
            "strategy": "创新管理策略",
            "reference": "Kirkpatrick",
        },
        "keywords": ["创新", "试错", "创意", "改进", "优化", "实验", "突破", "探索"],
    },
    {
        "id": "LN-006",
        "name": "风险管控",
        "definition": "系统识别业务和运营中的潜在风险，建立预警机制和应急预案，在风险发生前采取预防措施，风险发生后快速响应控制损失范围。",
        "industry_tags": ["金融", "制造", "科技", "通用"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "COSO 风险管理框架",
            "strategy": "风险管理策略",
            "reference": "COSO",
        },
        "keywords": ["风险", "预警", "应急", "预防", "控制", "合规", "安全", "审计"],
    },
    {
        "id": "LN-007",
        "name": "业务规划",
        "definition": "基于数据和市场分析制定年度业务计划，将模糊的业务方向量化为可追踪的KPI体系，在资源约束下排出优先级，确保核心目标不受日常事务干扰。",
        "industry_tags": ["通用", "互联网", "金融", "零售"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "平衡计分卡 BSC",
            "strategy": "战略规划策略",
            "reference": "BSC",
        },
        "keywords": ["规划", "预算", "KPI", "优先级", "指标", "资源", "年度", "目标"],
    },
    {
        "id": "LN-008",
        "name": "客户导向",
        "definition": "深度理解内外部客户需求与痛点，在决策中优先考虑客户价值创造，将客户反馈系统性地转化为产品和服务改进，建立以客户为中心的团队文化。",
        "industry_tags": ["通用", "互联网", "零售", "金融", "服务"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "亚马逊领导力原则 Customer Obsession",
            "strategy": "客户中心策略",
            "reference": "Amazon Leadership Principles",
        },
        "keywords": ["客户", "需求", "痛点", "价值", "反馈", "服务", "体验", "满意度"],
    },
    # ═══════════════════════════════════════════════════════
    # 团队与人才 (8)
    # ═══════════════════════════════════════════════════════
    {
        "id": "LN-009",
        "name": "团队赋能",
        "definition": "识别团队成员的能力差距和发展潜力，通过教练式辅导、针对性授权和项目历练激发个体成长，构建自我驱动的学习型团队氛围。",
        "industry_tags": ["通用", "互联网", "科技", "制造"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Google Project Oxygen",
            "strategy": "团队赋能策略",
            "reference": "Google Project Oxygen",
        },
        "keywords": ["赋能", "辅导", "教练", "授权", "成长", "潜力", "能力", "发展"],
    },
    {
        "id": "LN-010",
        "name": "人才识别与梯队建设",
        "definition": "建立团队人才评估标准，识别高潜质成员并制定个性化发展计划，确保关键岗位有明确的后备人选，降低人才断层对业务的影响。",
        "industry_tags": ["通用", "科技", "金融", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "GE Session C 人才盘点",
            "strategy": "人才盘点策略",
            "reference": "GE Session C",
        },
        "keywords": ["人才", "梯队", "后备", "高潜", "盘点", "继任", "评估", "识别"],
    },
    {
        "id": "LN-011",
        "name": "绩效推动",
        "definition": "设定清晰的绩效标准和期望，通过持续反馈而非年终考核驱动业绩改善，对低绩效行为及时介入纠偏，对高绩效行为即时认可和复制推广。",
        "industry_tags": ["通用", "互联网", "金融", "零售"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Deloitte 绩效管理重构",
            "strategy": "绩效管理策略",
            "reference": "Deloitte",
        },
        "keywords": ["绩效", "反馈", "考核", "目标", "改善", "认可", "标准", "KPI"],
    },
    {
        "id": "LN-012",
        "name": "激励人心",
        "definition": "理解不同类型成员的驱动力来源，将工作本身设计为激励载体，通过意义感、自主权和成长空间激发内在动机，而非仅依赖物质奖励。",
        "industry_tags": ["通用", "互联网", "科技"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Daniel Pink 驱动力3.0",
            "strategy": "激励管理策略",
            "reference": "Daniel Pink",
        },
        "keywords": ["激励", "动机", "驱动力", "意义", "自主", "认可", "敬业", "士气"],
    },
    {
        "id": "LN-013",
        "name": "冲突化解",
        "definition": "识别团队内部和跨部门冲突的根源，运用双赢思维引导各方从立场之争转向利益协同，将建设性冲突转化为团队创新和改进的契机。",
        "industry_tags": ["通用", "制造", "金融"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Thomas-Kilmann 冲突模式模型",
            "strategy": "冲突管理策略",
            "reference": "Thomas-Kilmann",
        },
        "keywords": ["冲突", "调解", "分歧", "协商", "双赢", "利益", "斡旋", "化解"],
    },
    {
        "id": "LN-014",
        "name": "凝聚力打造",
        "definition": "通过团队愿景共启、成功经验共享和困难时刻的并肩作战建立信任纽带，营造心理安全氛围使成员敢于表达不同意见和承担人际风险。",
        "industry_tags": ["通用", "互联网", "科技"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Google Project Aristotle",
            "strategy": "团队建设策略",
            "reference": "Google Project Aristotle",
        },
        "keywords": ["凝聚", "信任", "安全", "氛围", "团队", "默契", "共享", "归属"],
    },
    {
        "id": "LN-015",
        "name": "授权管理",
        "definition": "根据成员能力和任务复杂度匹配合适的授权层级，在授权过程中明确边界和决策权限，授权后提供支持而非干预，让成员在承担责任中加速成长。",
        "industry_tags": ["通用", "互联网", "科技", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Situational Leadership II",
            "strategy": "情境领导策略",
            "reference": "Situational Leadership II",
        },
        "keywords": ["授权", "边界", "权限", "放权", "决策", "信任", "赋能", "自主"],
    },
    {
        "id": "LN-016",
        "name": "团队管理",
        "definition": "合理配置团队成员角色与任务分配，建立高效的工作机制和沟通节奏，平衡团队工作负荷与成员发展需求，打造稳定交付的高绩效团队。",
        "industry_tags": ["通用", "互联网", "科技", "制造", "金融"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Tuckman 团队发展阶段模型",
            "strategy": "团队管理策略",
            "reference": "Tuckman",
        },
        "keywords": ["团队", "管理", "角色", "任务", "机制", "沟通", "配置", "效率"],
    },
    # ═══════════════════════════════════════════════════════
    # 执行与流程 (6)
    # ═══════════════════════════════════════════════════════
    {
        "id": "LN-017",
        "name": "目标导向执行",
        "definition": "将模糊的方向转化为清晰可衡量的行动方案，设定明确的时间节点和交付标准，在推进过程中持续追踪关键里程碑，确保承诺结果按期达成。",
        "industry_tags": ["通用", "制造", "金融", "零售"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "OKR 目标与关键结果",
            "strategy": "目标管理策略",
            "reference": "OKR",
        },
        "keywords": ["执行", "目标", "交付", "里程碑", "追踪", "结果", "承诺", "达成"],
    },
    {
        "id": "LN-018",
        "name": "过程管控",
        "definition": "建立可视化进度追踪机制，定期检查关键节点完成质量，发现偏差当周启动纠偏动作而非等待月末复盘，将过程数据作为持续改进的依据。",
        "industry_tags": ["制造", "金融", "通用"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "精益管理 Lean Management",
            "strategy": "过程管理策略",
            "reference": "Lean Management",
        },
        "keywords": ["过程", "进度", "节点", "纠偏", "追踪", "检查", "质量", "数据"],
    },
    {
        "id": "LN-019",
        "name": "资源统筹",
        "definition": "在资源有限的前提下合理分配人力、预算和时间到各项任务，预判资源瓶颈并提前协调，在优先级冲突时基于业务价值而非惯性做出取舍。",
        "industry_tags": ["通用", "互联网", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "PMBOK",
            "strategy": "资源管理策略",
            "reference": "PMBOK",
        },
        "keywords": ["资源", "预算", "分配", "统筹", "优先级", "瓶颈", "协调", "取舍"],
    },
    {
        "id": "LN-020",
        "name": "数据决策",
        "definition": "在管理决策中基于数据分析而非直觉判断，建立关键业务指标体系和数据仪表盘，用数据验证假设，将数据洞察转化为可操作的业务行动。",
        "industry_tags": ["互联网", "科技", "金融", "零售"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "数据驱动决策 DDDM",
            "strategy": "数据决策策略",
            "reference": "DDDM",
        },
        "keywords": ["数据", "决策", "分析", "指标", "仪表盘", "验证", "洞察", "假设"],
    },
    {
        "id": "LN-021",
        "name": "流程优化",
        "definition": "定期审视现有工作流程中的浪费和低效环节，运用流程改进工具进行系统性优化，推动标准化和自动化以减少人为差错，沉淀最佳实践。",
        "industry_tags": ["制造", "金融", "科技", "通用"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "六西格玛 Six Sigma",
            "strategy": "流程优化策略",
            "reference": "Six Sigma",
        },
        "keywords": ["流程", "优化", "效率", "标准化", "自动化", "浪费", "改进", "沉淀"],
    },
    {
        "id": "LN-022",
        "name": "质量意识",
        "definition": "在交付的每个环节建立质量标准和控制节点，对输出的准确性和完整性负责，建立团队一次做对的质量文化，降低返工成本和客户投诉。",
        "industry_tags": ["制造", "金融", "科技", "通用"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "全面质量管理 TQM",
            "strategy": "质量管理策略",
            "reference": "TQM",
        },
        "keywords": ["质量", "标准", "准确", "完整", "控制", "返工", "检查", "细节"],
    },
    # ═══════════════════════════════════════════════════════
    # 协同与影响 (7)
    # ═══════════════════════════════════════════════════════
    {
        "id": "LN-023",
        "name": "跨部门协作",
        "definition": "主动识别跨部门协作节点和依赖关系，建立定期同步机制和信息共享平台，在资源冲突和利益分歧时介入斡旋，推动多方达成共识确保项目推进。",
        "industry_tags": ["通用", "互联网", "科技", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "横向领导力 Lateral Leadership",
            "strategy": "协作管理策略",
            "reference": "Lateral Leadership",
        },
        "keywords": ["协作", "跨部门", "协同", "同步", "共识", "斡旋", "依赖", "信息"],
    },
    {
        "id": "LN-024",
        "name": "沟通影响力",
        "definition": "根据沟通对象和场景灵活调整表达策略：向上聚焦结论和风险，横向强调共同利益和互换价值，向下注重拆解和激励，确保信息被准确理解和采纳。",
        "industry_tags": ["通用", "金融", "互联网"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "哈佛商学院影响力沟通模型",
            "strategy": "沟通管理策略",
            "reference": "Harvard Business School",
        },
        "keywords": ["沟通", "影响", "表达", "汇报", "说服", "演讲", "倾听", "策略"],
    },
    {
        "id": "LN-025",
        "name": "向上管理",
        "definition": "主动对齐上级的优先级和期望，预判上级的信息需求和决策节点并在其提问前提供关键信息，以数据和方案支撑提案而非仅抛出问题。",
        "industry_tags": ["通用", "互联网", "金融"],
        "level_range": ["基层", "中层"],
        "sources": {
            "framework": "Harvard Business Review Managing Up",
            "strategy": "向上管理策略",
            "reference": "Harvard Business Review",
        },
        "keywords": ["向上", "汇报", "对齐", "预判", "上级", "提案", "决策", "期望"],
    },
    {
        "id": "LN-026",
        "name": "伙伴关系构建",
        "definition": "识别外部合作伙伴和供应商中的战略价值节点，建立互利共赢的长期合作机制，在合作中保持专业边界的同时深度理解对方利益诉求。",
        "industry_tags": ["制造", "零售", "科技"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "战略供应商管理 SRM",
            "strategy": "供应商管理策略",
            "reference": "SRM",
        },
        "keywords": ["伙伴", "合作", "供应商", "联盟", "共赢", "边界", "长期", "关系"],
    },
    {
        "id": "LN-027",
        "name": "谈判斡旋",
        "definition": "在资源分配和利益协调中运用谈判技巧创造增量价值而非零和博弈，深入理解各方底线和谈判空间，在坚持原则的前提下灵活设计方案达成协议。",
        "industry_tags": ["通用", "金融", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "哈佛谈判术 Getting to Yes",
            "strategy": "谈判管理策略",
            "reference": "Getting to Yes",
        },
        "keywords": ["谈判", "斡旋", "协议", "底线", "博弈", "价值", "方案", "让步"],
    },
    {
        "id": "LN-028",
        "name": "生态构建",
        "definition": "识别产业链中的关键节点和互补资源，主动构建外部合作网络和资源生态圈，将零散的外部关系升级为体系化可复用的合作资产。",
        "industry_tags": ["互联网", "科技", "金融"],
        "level_range": ["高层"],
        "sources": {
            "framework": "平台生态系统战略",
            "strategy": "生态构建策略",
            "reference": "Platform Ecosystem Strategy",
        },
        "keywords": ["生态", "产业", "网络", "平台", "资源", "整合", "链", "互补"],
    },
    {
        "id": "LN-029",
        "name": "文化塑造",
        "definition": "以身作则践行组织价值观，通过日常行为、机制设计和符号化事件将抽象价值观转化为团队成员的共识和习惯，在文化冲突时坚定守护核心原则。",
        "industry_tags": ["通用", "互联网", "科技"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Schein 组织文化三层模型",
            "strategy": "文化建设策略",
            "reference": "Schein",
        },
        "keywords": ["文化", "价值", "理念", "共识", "习惯", "机制", "榜样", "原则"],
    },
    {
        "id": "LN-030",
        "name": "利益相关者管理",
        "definition": "系统识别所有受决策影响的内外部利益相关者，分析各自的立场、影响力和期望，在关键决策前制定沟通和参与计划确保各方被听见和尊重。",
        "industry_tags": ["通用", "金融", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "PMBOK 利益相关者管理",
            "strategy": "利益相关者管理策略",
            "reference": "PMBOK",
        },
        "keywords": ["利益", "相关者", "影响", "立场", "沟通", "参与", "关系", "期望"],
    },
    # ═══════════════════════════════════════════════════════
    # 自我与认知 (7)
    # ═══════════════════════════════════════════════════════
    {
        "id": "LN-031",
        "name": "学习敏锐度",
        "definition": "在新领域和陌生情境中快速识别关键知识并建立认知框架，将过往经验灵活迁移到新问题解决中，对自己的知识盲区保持清醒并主动补足。",
        "industry_tags": ["通用", "互联网", "科技", "金融"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "Learning Agility Lominger",
            "strategy": "学习发展策略",
            "reference": "Lominger",
        },
        "keywords": ["学习", "敏锐", "迁移", "适应", "框架", "盲区", "认知", "成长"],
    },
    {
        "id": "LN-032",
        "name": "情绪韧性",
        "definition": "在高压和挫折情境下保持冷静和理性判断，不被情绪左右决策质量，从失败中快速恢复并提炼经验教训，为团队在动荡时期提供情绪稳定锚。",
        "industry_tags": ["通用", "互联网", "金融"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "EQ-i 2.0 情绪智力模型",
            "strategy": "情绪管理策略",
            "reference": "EQ-i 2.0",
        },
        "keywords": ["情绪", "韧性", "压力", "恢复", "冷静", "挫折", "适应", "平衡"],
    },
    {
        "id": "LN-033",
        "name": "系统思考",
        "definition": "识别复杂问题中的因果关系和反馈回路，避免线性归因和局部优化陷阱，在决策时考虑二阶效应和长期动态，帮助团队看清冰山之下的结构性因素。",
        "industry_tags": ["科技", "金融", "制造"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "第五项修炼 系统思考 Senge",
            "strategy": "系统思考策略",
            "reference": "Senge",
        },
        "keywords": ["系统", "因果", "反馈", "结构", "复杂", "长期", "分析", "模式"],
    },
    {
        "id": "LN-034",
        "name": "概念思维",
        "definition": "从碎片化的信息中提炼出模式和规律，将具体问题抽象为可复用的分析框架，在不同领域间建立类比和联系以产生创新性的解决方案。",
        "industry_tags": ["科技", "互联网", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "McClelland 胜任力词典",
            "strategy": "概念思维策略",
            "reference": "McClelland",
        },
        "keywords": ["概念", "抽象", "规律", "框架", "模式", "提炼", "类比", "归纳"],
    },
    {
        "id": "LN-035",
        "name": "成就导向",
        "definition": "为自己和团队设定挑战性的目标而非安于现状，持续寻找超越标准和期望的机会，对结果有强烈的拥有感不达目标不罢休。",
        "industry_tags": ["通用", "互联网", "金融", "零售"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "McClelland 成就动机理论",
            "strategy": "成就导向策略",
            "reference": "McClelland",
        },
        "keywords": ["成就", "挑战", "超越", "结果", "卓越", "追求", "突破", "标准"],
    },
    {
        "id": "LN-036",
        "name": "诚信正直",
        "definition": "在利益冲突和压力下坚持道德底线和职业操守，承诺的事项坚决兑现，敢于承认错误和承担责任，在组织中建立可靠的个人品牌。",
        "industry_tags": ["通用", "金融"],
        "level_range": ["基层", "中层", "高层"],
        "sources": {
            "framework": "McClelland Integrity",
            "strategy": "诚信管理策略",
            "reference": "McClelland",
        },
        "keywords": ["诚信", "正直", "道德", "责任", "承诺", "可靠", "底线", "操守"],
    },
    {
        "id": "LN-037",
        "name": "认知灵活性",
        "definition": "在矛盾信息和多变情境中保持思维开放，不执着于既定方案，根据新信息快速调整判断和策略，在模糊性中做出合理决策而非等待完全信息。",
        "industry_tags": ["互联网", "科技", "金融"],
        "level_range": ["中层", "高层"],
        "sources": {
            "framework": "Cognitive Flexibility Theory",
            "strategy": "认知灵活策略",
            "reference": "Cognitive Flexibility Theory",
        },
        "keywords": ["灵活", "适应", "调整", "开放", "模糊", "信息", "判断", "转变"],
    },
]


# ─────────────────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────────────────

def search_knowledge_base(company_info: str, level: str, top_n: int = 15) -> list[dict]:
    """关键词 + 标签 + 层级匹配检索。

    1. 按标点分词 + 2-gram 切分
    2. 计分：关键词命中 +3，2-gram 部分匹配 +1，行业标签 +2，层级 +5，名称直中 +8
    3. 返回 top_n 条降序
    """
    if not company_info or not company_info.strip():
        return LEADERSHIP_DIMENSIONS[:top_n]

    # Tokenize — split by punctuation
    raw_tokens = re.split(r"[，、。；：？！.,;:!?\s\n\r\t]+", company_info)
    tokens = [t.strip() for t in raw_tokens if t.strip()]

    # 2-gram segmentation for partial matching
    bigrams: set[str] = set()
    for token in tokens:
        for i in range(len(token) - 1):
            bigrams.add(token[i : i + 2])

    all_text = company_info

    scored: list[tuple[int, dict]] = []
    for dim in LEADERSHIP_DIMENSIONS:
        score = 0

        # Name direct hit +8
        if dim["name"] in all_text:
            score += 8

        # Keyword hits +3 each / partial match via 2-gram +1 each
        for kw in dim["keywords"]:
            if kw in all_text:
                score += 3
            else:
                kw_bigrams = {kw[i : i + 2] for i in range(len(kw) - 1)}
                if kw_bigrams & bigrams:
                    score += 1

        # Industry tag match +2 each
        for tag in dim["industry_tags"]:
            if tag in all_text:
                score += 2

        # Level match +5
        if level:
            for lvl in dim["level_range"]:
                if lvl in level or level in lvl:
                    score += 5
                    break

        scored.append((score, dim))

    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [dim for _, dim in scored[:top_n]]


# ─────────────────────────────────────────────────────────
# Context builder
# ─────────────────────────────────────────────────────────

def build_kb_context(company_info: str, level: str = "中层管理者") -> str:
    """将检索结果格式化为提示文本。"""
    results = search_knowledge_base(company_info, level, top_n=15)

    lines = ["【领导力知识库匹配结果】"]
    lines.append(f"匹配维度数: {len(results)}")
    lines.append("")

    for dim in results:
        tags = "/".join(dim["industry_tags"])
        levels = "/".join(dim["level_range"])
        lines.append(f"{dim['id']} {dim['name']}")
        lines.append(f"  定义: {dim['definition']}")
        lines.append(f"  适用行业: {tags} | 适用层级: {levels}")
        lines.append(f"  关键词: {'/'.join(dim['keywords'])}")
        lines.append(f"  来源: {dim['sources']['framework']}")
        lines.append("")

    return "\n".join(lines)
