from dataclasses import dataclass

from rag.loader import DocumentChunk
import re


SECTION_PATTERNS = [
    r"^\s*abstract\s*$",
    r"^\s*introduction\s*$",
    r"^\s*related work\s*$",
    r"^\s*method\s*$",
    r"^\s*methodology\s*$",
    r"^\s*approach\s*$",
    r"^\s*experiments?\s*$",
    r"^\s*evaluation\s*$",
    r"^\s*results?\s*$",
    r"^\s*discussion\s*$",
    r"^\s*limitations?\s*$",
    r"^\s*conclusion\s*$",
    r"^\s*references\s*$",
    r"^\s*\d+\.?\s+.+$",
]


def guess_section_title(line: str) -> str | None:
    """
    简单判断某一行是否像章节标题。
    """

    stripped = line.strip()

    if not stripped:
        return None

    lower = stripped.lower()

    for pattern in SECTION_PATTERNS:
        if re.match(pattern, lower):
            return stripped

    # 很短、首字母大写、没有句号，也可能是标题
    if len(stripped) <= 80 and "." not in stripped[-3:]:
        words = stripped.split()
        if 1 <= len(words) <= 10 and stripped[0].isupper():
            return stripped

    return None

@dataclass
class TextChunk:
    text: str
    source: str
    page: int | None
    chunk_id: int
    section_title: str | None = None
    block_type: str = "content"


def split_documents(
    documents: list[DocumentChunk],
    chunk_size: int = 800,
    overlap: int = 100,
) -> list[TextChunk]:
    """
    将文档内容切分成多个 TextChunk。

    参数：
        documents: loader.py 返回的 DocumentChunk 列表
        chunk_size: 每个 chunk 最大字符数
        overlap: 相邻 chunk 的重叠字符数

    返回：
        list[TextChunk]
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0。")

    if overlap < 0:
        raise ValueError("overlap 不能小于 0。")

    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size。")

    chunks: list[TextChunk] = []
    chunk_id = 0

    current_section = None

    for document in documents:
        text = _normalize_text(document.text)

        for line in text.splitlines():
            guessed = guess_section_title(line)
            if guessed:
                current_section = guessed
                break

        pieces = split_text(text, chunk_size=chunk_size, overlap=overlap)

        for piece in pieces:
            chunks.append(
                TextChunk(
                    text=piece,
                    source=document.source,
                    page=document.page,
                    chunk_id=chunk_id,
                    section_title=document.section_title or current_section,
                    block_type=document.block_type,
                )
            )
            chunk_id += 1

    return chunks
# 如果没有 overlap，前后可能被切开。保留重叠可以缓解这个问题。

def split_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100,
) -> list[str]:
    """
    将单段文本切成多个字符串 chunk。
    """

    text = _normalize_text(text)#简单的清洗文本，去除首尾换行之类的

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


def _normalize_text(text: str) -> str:
    """
    简单清洗文本。

    作用：
    1. 去掉多余空白；
    2. 保留基本段落结构；
    3. 避免连续空格过多。
    """

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)