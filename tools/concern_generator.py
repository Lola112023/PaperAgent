from tools.paper_analysis_common import collect_evidence, format_evidence


def generate_concerns() -> str:
    try:
        evidence = collect_evidence(
            [
                "limitations weakness failure case future work",
                "dataset coverage generalization robustness",
                "baseline fairness comparison",
                "ablation study missing component analysis",
                "reproducibility implementation details compute resources",
                "statistical significance error bar multiple runs",
            ],
            limit=14,
        )

        return (
            "你是一名严谨的论文审稿人。请基于证据提出 3-6 条 concern。\n\n"
            "每条 concern 必须包含：\n"
            "- Concern：问题是什么\n"
            "- 证据：页码、章节或 chunk_id\n"
            "- 影响：为什么会削弱论文结论\n"
            "- 建议：作者可以增加什么实验或说明\n"
            "- 置信度：高 / 中 / 低\n\n"
            "禁止把未检索到的内容说成论文缺失；"
            "证据不足时使用条件式表达。\n\n"
            f"证据：\n{format_evidence(evidence)}"
        )
    except FileNotFoundError:
        return "Concern 生成失败：请先为论文建立索引。"
    except Exception as e:
        return f"Concern 生成失败：{e}"