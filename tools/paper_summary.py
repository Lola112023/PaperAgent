from rag.retriever import retrieve, RetrievedChunk


def summarize_paper() -> str:
    """
    基于当前向量索引，对论文或文档进行结构化总结。

    这个版本会：
    1. 按论文结构分别检索；
    2. 过滤 checklist / references 等非正文内容；
    3. 保留页码、chunk_id、章节标题等 metadata；
    4. 返回适合 LLM 进一步总结的证据材料。
    """

    try:
        section_queries = {
            "研究背景": [
                "abstract research background motivation",
                "introduction problem motivation background",
            ],
            "研究问题": [
                "problem definition task challenge research question",
                "this paper aims to problem setting",
            ],
            "核心方法": [
                "method approach framework model architecture",
                "we propose our method pipeline algorithm",
            ],
            "实验设置": [
                "experiment evaluation dataset metric baseline benchmark",
                "experimental setup datasets metrics baselines",
            ],
            "主要结果": [
                "results performance achieves outperforms main results",
                "experimental results comparison performance table",
            ],
            "局限性或不足": [
                "limitation limitations discussion future work weakness",
                "failure case limitation future direction",
            ],
        }

        all_blocks: list[str] = []

        for section_name, queries in section_queries.items():
            all_blocks.append(f"\n## {section_name}")

            section_results: list[RetrievedChunk] = []

            for query in queries:
                results = retrieve(query, top_k=5)
                valid_results = _filter_valid_results(results)
                section_results.extend(valid_results)

            section_results = _deduplicate_results(section_results)
            section_results = section_results[:5]

            if not section_results:
                all_blocks.append("当前检索结果未明确说明。")
                continue

            for index, item in enumerate(section_results, start=1):
                all_blocks.append(_format_retrieved_chunk(index, item))

        context = "\n".join(all_blocks)

        return (
            "下面是从当前索引文档中检索到的论文关键信息。\n"
            "请基于这些内容进行结构化论文总结。\n\n"
            "输出格式要求：\n"
            "1. 研究背景\n"
            "2. 研究问题\n"
            "3. 核心方法\n"
            "4. 实验设置\n"
            "5. 主要结果\n"
            "6. 局限性或不足\n"
            "7. 一句话总结\n\n"
            "回答要求：\n"
            "- 必须基于检索内容，不要编造；\n"
            "- 如果某部分没有明确证据，请写“当前检索结果未明确说明”；\n"
            "- 尽量引用来源、页码、章节标题或 chunk_id；\n"
            "- 不要把 NeurIPS Checklist、References、模板说明当成论文正文；\n"
            "- 如果当前文档不是完整论文，而是声明、表格、Checklist、申请材料等，请明确说明文档类型，"
            "不要强行套用论文总结结构。\n\n"
            f"检索内容如下：\n{context}"
        )

    except FileNotFoundError:
        return (
            "论文总结失败：当前还没有建立向量索引。\n"
            "请先使用 /index 文件路径 建立索引。"
        )
    except Exception as e:
        return f"论文总结失败：{e}"


def _filter_valid_results(results: list[RetrievedChunk]) -> list[RetrievedChunk]:
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


def _deduplicate_results(results: list[RetrievedChunk]) -> list[RetrievedChunk]:
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


def _format_retrieved_chunk(index: int, item: RetrievedChunk) -> str:
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