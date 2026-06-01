from rag.loader import load_document
from rag.chunker import split_documents


def chunk_document_preview(
    file_path: str,
    chunk_size: int = 800,
    overlap: int = 100,
) -> str:
    """
    加载文档并切分，返回 chunk 预览信息。
    """

    try:
        documents = load_document(file_path)
        chunks = split_documents(
            documents,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        if not chunks:
            return "文档切分完成，但没有得到有效 chunk。"

        preview = chunks[0].text[:500]

        return (
            f"文档切分成功。\n"
            f"原始片段数量：{len(documents)}\n"
            f"切分后 chunk 数量：{len(chunks)}\n"
            f"第一个 chunk 来源：{chunks[0].source}\n"
            f"第一个 chunk 页码：{chunks[0].page}\n"
            f"第一个 chunk ID：{chunks[0].chunk_id}\n\n"
            f"第一个 chunk 预览：\n{preview}"
        )

    except Exception as e:
        return f"文档切分失败：{e}"