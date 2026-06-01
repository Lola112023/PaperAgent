from rag.loader import load_document


def load_document_preview(file_path: str) -> str:
    """
    加载文档，并返回简单预览信息。
    """

    try:
        chunks = load_document(file_path)

        if not chunks:
            return "文档加载成功，但没有提取到文本内容。"

        total_chars = sum(len(chunk.text) for chunk in chunks)
        preview = chunks[0].text[:500]

        page_info = ""
        if chunks[0].page is not None:
            page_info = f"第一页页码：{chunks[0].page}\n"

        return (
            f"文档加载成功。\n"
            f"片段数量：{len(chunks)}\n"
            f"总字符数：{total_chars}\n"
            f"{page_info}"
            f"\n内容预览：\n{preview}"
        )

    except Exception as e:
        return f"文档加载失败：{e}"