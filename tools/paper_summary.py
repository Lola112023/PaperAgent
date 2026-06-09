from rag.retriever import retrieve, RetrievedChunk
from tools.paper_analysis_common import (
    deduplicate_results,
    filter_valid_results,
    format_retrieved_chunk
)

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
                valid_results = filter_valid_results(results)
                section_results.extend(valid_results)

            section_results = deduplicate_results(section_results)
            section_results = section_results[:5]

            if not section_results:
                all_blocks.append("当前检索结果未明确说明。")
                continue

            for index, item in enumerate(section_results, start=1):
                all_blocks.append(format_retrieved_chunk(index, item))

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




