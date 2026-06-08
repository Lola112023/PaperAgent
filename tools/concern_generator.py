from rag.retriever import retrieve


def generate_concerns() -> str:
    """
    基于当前索引文档，生成论文 concern / 不足分析。
    """

    try:
        queries = [
            "limitations weakness future work limitation discussion",
            "ablation study 消融实验 模块分析 是否充分",
            "baseline comparison previous methods fair comparison",
            "dataset benchmark 数据集 实验规模 泛化性 generalization",
            "evaluation metrics 指标 human evaluation robustness",
            "实验设置是否充分 是否有局限性 是否存在不足",
        ]

        blocks = []

        for query in queries:
            results = retrieve(query, top_k=4)
            blocks.append(f"【检索问题】{query}")

            if not results:
                blocks.append("未检索到相关内容。")
                continue

            for index, item in enumerate(results, start=1):
                page_text = f"第 {item.page} 页" if item.page is not None else "无页码"

                blocks.append(
                    f"[结果 {index}]\n"
                    f"来源：{item.source}\n"
                    f"页码：{page_text}\n"
                    f"chunk_id：{item.chunk_id}\n"
                    f"相似度：{item.score:.4f}\n"
                    f"内容：\n{item.text[:1200]}\n"
                )

            blocks.append("-" * 60)

        context = "\n".join(blocks)

        return (
            "下面是从当前索引文档中检索到的与论文不足、局限性、实验设计相关的内容。\n"
            "请基于这些内容生成学术 concern。\n\n"
            "输出格式要求：\n"
            "Concern 1：标题\n"
            "依据：引用来源、页码或 chunk_id。\n"
            "为什么是问题：解释该问题为什么会影响论文说服力。\n"
            "改进建议：说明可以如何补充实验或改进方法。\n\n"
            "Concern 2：标题\n"
            "依据：……\n"
            "为什么是问题：……\n"
            "改进建议：……\n\n"
            "要求：\n"
            "- 至少给出 3 条 concern；\n"
            "- 必须基于检索内容，不要无依据批评；\n"
            "- 如果证据不足，要明确说明“当前检索结果不足以判断”；\n"
            "- 优先关注实验充分性、baseline、ablation、数据集、指标和泛化性。\n\n"
            f"检索内容如下：\n{context}"
        )

    except FileNotFoundError:
        return (
            "Concern 生成失败：当前还没有建立向量索引。\n"
            "请先使用 /index 文件路径 建立索引。"
        )
    except Exception as e:
        return f"Concern 生成失败：{e}"