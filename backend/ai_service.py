"""
AI Service — DeepSeek API wrapper for leadership modeling.
Uses OpenAI-compatible API protocol.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from backend.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_CHAT_MODEL,
    DEEPSEEK_REASONER_MODEL,
)

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# ── System Prompts ─────────────────────────────────────────────

SYSTEM_PROMPT = """你是一名资深领导力建模顾问，服务于一家快速成长的中国科技企业。
你的专业领域包括：胜任力模型构建、BARS行为锚定、领导力发展体系设计。

企业背景：
- 行业：科技/SaaS/To B 服务
- 规模：500-1000人，快速扩张期
- 管理层级：基层管理者（团队长）、中层管理者（部门经理）、高层管理者（VP/总经理）

输出要求：
- 使用专业但不晦涩的中文
- 结构清晰，要点明确
- 行为描述必须以可观察的动词开头
- 所有输出贴合中国科技企业管理实际
"""

DOC_ANALYSIS_SYS = """你是一名领导力建模顾问，负责从企业文档中提取与领导力建模相关的核心信息。
严格按以下格式输出，内容简洁、信息密度高：

【战略关键词】：3-8个战略方向关键词（逗号分隔）
【高绩效行为特征】：2-4条高绩效管理者典型行为描述
【能力要求关键词】：文档中出现的管理者能力要求关键词（逗号分隔）
【建模参考重点】：1-2条最值得纳入领导力模型的核心洞察

用中文回答，每项不超过150字。文档内容不足时如实说明。"""

DIMENSION_PROMPT = """基于以下企业信息，生成5-6个针对{level}的领导力维度。
每个维度包含：名称（2-4字）、定义（2-3句话）、优先级（core/important/supplementary）。

企业背景：{company_info}

输出严格按JSON格式（不要markdown标记）：
{{
  "dimensions": [
    {{"id": "D1", "name": "维度名", "definition": "定义描述...", "priority": "core"}}
  ]
}}

要求：
- 核心维度(core) 3-4个，重要维度(important) 1-2个，补充维度(supplementary) 0-1个
- 维度名称精炼有力，定义包含可观察的行为指向
- 贴合企业实际情况，不要泛泛而谈
"""

DESCRIPTION_PROMPT = """基于以下领导力维度，为{level}管理者生成每个维度的定位描述。
描述需包含该维度在{level}层级的具体体现、关键动作和可观察结果。

维度列表：{dimensions_json}

企业背景：{company_info}

输出严格按JSON格式（不要markdown标记）：
{{
  "descriptions": [
    {{"dimension_id": "D1", "dimension_name": "维度名", "description": "定位描述...", "qc_pass": true, "qc_issues": []}}
  ]
}}

要求：
- 每个描述150-250字
- 使用可观察的行为动词（如"制定""推动""识别""建立"）
- 贴合{level}管理者的实际工作场景
- qc_pass为true表示通过质检，false表示有问题；qc_issues列出具体问题
"""

ANCHOR_PROMPT = """基于以下领导力维度和定位描述，为每个维度生成BARS行为锚定（优秀/达标/不达标三档）。

维度信息：{dimensions_with_descriptions_json}

企业背景：{company_info}
目标层级：{level}

输出严格按JSON格式（不要markdown标记）：
{{
  "anchors": [
    {{
      "dimension_id": "D1",
      "dimension_name": "维度名",
      "excellent": ["优秀行为1"],
      "standard": ["达标行为1", "达标行为2"],
      "below": ["不达标行为1", "不达标行为2"]
    }}
  ]
}}

要求：
- 每个维度：优秀1条、达标2条、不达标2条
- 所有行为以动词开头，描述具体可观察
- 优秀行为体现引领性和突破性
- 达标行为体现稳定输出和规范执行
- 不达标行为体现常见差距和典型问题
- 三档之间形成清晰的行为递进
"""

REGENERATE_PROMPT = """基于以下方向和反馈，重新生成一条内容。

原始内容：{original}
修改方向：{direction}
类型：{item_type}（维度定义/定位描述/行为锚定）

输出严格按JSON格式：
{{
  "result": "重新生成的内容..."
}}
"""


# ── Core Functions ─────────────────────────────────────────────

def _call_deepseek(system_prompt: str, user_prompt: str, max_tokens: int = 2000, use_reasoner: bool = False) -> str:
    """通用 DeepSeek API 调用"""
    model = DEEPSEEK_REASONER_MODEL if use_reasoner else DEEPSEEK_CHAT_MODEL
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content or ""


def chat(messages: list[dict], context: str = "") -> str:
    """Step1 引导式对话"""
    user_context = f"\n\n当前已收集的企业信息：{context}" if context else ""
    conversation = "\n".join(
        f"{'AI' if m['role'] == 'assistant' else '用户'}：{m['content']}"
        for m in messages[-6:]  # 最近6轮
    )
    user_prompt = f"""你正在进行领导力建模的信息采集对话。通过6轮对话收集：行业/业务、规模/阶段、战略重点、管理痛点、建模层级、优秀管理者画像。

当前对话记录：
{conversation}{user_context}

请根据对话进度自然地回复用户，引导完成信息采集。如果已收集足够信息（6项），在回复末尾附上摘要，格式：
【摘要】
行业/业务：xxx
规模/阶段：xxx
战略重点：xxx
管理痛点：xxx
建模层级：xxx
优秀画像：xxx"""
    return _call_deepseek(SYSTEM_PROMPT, user_prompt, max_tokens=1000)


def analyze_document(text: str, filename: str) -> str:
    """文档分析"""
    user_prompt = f"请分析以下文档，提取与领导力建模相关的核心信息。\n文件名：{filename}\n\n文档内容：\n{text[:8000]}"
    return _call_deepseek(DOC_ANALYSIS_SYS, user_prompt, max_tokens=1000)


def generate_dimensions(company_info: str, level: str = "中层管理者") -> str:
    """Step2 生成维度"""
    user_prompt = DIMENSION_PROMPT.format(level=level, company_info=company_info)
    return _call_deepseek(SYSTEM_PROMPT, user_prompt, max_tokens=2000)


def generate_descriptions(dimensions_json: str, company_info: str, level: str = "中层管理者") -> str:
    """Step3 生成维度描述"""
    user_prompt = DESCRIPTION_PROMPT.format(
        level=level,
        dimensions_json=dimensions_json,
        company_info=company_info,
    )
    return _call_deepseek(SYSTEM_PROMPT, user_prompt, max_tokens=3000)


def generate_anchors(dimensions_with_descriptions_json: str, company_info: str, level: str = "中层管理者") -> str:
    """Step4 生成行为锚定"""
    user_prompt = ANCHOR_PROMPT.format(
        dimensions_with_descriptions_json=dimensions_with_descriptions_json,
        company_info=company_info,
        level=level,
    )
    return _call_deepseek(SYSTEM_PROMPT, user_prompt, max_tokens=4000, use_reasoner=True)


def regenerate(original: str, direction: str, item_type: str) -> str:
    """重新生成某条内容"""
    user_prompt = REGENERATE_PROMPT.format(
        original=original,
        direction=direction,
        item_type=item_type,
    )
    return _call_deepseek(SYSTEM_PROMPT, user_prompt, max_tokens=1000)
