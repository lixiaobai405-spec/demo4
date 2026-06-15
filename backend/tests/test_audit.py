"""
TDD tests for quality audit system
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.ai_service import audit_text, BANNED_WORDS


# ═══════════════════════════════════════════════════════════
# audit_text tests
# ═══════════════════════════════════════════════════════════

def test_audit_passes_clean_text():
    """干净文本（足够长度+无禁用词）通过审计"""
    # 50字以上
    text = "制定部门季度OKR，将战略目标拆解为月度任务清单与关键里程碑，明确每项任务的交付标准和完成时限，通过周度追踪机制确保执行进度可视化"
    issues = audit_text(text, "description")
    assert issues == []


def test_audit_detects_banned_word_active():
    """检测禁用词'主动'"""
    issues = audit_text("主动识别跨部门协作节点并建立沟通机制", "description")
    assert any("主动" in i for i in issues)


def test_audit_detects_banned_word_responsible():
    """检测禁用词'负责'（非'负责人'复合词）"""
    issues = audit_text("负责协调各部门资源并推动任务落实", "description")
    assert any("负责" in i for i in issues)


def test_audit_allows_fuzeren_as_title():
    """'负责人'作为职位名不触发审计"""
    issues = audit_text("明确每项任务的负责人与完成时限", "description")
    assert not any("负责" in i for i in issues)


def test_audit_allows_excellent_header():
    """'优秀水平'作为标题不触发审计"""
    issues = audit_text("在优秀水平上，管理者能超前完成目标", "anchor")
    assert not any("优秀" in i for i in issues)


def test_audit_detects_multiple_banned_words():
    """同时检测多个禁用词"""
    issues = audit_text("主动积极地推动跨部门协作，具备出色的沟通能力", "description")
    assert len(issues) >= 3  # 主动、积极、具备、出色


def test_audit_checks_description_length_too_short():
    """描述过短触发审计"""
    issues = audit_text("制定目标", "description")
    assert any("过短" in i for i in issues)


def test_audit_checks_description_length_too_long():
    """描述过长触发审计"""
    long_text = "这是一个" + "非常" * 80 + "长的描述文本"
    issues = audit_text(long_text, "description")
    assert any("过长" in i for i in issues)


def test_audit_checks_anchor_verb():
    """行为锚定以弱动词开头触发审计"""
    issues = audit_text("将任务分配给团队成员", "anchor")
    assert any("强动词" in i for i in issues)


def test_audit_anchor_with_strong_verb_passes():
    """强动词开头的锚定通过"""
    issues = audit_text("制定部门季度OKR并分配责任人", "anchor")
    assert not any("强动词" in i for i in issues)


def test_banned_words_list_is_nonempty():
    """禁用词列表至少10个"""
    assert len(BANNED_WORDS) >= 10


def test_all_banned_words_are_two_chars():
    """所有禁用词至少2个字符（避免误匹配）"""
    for word in BANNED_WORDS:
        assert len(word) >= 2, f"'{word}' too short, may cause false match"
