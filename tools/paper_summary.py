from rag.retriever import retrieve


def summarize_paper() -> str:
    """
    基于当前向量索引，对论文或文档进行结构化总结。
    """

    try:
        queries = [
            "论文的摘要、研究背景和主要问题是什么？",
            "本文提出了什么方法或系统？",
            "本文使用了哪些实验、数据集、评价指标和 baseline？",
            "本文的主要实验结果和结论是什么？",
            "本文是否提到了局限性、限制或未来工作？",
        ]

        retrieved_blocks = []

        for query in queries:
            results = retrieve(query, top_k=3)

            retrieved_blocks.append(f"【检索问题】{query}")

            if not results:
                retrieved_blocks.append("未检索到相关内容。")
                continue

            for index, item in enumerate(results, start=1):
                page_text = f"第 {item.page} 页" if item.page is not None else "无页码"
                retrieved_blocks.append(
                    f"[结果 {index}]\n"
                    f"来源：{item.source}\n"
                    f"页码：{page_text}\n"
                    f"chunk_id：{item.chunk_id}\n"
                    f"相似度：{item.score:.4f}\n"
                    f"内容：\n{item.text[:1200]}\n"
                )

            retrieved_blocks.append("-" * 60)

        context = "\n".join(retrieved_blocks)

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
            "要求：\n"
            "- 必须基于检索内容，不要编造；\n"
            "- 如果某部分没有明确证据，请写“当前检索结果未明确说明”；\n"
            "- 尽量保留来源、页码或 chunk_id。\n\n"
            f"检索内容如下：\n{context}"
        )

    except FileNotFoundError:
        return (
            "论文总结失败：当前还没有建立向量索引。\n"
            "请先使用 /index 文件路径 建立索引。"
        )
    except Exception as e:
        return f"论文总结失败：{e}"