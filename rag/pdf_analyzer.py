from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass
class PDFProfile:
    """
    PDF 类型检测结果。
    """

    file_path: str
    page_count: int
    total_text_chars: int
    avg_chars_per_page: float
    empty_page_count: int
    is_scanned_like: bool
    is_text_pdf: bool
    has_checklist_like_content: bool
    parse_suggestion: str


def analyze_pdf(file_path: str) -> PDFProfile:
    """
    分析 PDF 类型。

    目标：
    1. 判断是否能提取文本；
    2. 判断是否像扫描版；
    3. 判断是否包含 checklist / template 类内容；
    4. 给出推荐解析策略。
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    total_chars = 0
    empty_pages = 0
    checklist_hits = 0

    checklist_keywords = [
        "checklist",
        "neurips paper checklist",
        "limitations",
        "claims",
        "experimental reproducibility",
        "dataset and benchmark",
        "[todo]",
    ]

    with fitz.open(path) as pdf:
        page_count = pdf.page_count

        for page_index in range(page_count):
            page = pdf.load_page(page_index)
            text = page.get_text().strip() # type: ignore
            text_lower = text.lower()

            if not text:
                empty_pages += 1
            else:
                total_chars += len(text)

            if any(keyword in text_lower for keyword in checklist_keywords):
                checklist_hits += 1

    avg_chars = total_chars / page_count if page_count else 0

    is_scanned_like = page_count > 0 and avg_chars < 50
    is_text_pdf = total_chars > 0 and not is_scanned_like
    has_checklist_like_content = checklist_hits > 0

    if is_scanned_like:
        suggestion = "ocr_required"
    elif has_checklist_like_content:
        suggestion = "structured_parse_and_filter_checklist"
    elif page_count >= 6:
        suggestion = "structured_parse_recommended"
    else:
        suggestion = "simple_text_parse_ok"

    return PDFProfile(
        file_path=str(path),
        page_count=page_count,
        total_text_chars=total_chars,
        avg_chars_per_page=avg_chars,
        empty_page_count=empty_pages,
        is_scanned_like=is_scanned_like,
        is_text_pdf=is_text_pdf,
        has_checklist_like_content=has_checklist_like_content,
        parse_suggestion=suggestion,
    )