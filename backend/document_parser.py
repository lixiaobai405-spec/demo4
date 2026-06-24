"""
Helpers for extracting text from uploaded reference documents.
"""
from io import BytesIO

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - runtime dependency check
    PdfReader = None

try:
    from docx import Document
except ImportError:  # pragma: no cover - runtime dependency check
    Document = None


class DocumentParseError(ValueError):
    """Raised when an uploaded document cannot be parsed."""


def extract_document_text(content: bytes, filename: str) -> str:
    """Extract normalized text from supported upload formats."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext in ("txt", "md"):
        return _extract_text_file(content)
    if ext == "pdf":
        return _extract_pdf_text(content)
    if ext == "docx":
        return _extract_docx_text(content)
    if ext == "doc":
        raise DocumentParseError("暂不支持老式 .doc 文件，请先另存为 Word .docx 后再上传")

    raise DocumentParseError(f"不支持的文件类型: .{ext}")


def _extract_text_file(content: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return _normalize_text(content.decode(encoding), "TXT")
        except UnicodeDecodeError:
            continue
    raise DocumentParseError("文本文件编码无法识别，请转为 UTF-8 后重试")


def _extract_pdf_text(content: bytes) -> str:
    if PdfReader is None:
        raise DocumentParseError("服务器缺少 pypdf 依赖，暂时无法解析 PDF")

    reader = PdfReader(BytesIO(content))
    text = "\n".join((page.extract_text() or "").strip() for page in reader.pages)
    return _normalize_text(text, "PDF")


def _extract_docx_text(content: bytes) -> str:
    if Document is None:
        raise DocumentParseError("服务器缺少 python-docx 依赖，暂时无法解析 DOCX")

    doc = Document(BytesIO(content))
    parts = [paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip()]
    for table in getattr(doc, "tables", []):
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    text = "\n".join(parts)
    return _normalize_text(text, "DOCX")


def _normalize_text(text: str, file_type: str) -> str:
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        raise DocumentParseError(f"{file_type} 未提取到可用文本，请检查文件内容是否为扫描件或图片")
    return normalized
