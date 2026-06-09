from tools.paper_analysis_common import collect_evidence, format_evidence


def analyze_experiment() -> str:
    try:
        evidence = collect_evidence(
            [
                "experimental setup dataset benchmark data split",
                "baseline comparison metric evaluation protocol",
                "main results table performance improvement",
                "ablation study sensitivity analysis",
                "failure case error analysis statistical significance",
            ],
            limit=12,
        )

        return (
            "请严格基于以下证据分析论文实验。\n\n"
            "输出结构：\n"
            "1. 数据集与数据划分\n"
            "2. 对比基线\n"
            "3. 评价指标\n"
            "4. 实验设置\n"
            "5. 主要结果\n"
            "6. 消融实验\n"
            "7. 失败案例或误差分析\n"
            "8. 实验是否足以支持论文结论\n\n"
            "要求：区分论文明确报告的事实与分析性判断；"
            "引用页码或 chunk_id；没有证据时不要补写。\n\n"
            f"证据：\n{format_evidence(evidence)}"
        )
    except FileNotFoundError:
        return "实验分析失败：请先为论文建立索引。"
    except Exception as e:
        return f"实验分析失败：{e}"