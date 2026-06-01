from rag.retriever import retrieve


def search_index(query: str, top_k: int = 5) -> str:
    """
    从本地向量库中检索相关文本片段。
    """

    try:
        results = retrieve(query, top_k=top_k)

        if not results:
            return "没有检索到相关内容。"

        lines = []

        for index, item in enumerate(results, start=1):
            page_text = f"第 {item.page} 页" if item.page is not None else "无页码"
            preview = item.text[:500]

            lines.append(
                f"结果 {index}\n"
                f"来源：{item.source}\n"
                f"页码：{page_text}\n"
                f"chunk_id：{item.chunk_id}\n"
                f"相似度：{item.score:.4f}\n"
                f"内容预览：\n{preview}\n"
            )

        return ("\n" + "-" * 60 + "\n").join(lines)

    except Exception as e:
        return f"检索失败：{e}"