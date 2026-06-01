from dataclasses import dataclass

from rag.loader import DocumentChunk


@dataclass
class TextChunk:
    """
    文本切分后的片段。

    text: chunk 文本内容
    source: 来源文件路径
    page: 页码，如果不是 PDF，则为 None
    chunk_id: 当前 chunk 的编号
    """

    text: str
    source: str
    page: int | None
    chunk_id: int


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

    for document in documents:
        text = _normalize_text(document.text)

        if not text:
            continue

        pieces = split_text(text, chunk_size=chunk_size, overlap=overlap)

        for piece in pieces:
            chunks.append(
                TextChunk(
                    text=piece,
                    source=document.source,
                    page=document.page,
                    chunk_id=chunk_id,
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