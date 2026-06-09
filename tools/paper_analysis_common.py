from rag.retriever import RetrievedChunk, retrieve


def _looks_like_checklist(text: str) -> bool:
    """
    判断文本是否像 NeurIPS / conference checklist。
    """

    checklist_keywords = [
        "neurips paper checklist",
        "paper checklist",
        "does the paper",
        "claims",
        "limitations",
        "experimental reproducibility",
        "dataset and benchmark",
        "code of ethics",
        "[todo]",
    ]

    hit_count = sum(1 for keyword in checklist_keywords if keyword in text)

    return hit_count >= 2


def _looks_like_reference(text: str) -> bool:
    """
    判断文本是否像 References / Bibliography。
    """

    stripped = text.strip().lower()

    if stripped.startswith("references") or stripped.startswith("bibliography"):
        return True

    # 粗略判断：如果一段里出现很多年份和作者引用形式，可能是参考文献
    year_like_count = sum(str(year) in stripped for year in range(1990, 2031))

    return year_like_count >= 5


def deduplicate_results(results: list[RetrievedChunk]) -> list[RetrievedChunk]:
    """
    按 chunk_id 去重，避免同一个 chunk 在多个 query 下重复出现。
    """

    seen: set[int] = set()
    unique_results: list[RetrievedChunk] = []

    for item in results:
        if item.chunk_id in seen:
            continue

        seen.add(item.chunk_id)
        unique_results.append(item)

    return unique_results


def format_retrieved_chunk(index: int, item: RetrievedChunk) -> str:
    """
    格式化检索结果，方便 LLM 阅读。
    """

    page_text = f"第 {item.page} 页" if item.page is not None else "无页码"
    section_title = getattr(item, "section_title", None) or "未知章节"
    block_type = getattr(item, "block_type", "content")

    return (
        f"\n[结果 {index}]\n"
        f"来源：{item.source}\n"
        f"页码：{page_text}\n"
        f"章节：{section_title}\n"
        f"类型：{block_type}\n"
        f"chunk_id：{item.chunk_id}\n"
        f"相似度：{item.score:.4f}\n"
        f"内容：\n{item.text[:1200]}\n"
    )

def filter_valid_results(results: list[RetrievedChunk]) -> list[RetrievedChunk]:
    """
    过滤不适合作为论文正文总结依据的检索结果。

    主要过滤：
    1. checklist
    2. reference
    3. 空内容
    4. 明显模板内容
    """

    valid_results: list[RetrievedChunk] = []

    for item in results:
        text = item.text.strip()
        lower_text = text.lower()

        if not text:
            continue

        block_type = getattr(item, "block_type", "content")

        if block_type in {"checklist", "reference"}:
            continue

        if _looks_like_checklist(lower_text):
            continue

        if _looks_like_reference(lower_text):
            continue

        valid_results.append(item)

    return valid_results

def collect_evidence(
    queries: list[str],
    top_k_per_query: int = 5,
    limit: int = 8,
) -> list[RetrievedChunk]:
    results: list[RetrievedChunk] = []

    for query in queries:
        results.extend(
            filter_valid_results(retrieve(query, top_k=top_k_per_query))
        )

    results = deduplicate_results(results)
    results.sort(key=lambda item: item.score, reverse=True)
    return results[:limit]


def format_evidence(results: list[RetrievedChunk]) -> str:
    if not results:
        return "当前索引中没有找到足够证据。"

    return "\n".join(
        format_retrieved_chunk(index, item)
        for index, item in enumerate(results, start=1)
    )