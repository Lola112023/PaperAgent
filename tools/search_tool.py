from rag.retriever import retrieve


def search_index(query: str, top_k: int = 5) -> str:
    """
    从本地向量库中检索相关文本片段。

    返回格式尽量清晰，方便 LLM 基于检索结果回答。
    """

    try:
        top_k = int(top_k)
        results = retrieve(query, top_k=top_k)

        if not results:
            return "没有检索到相关内容。"

        lines = [
            f"检索问题：{query}",
            f"返回结果数量：{len(results)}",
            "",
        ]

        for index, item in enumerate(results, start=1):
            page_text = f"第 {item.page} 页" if item.page is not None else "无页码"

            lines.append(f"[检索结果 {index}]")
            lines.append(f"来源：{item.source}")
            lines.append(f"页码：{page_text}")
            lines.append(f"chunk_id：{item.chunk_id}")
            lines.append(f"相似度：{item.score:.4f}")
            lines.append("内容：")
            lines.append(item.text[:1200])
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"检索失败：{e}"