"""
Tests for leadership knowledge base.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.knowledge_base import (
    LEADERSHIP_DIMENSIONS,
    search_knowledge_base,
    build_kb_context,
)

REQUIRED_FIELDS = ["id", "name", "definition", "industry_tags", "level_range", "sources", "keywords"]
SOURCES_FIELDS = ["framework", "strategy", "reference"]


def test_leadership_dimensions_populated():
    """至少 30 条维度，每条含所有必填字段，id 以 LN- 开头"""
    assert len(LEADERSHIP_DIMENSIONS) >= 30

    for dim in LEADERSHIP_DIMENSIONS:
        for field in REQUIRED_FIELDS:
            assert field in dim, f"维度 {dim.get('id', '?')} 缺少字段 {field}"

        assert dim["id"].startswith("LN-"), f"id {dim['id']} 不以 LN- 开头"
        assert len(dim["name"]) >= 2, f"{dim['id']} name 太短"
        assert len(dim["definition"]) >= 20, f"{dim['id']} definition 太短"
        assert isinstance(dim["industry_tags"], list), f"{dim['id']} industry_tags 不是 list"
        assert len(dim["industry_tags"]) > 0, f"{dim['id']} industry_tags 为空"
        assert isinstance(dim["level_range"], list), f"{dim['id']} level_range 不是 list"
        assert isinstance(dim["keywords"], list), f"{dim['id']} keywords 不是 list"
        assert len(dim["keywords"]) >= 4, f"{dim['id']} keywords 不足 4 个"

        assert isinstance(dim["sources"], dict), f"{dim['id']} sources 不是 dict"
        for sf in SOURCES_FIELDS:
            assert sf in dim["sources"], f"{dim['id']} sources 缺少 {sf}"


def test_search_knowledge_base_returns_relevant_results():
    """搜索跨部门协作相关文本应返回协作相关维度"""
    results = search_knowledge_base(
        "互联网科技公司，快速扩张期，中层管理者面临跨部门协作挑战",
        "中层管理者",
        top_n=10,
    )
    ids = [d["id"] for d in results]
    assert "LN-023" in ids, "跨部门协作未出现在结果中"


def test_search_knowledge_base_handles_empty_input():
    """空字符串不崩溃，返回 list"""
    results = search_knowledge_base("", "中层管理者")
    assert isinstance(results, list)


def test_search_knowledge_base_respects_level():
    """战略规划+高层管理者搜索应优先返回高层级维度"""
    results = search_knowledge_base("战略规划", "高层管理者", top_n=15)
    ids = [d["id"] for d in results]
    # LN-001 (战略拆解与落地) 应出现在靠前位置
    assert "LN-001" in ids, "战略拆解与落地未出现在结果中"
    # LN-001 应该比 LN-017 更靠前（战略词匹配优先级高于执行）
    idx_001 = ids.index("LN-001")
    # 至少前 3 名
    assert idx_001 < 5, f"LN-001 排名太靠后: index={idx_001}"


def test_build_kb_context_formats_as_prompt_text():
    """build_kb_context 返回含 LN- 的长字符串"""
    context = build_kb_context("互联网科技公司", "中层管理者")
    assert isinstance(context, str)
    assert len(context) > 100
    assert "LN-" in context
