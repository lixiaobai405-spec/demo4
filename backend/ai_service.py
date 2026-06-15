"""
AI Service — DeepSeek API 封装，借鉴 demo2 的 prompt 工程和 JSON 提取逻辑
"""
import json
import re
from openai import OpenAI
from backend.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_CHAT_MODEL,
    DEEPSEEK_REASONER_MODEL,
    LLM_TIMEOUT,
)

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL, timeout=LLM_TIMEOUT)

# ── System Prompts（借鉴 demo2 leadership_prompts.py 的精华） ──

SYSTEM_PROMPT = """你是资深领导力建模顾问，服务于中国科技企业。
你的专业领域：胜任力模型构建、BARS行为锚定、领导力发展体系设计。

全局规则：
1. 本次建模只服务一个单一层级/群体，不生成多层级矩阵
2. 信息采集按行业/规模/战略/痛点/目标层级/优秀管理者画像归纳，信息不足时直接指出缺口
3. 维度必须生成4-8个推荐维度+若干备选维度
4. 每个维度包含id、name、definition、sources、priority、rationale
5. 描述聚焦目标层级，长度50-120字
6. 禁用空泛词：积极、主动、高度、认真、负责、努力、认可、重视、关注、善于、较强、具备、出色、优秀、良好
7. 行为锚定必须输出优秀/达标/不达标三档
8. 每条行为以行为动词开头，可观察、可衡量
9. 信息缺失时直接指出，不虚构
10. 只输出JSON，不输出Markdown"""

CHAT_SYSTEM_PROMPT = """你是资深领导力建模顾问，正在通过自然对话采集企业信息。
你需要像一位专业顾问一样与用户自然交流，逐步收集信息。

需要收集的6项信息：
1. 行业/业务类型
2. 企业规模/发展阶段
3. 当前战略重点
4. 主要管理痛点
5. 目标建模层级（基层/中层/高层）
6. 优秀管理者具体行为画像

对话规则：
- 用自然友好的中文对话，不要输出JSON或结构化数据
- 每次只问1-2个问题，不要一次列出所有问题
- 根据用户回答灵活调整下一个问题
- 当收集到足够信息后，在回复末尾用【摘要】格式汇总
- 摘要格式：每行"字段名：内容"
- 如果用户已经提供了多项信息，先确认再追问缺失项"""

DOC_ANALYSIS_SYS = """你是领导力建模顾问，从企业文档中提取建模相关信息。
严格按以下格式输出：

【战略关键词】：3-8个战略方向关键词（逗号分隔）
【高绩效行为特征】：2-4条高绩效管理者典型行为描述
【能力要求关键词】：文档中出现的管理者能力要求关键词（逗号分隔）
【建模参考重点】：1-2条最值得纳入领导力模型的核心洞察

用中文回答，每项不超过150字。文档内容不足时如实说明。"""

# ── JSON 提取（借鉴 demo2 leadership_llm.py） ──

class LLMError(Exception):
    pass


def _extract_json(content: str) -> dict:
    """健壮的JSON提取：先直接解析，再去fence，再regex"""
    content = (content or "").strip()
    # 1. 直接解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    # 2. 去 markdown fence
    without_fence = content.strip("`")
    if without_fence.lower().startswith("json"):
        without_fence = without_fence[4:].strip()
        try:
            return json.loads(without_fence)
        except json.JSONDecodeError:
            pass
    # 3. Regex 提取第一个 JSON 对象
    match = re.search(r"\{.*\}", content, re.S)
    if not match:
        raise LLMError("AI 输出不包含 JSON")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise LLMError(f"AI JSON 解析失败: {exc}")


# ── Core Functions ─────────────────────────────────────────────

def _call_deepseek(system: str, user: str, max_tokens: int = 2000, use_reasoner: bool = False) -> str:
    model = DEEPSEEK_REASONER_MODEL if use_reasoner else DEEPSEEK_CHAT_MODEL
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def chat(messages: list[dict], context: str = "") -> str:
    """Step1: 引导式对话，采集企业背景信息"""
    user_context = f"\n\n已收集的企业信息：{context}" if context else ""
    conversation = "\n".join(
        f"{'AI' if m['role'] == 'assistant' else '用户'}：{m['content']}"
        for m in messages[-6:]
    )
    user_prompt = f"""正在进行领导力建模信息采集。需收集6项：行业/业务、规模/阶段、战略重点、管理痛点、建模层级、优秀管理者画像。

对话记录：
{conversation}{user_context}

请根据进度自然地回复用户，引导完成信息采集。当收集到足够信息时，在末尾附上摘要：
【摘要】
行业/业务：xxx
规模/阶段：xxx
战略重点：xxx
管理痛点：xxx
建模层级：xxx
优秀画像：xxx"""
    return _call_deepseek(CHAT_SYSTEM_PROMPT, user_prompt, max_tokens=1000)


def analyze_document(text: str, filename: str) -> str:
    """Step1: 文档分析"""
    user_prompt = f"分析以下文档，提取与领导力建模相关的核心信息。\n文件名：{filename}\n\n文档内容：\n{text[:8000]}"
    return _call_deepseek(DOC_ANALYSIS_SYS, user_prompt, max_tokens=1000)


def generate_dimensions(company_info: str, level: str = "中层管理者") -> dict:
    """Step2: 生成维度 → 返回结构化 dict"""
    prompt = f"""根据以下企业信息，为{level}生成推荐维度和备选维度。
企业背景：{company_info}

输出 JSON：
{{"recommended":[{{"id":"D1","name":"2-5字","definition":"2-3句定义","sources":{{"strategy":"战略来源","framework":"框架来源","interview":"访谈来源"}},"priority":"core|important|supplementary","rationale":"1句理由"}}],"alternatives":[]}}

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

    return {
        "recommended": [
            {
                "id": d.get("id", f"D{i+1}"),
                "name": d.get("name", ""),
                "definition": d.get("definition", ""),
                "sources": d.get("sources", {}),
                "priority": d.get("priority", "important"),
                "rationale": d.get("rationale", ""),
            }
            for i, d in enumerate(recommended)
        ],
        "alternatives": [
            {
                "id": d.get("id", f"DA{i+1}"),
                "name": d.get("name", ""),
                "definition": d.get("definition", ""),
                "priority": d.get("priority", "supplementary"),
            }
            for i, d in enumerate(alternatives)
        ],
    }


def generate_descriptions(dimensions: list, company_info: str, level: str = "中层管理者") -> list:
    """Step3: 生成维度描述 → 返回 list"""
    dims_json = json.dumps(dimensions, ensure_ascii=False)
    prompt = f"""为{level}的每个维度生成定位描述。

维度列表：{dims_json}
企业背景：{company_info}

输出 JSON：
{{"descriptions":[{{"dimension_id":"D1","dimension_name":"维度名","description":"50-120字","quality_check":{{"passed":true,"issues":[]}}}}]}}

要求：
- 每个描述50-120字，聚焦{level}的实际工作场景
- 使用可观察的行为动词（制定、推动、识别、建立、拆解、复盘等）
- 严格禁止空泛词：主动、积极、高度、认真、负责、努力、认可、重视、关注、善于、较强、具备、出色、优秀、良好
- quality_check.passed 为 true 表示通过质检"""
    result = _call_deepseek(SYSTEM_PROMPT, prompt, max_tokens=3000)
    payload = _extract_json(result)
    items = payload.get("descriptions") or []
    return [
        {
            "dimension_id": d.get("dimension_id", ""),
            "dimension_name": d.get("dimension_name", ""),
            "description": d.get("description", ""),
            "quality_check": d.get("quality_check", {"passed": True, "issues": []}),
        }
        for d in items
    ]


def generate_anchors(dimensions: list, company_info: str, level: str = "中层管理者") -> list:
    """Step4: 生成BARS行为锚定 → 返回 list"""
    dims_json = json.dumps(dimensions, ensure_ascii=False)
    prompt = f"""为每个维度生成 BARS 行为锚定（优秀/达标/不达标三档）。

维度信息：{dims_json}
企业背景：{company_info}
目标层级：{level}

输出 JSON：
{{"anchors":[{{"dimension_id":"D1","dimension_name":"维度名","anchors":{{"excellent":[{{"id":"D1-E1","text":"优秀行为","level":"excellent"}}],"standard":[{{"id":"D1-S1","text":"达标行为","level":"standard"}}],"below":[{{"id":"D1-B1","text":"不达标行为","level":"below"}}]}}}}]}}

要求：
- 每个维度：优秀1条、达标2条、不达标2条
- 所有行为以动词开头，具体可观察
- 严格禁止空泛词：主动、积极、高度、认真、负责、努力、认可、重视、关注、善于、较强、具备、出色、优秀、良好
- 三档形成清晰的行为递进"""
    result = _call_deepseek(SYSTEM_PROMPT, prompt, max_tokens=4000, use_reasoner=True)
    payload = _extract_json(result)
    return payload.get("anchors") or []


def regenerate_item(original: str, direction: str, item_type: str) -> str:
    """重新生成某条内容"""
    prompt = f"""根据指定方向重新生成内容。

原始内容：{original}
修改方向：{direction}
类型：{item_type}

输出 JSON：
{{"result":"新内容..."}}"""
    result = _call_deepseek(SYSTEM_PROMPT, prompt, max_tokens=1000)
    payload = _extract_json(result)
    return payload.get("result", result)


# ═══════════════════════════════════════════════════════════
#  质量审计 + 残差式定向修复
# ═══════════════════════════════════════════════════════════

BANNED_WORDS = [
    "主动", "积极", "高度", "认真", "负责",
    "努力", "认可", "重视", "关注", "善于",
    "较强", "具备", "出色", "优秀", "良好",
]

# 复合词白名单：包含禁用词但不是空泛用法
BANNED_WHITELIST = ["负责人", "优秀水平", "优秀行为", "高度重视"]  # 作为职位/标题使用


def audit_text(text: str, context: str = "") -> list[str]:
    """审计单段文本，返回问题列表（空列表=通过）"""
    issues = []
    # 1. 禁用词检查
    for word in BANNED_WORDS:
        if word in text:
            # 检查是否在白名单复合词中
            whitelisted = any(wl in text and word in wl for wl in BANNED_WHITELIST)
            if not whitelisted:
                # 需要确认不是复合词的一部分
                # 若 word="负责"且"负责人"在text中，则不算违规
                if word == "负责" and "负责人" in text:
                    continue
                if word == "优秀" and ("优秀水平" in text or "优秀行为" in text):
                    continue
                issues.append(f"包含禁用词「{word}」，请替换为具体的行为描述")
    # 2. 行为动词检查（仅对行为锚定文本）
    if context == "anchor":
        first_char = text.strip()[0] if text.strip() else ""
        weak_starts = {"在", "为", "与", "和", "对", "从", "以", "通", "按", "凭", "通", "将"}
        if first_char in weak_starts:
            issues.append(f"行为应以强动词开头，当前以「{first_char}」开头")
    # 3. 长度检查
    if context == "description":
        ln = len(text)
        if ln < 50:
            issues.append(f"描述过短({ln}字)，需≥50字")
        elif ln > 120:
            issues.append(f"描述过长({ln}字)，需≤120字")
    return issues


def retry_item_with_feedback(
    item_type: str,
    original: str,
    issues: list[str],
    dimension_name: str = "",
    max_retries: int = 2,
) -> str:
    """残差式修复：仅针对具体问题重新生成，保留原始内容框架"""
    if not issues:
        return original

    feedback = "\n".join(f"- {issue}" for issue in issues)
    prompt = f"""修复以下{ item_type }中的质量问题，保留原始内容的优点和框架，仅修改有问题的部分。

维度：{dimension_name}
原始内容：{original}

需要修复的问题：
{feedback}

修复规则：
1. 禁用词替换：用具体可观察的动词/描述替代空泛词
   - "主动"→"牵头/发起/率先"
   - "积极"→删除或用"推动/促成"
   - "负责"→"承担/主导/管理"（注意："负责人"作为职位名可使用）
   - "优秀/良好"→具体描述好在哪
   - "高度重视"→"优先保障/投入额外资源"
2. 行为以强动词开头（制定/推动/识别/建立/拆解/复盘/组织/协调/设定/追踪）
3. 保持长度在合理范围

只输出修复后的完整内容，不要输出解释或JSON包装。"""
    for attempt in range(max_retries):
        result = _call_deepseek(SYSTEM_PROMPT, prompt, max_tokens=800)
        # 清理可能的JSON包装
        result = result.strip().strip('"').strip("'")
        try:
            parsed = json.loads(result)
            if isinstance(parsed, dict) and "result" in parsed:
                result = parsed["result"]
        except (json.JSONDecodeError, TypeError):
            pass
        # 验证修复效果
        remaining = audit_text(result, "description" if item_type == "定位描述" else "anchor")
        if not remaining:
            return result
        if attempt < max_retries - 1:
            # 还有重试机会，追加反馈
            feedback += "\n" + "\n".join(f"- [仍存在] {r}" for r in remaining)
    # 所有重试都失败，返回原始内容（标记问题）
    return original


def generate_with_audit(
    generate_fn,
    audit_context: str,
    *args,
    max_total_retries: int = 2,
    **kwargs,
):
    """
    生成+审计+残差修复的通用包装器。

    generate_fn: 生成函数
    audit_context: "dimension" | "description" | "anchor"
    返回: (result, audit_report)
    """
    result = generate_fn(*args, **kwargs)
    report = {"total": 0, "passed": 0, "fixed": 0, "failed": 0, "details": []}

    items = []
    if isinstance(result, dict) and "recommended" in result:
        # dimensions result
        all_items = result.get("recommended", []) + result.get("alternatives", [])
        items = all_items
        for item in all_items:
            report["total"] += 1
            text = item.get("definition", "")
            issues = audit_text(text, "dimension")
            name = item.get("name", "")
            detail = {"name": name, "issues": issues, "fixed": False}
            if issues:
                new_def = retry_item_with_feedback(
                    "维度定义", text, issues, name, max_retries=max_total_retries
                )
                if new_def != text and not audit_text(new_def, "dimension"):
                    item["definition"] = new_def
                    detail["fixed"] = True
                    report["fixed"] += 1
                else:
                    report["failed"] += 1
            else:
                report["passed"] += 1
            report["details"].append(detail)

    elif isinstance(result, list):
        # descriptions or anchors list
        items = result
        for item in items:
            report["total"] += 1
            if audit_context == "description":
                text = item.get("description", "")
                name = item.get("dimension_name", "")
            else:
                # anchor - audit all behavior texts
                name = item.get("dimension_name", "")
                anc = item.get("anchors", {})
                all_texts = []
                for level in ["excellent", "standard", "below"]:
                    for b in anc.get(level, []):
                        all_texts.append(b.get("text", "") if isinstance(b, dict) else str(b))
                text = " ".join(all_texts)

            issues = audit_text(text, audit_context)
            detail = {"name": name, "issues": issues, "fixed": False}

            if issues and audit_context == "description":
                new_desc = retry_item_with_feedback(
                    "定位描述", text, issues, name, max_retries=max_total_retries
                )
                if new_desc != text and not audit_text(new_desc, "description"):
                    item["description"] = new_desc
                    item["quality_check"] = {"passed": True, "issues": []}
                    detail["fixed"] = True
                    report["fixed"] += 1
                else:
                    item["quality_check"] = {"passed": False, "issues": issues}
                    report["failed"] += 1
            elif issues and audit_context == "anchor":
                # 对每条行为单独修复
                anc = item.get("anchors", {})
                fixed_any = False
                for level in ["excellent", "standard", "below"]:
                    for b in anc.get(level, []):
                        if isinstance(b, dict):
                            bt = b.get("text", "")
                            bt_issues = audit_text(bt, "anchor")
                            if bt_issues:
                                new_bt = retry_item_with_feedback(
                                    "行为描述", bt, bt_issues, name, max_retries=max_total_retries
                                )
                                if new_bt != bt and not audit_text(new_bt, "anchor"):
                                    b["text"] = new_bt
                                    fixed_any = True
                if fixed_any:
                    detail["fixed"] = True
                    report["fixed"] += 1
                else:
                    report["failed"] += 1
            else:
                report["passed"] += 1
            report["details"].append(detail)

    return result, report
