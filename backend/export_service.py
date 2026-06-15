"""
导出服务 — DOCX（纯XML生成） + Markdown
借鉴 demo2 leadership_export.py
"""
import html
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


# ── Context normalization ─────────────────────────────────


def _norm(ctx):
    """标准化 context：兼容中英文key"""
    if not ctx:
        return {}
    c = dict(ctx)
    mapping = {
        "行业/业务": "industry", "规模/阶段": "scale",
        "战略重点": "strategy", "管理痛点": "pains",
        "建模层级": "target_group", "优秀画像": "profile",
    }
    for cn, en in mapping.items():
        if cn in c:
            c[en] = c[cn]
    return c


def _g(ctx, key, default=""):
    """安全获取，自动查中英文key"""
    if key in ctx:
        return str(ctx[key] or default)
    # Try Chinese alias
    alias = {
        "company_name": "行业/业务", "industry": "行业/业务",
        "target_group": "建模层级", "strategy": "战略重点",
        "pains": "管理痛点", "profile": "优秀画像",
        "scale": "规模/阶段",
    }
    cn = alias.get(key)
    if cn and cn in ctx:
        return str(ctx[cn] or default)
    return default


# ── Public API ────────────────────────────────────────────


def build_docx_bytes(model):
    """生成 DOCX 文件（纯 XML，不依赖 python-docx）"""
    paragraphs = _build_paragraphs(model)
    document_xml = _document_xml(paragraphs)
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _content_types_xml())
        zf.writestr("_rels/.rels", _rels_xml())
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/styles.xml", _styles_xml())
    return buffer.getvalue()


def build_markdown(model):
    """生成 Markdown 文本"""
    ctx = _norm(model.get("context") or {})
    dims = model.get("dimensions") or []
    descs = {d.get("id"): d for d in (model.get("descriptions") or [])}
    anchors = {a.get("dimension_id") or a.get("id"): a for a in (model.get("anchors") or [])}

    lines = [
        f"# {_g(ctx, 'industry', '企业')} {_g(ctx, 'target_group', '管理者')} 领导力模型",
        "",
        f"> 生成时间：{model.get('date', '')}",
        "",
        "## 模型概览",
        "",
        f"- 维度数量：{len(dims)}",
        f"- 行业：{_g(ctx, 'industry', '未提供')}",
        f"- 规模：{_g(ctx, 'scale', '未提供')}",
        f"- 战略重点：{_g(ctx, 'strategy', '未提供')}",
        f"- 建模层级：{_g(ctx, 'target_group', '未指定')}",
        "",
        "---",
        "",
    ]

    for i, dim in enumerate(dims, 1):
        dim_id = dim.get("id")
        desc = descs.get(dim_id, {})
        anc = anchors.get(dim_id, {})

        lines.append(f"## {i}. {dim.get('name', '未命名')}")
        lines.append("")
        if dim.get("definition"):
            lines.append(f"**定义**：{dim['definition']}")
            lines.append("")
        if desc.get("description"):
            lines.append(f"**定位描述**：{desc['description']}")
            lines.append("")

        anc_data = anc.get("anchors", {})
        for level_key, emoji_label in [
            ("excellent", "优秀水平"),
            ("standard", "达标水平"),
            ("below", "不达标"),
        ]:
            texts = _anchor_texts(anc_data, level_key)
            if texts:
                lines.append(f"### {emoji_label}")
                lines.append("")
                for t in texts:
                    lines.append(f"- {t}")
                lines.append("")

    return "\n".join(lines)


# ── Internal ──────────────────────────────────────────────


def _build_paragraphs(model):
    ctx = _norm(model.get("context") or {})
    dims = model.get("dimensions") or []
    descs = {d.get("id"): d for d in (model.get("descriptions") or [])}
    anchors = {a.get("dimension_id") or a.get("id"): a for a in (model.get("anchors") or [])}

    title = _g(ctx, "industry", "企业") + " " + _g(ctx, "target_group", "管理者") + " 领导力模型"
    paragraphs = [
        ("title", title),
        ("body", "版本：V1.0"),
        ("body", "适用对象：" + _g(ctx, "target_group", "--")),
        ("heading", "第一章 模型概述"),
        ("body", _bg_text(ctx)),
        ("heading", "第二章 维度详解"),
    ]

    for dim in dims:
        dim_id = dim.get("id")
        desc = descs.get(dim_id, {})
        anc = anchors.get(dim_id, {})
        anc_data = anc.get("anchors", {})

        paragraphs.append(("heading", dim_id + " " + (dim.get("name") or "未命名")))
        paragraphs.append(("body", "维度定义：" + (dim.get("definition") or "--")))
        paragraphs.append(("body", "定位描述：" + (desc.get("description") or "--")))
        paragraphs.append(("body", "优秀行为：" + "；".join(_anchor_texts(anc_data, "excellent") or ["--"])))
        paragraphs.append(("body", "达标行为：" + "；".join(_anchor_texts(anc_data, "standard") or ["--"])))
        paragraphs.append(("body", "不达标表现：" + "；".join(_anchor_texts(anc_data, "below") or ["--"])))

    paragraphs.append(("heading", "附录A 建模方法说明"))
    paragraphs.append(("body", "本模型采用 AI 辅助建模方式，融合企业背景、用户访谈与标准库参照形成。"))
    return paragraphs


def _bg_text(ctx):
    return (
        f"本模型聚焦{_g(ctx, 'target_group', '目标管理群体')}，"
        f"围绕{_g(ctx, 'strategy', '未提供战略')}等战略重点，"
        f"针对{_g(ctx, 'pains', '未提供痛点')}等管理挑战建立。"
        f"行业背景：{_g(ctx, 'industry', '未提供')}，规模：{_g(ctx, 'scale', '未提供')}。"
    )


def _anchor_texts(anchor_data, level):
    items = anchor_data.get(level) or []
    if not items:
        return None
    return [item.get("text") if isinstance(item, dict) else str(item) for item in items]


# ── DOCX XML Templates ────────────────────────────────────


def _document_xml(paragraphs):
    body = "".join(_para_xml(style, text) for style, text in paragraphs)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}"
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>'
        "</w:sectPr></w:body></w:document>"
    )


def _para_xml(style, text):
    style_id = {"title": "Title", "heading": "Heading1"}.get(style)
    ppr = f'<w:pPr><w:pStyle w:val="{style_id}"/></w:pPr>' if style_id else ""
    return f"<w:p>{ppr}<w:r><w:t>{html.escape(str(text))}</w:t></w:r></w:p>"


def _content_types_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        "</Types>"
    )


def _rels_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )


def _styles_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="40"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:b/><w:sz w:val="30"/></w:rPr></w:style>'
        "</w:styles>"
    )
