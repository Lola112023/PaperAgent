from rag.loader import DocumentChunk


CHECKLIST_KEYWORDS = [
    "neurips paper checklist",
    "paper checklist",
    "does the paper",
    "claims",
    "limitations",
    "experimental reproducibility",
    "dataset and benchmark",
    "[todo]",
]

REFERENCE_KEYWORDS = [
    "references",
    "bibliography",
]


def detect_block_type(text: str) -> str:
    """
    粗略判断文本块类型。
    """

    lower = text.lower()

    if any(keyword in lower for keyword in CHECKLIST_KEYWORDS):
        return "checklist"

    # References 不建议只凭一个词判断，否则容易误伤正文。
    if lower.strip().startswith("references") or lower.strip().startswith("bibliography"):
        return "reference"

    return "content"


def filter_chunks_for_paper_body(
    chunks: list[DocumentChunk],
    remove_checklist: bool = True,
    remove_references: bool = True,
) -> list[DocumentChunk]:
    """
    过滤掉 checklist / references 等不适合论文主体分析的内容。
    """

    filtered = []

    for chunk in chunks:
        block_type = chunk.block_type

        if block_type == "page_text":
            block_type = detect_block_type(chunk.text)

        if remove_checklist and block_type == "checklist":
            continue

        if remove_references and block_type == "reference":
            continue

        chunk.block_type = block_type
        filtered.append(chunk)

    return filtered