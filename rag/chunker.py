import re
from dataclasses import dataclass

from rag.loader import DocumentChunk


@dataclass
class TextChunk:
    text: str
    source: str
    page: int | None
    chunk_id: int
    section_title: str | None = None
    block_type: str = "content"


@dataclass
class SectionBlock:
    title: str | None
    text: str
    source: str
    page: int | None
    block_type: str = "content"


SECTION_PATTERNS = [
    r"^abstract$",
    r"^introduction$",
    r"^related work$",
    r"^background$",
    r"^method$",
    r"^methods$",
    r"^methodology$",
    r"^approach$",
    r"^model$",
    r"^experiments?$",
    r"^experimental setup$",
    r"^evaluation$",
    r"^results?$",
    r"^discussion$",
    r"^limitations?$",
    r"^conclusion$",
    r"^conclusions$",
    r"^references$",
    r"^\d+\.?\s+[A-Z][A-Za-z0-9 ,:;()/-]{2,}$",
    r"^[IVX]+\.?\s+[A-Z][A-Za-z0-9 ,:;()/-]{2,}$",
]


def split_documents(
    documents: list[DocumentChunk],
    chunk_size: int = 800,
    overlap: int = 100,
) -> list[TextChunk]:
    """
    将 DocumentChunk 切分成 TextChunk。

    切分策略：
    1. 先根据章节标题把文本聚合成 SectionBlock；
    2. 每个 SectionBlock 内部如果过长，再按照 chunk_size 切；
    3. 每个 chunk 保留 section_title、page、source、block_type 等 metadata。
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0。")

    if overlap < 0:
        raise ValueError("overlap 不能小于 0。")

    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size。")

    sections = build_sections(documents)

    chunks: list[TextChunk] = []
    chunk_id = 0

    for section in sections:
        pieces = split_text(
            section.text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for piece in pieces:
            chunks.append(
                TextChunk(
                    text=piece,
                    source=section.source,
                    page=section.page,
                    chunk_id=chunk_id,
                    section_title=section.title,
                    block_type=section.block_type,
                )
            )
            chunk_id += 1

    return chunks


def build_sections(documents: list[DocumentChunk]) -> list[SectionBlock]:
    """
    根据章节标题将文档内容聚合成 section。

    注意：
    - 这是轻量级规则，不是完美结构解析；
    - 对格式规范的论文有效；
    - 对复杂双栏 PDF、标题断行、扫描版 PDF 仍然有限。
    """

    sections: list[SectionBlock] = []

    current_title: str | None = None
    current_lines: list[str] = []
    current_source: str | None = None
    current_page: int | None = None
    current_block_type: str = "content"

    for document in documents:
        text = _normalize_text(document.text)

        if not text:
            continue

        source = document.source
        page = document.page
        block_type = getattr(document, "block_type", "content")
        document_section = getattr(document, "section_title", None)

        # 如果 loader 已经提供了 section_title，就优先使用
        if document_section and not current_title:
            current_title = document_section

        lines = text.splitlines()

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            guessed_title = guess_section_title(stripped)

            if guessed_title:
                # 遇到新标题，先保存旧 section
                if current_lines:
                    sections.append(
                        SectionBlock(
                            title=current_title,
                            text="\n".join(current_lines).strip(),
                            source=current_source or source,
                            page=current_page,
                            block_type=current_block_type,
                        )
                    )

                    current_lines = []

                current_title = guessed_title
                current_source = source
                current_page = page
                current_block_type = block_type
                continue

            current_lines.append(stripped)

            if current_source is None:
                current_source = source

            if current_page is None:
                current_page = page

            current_block_type = block_type

    if current_lines:
        sections.append(
            SectionBlock(
                title=current_title,
                text="\n".join(current_lines).strip(),
                source=current_source or "",
                page=current_page,
                block_type=current_block_type,
            )
        )

    return sections


def split_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100,
) -> list[str]:
    """
    对单个 section 内部做固定长度切分。

    这里仍然是按字符数切，但只在同一个 section 内部切，
    不会轻易把 Introduction 和 Method 混在同一个 chunk 里。
    """

    text = _normalize_text(text)

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def guess_section_title(line: str) -> str | None:
    """
    判断某一行是否像章节标题。
    """

    stripped = line.strip()

    if not stripped:
        return None

    normalized = re.sub(r"\s+", " ", stripped)
    lower = normalized.lower()

    # 去掉末尾冒号
    lower_no_colon = lower.rstrip(":")

    for pattern in SECTION_PATTERNS:
        if re.match(pattern, lower_no_colon):
            return normalized

    return None


def _normalize_text(text: str) -> str:
    """
    清洗文本：
    1. 去掉空行；
    2. 合并多余空白；
    3. 保留换行用于章节标题判断。
    """

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = re.sub(r"\s+", " ", line).strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)