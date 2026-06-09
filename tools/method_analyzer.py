from tools.paper_analysis_common import collect_evidence, format_evidence


def analyze_method() -> str:
    try:
        evidence = collect_evidence(
            [
                "method approach framework architecture pipeline",
                "proposed model core module algorithm",
                "input output training objective loss function",
                "difference compared with baseline method",
            ],
            limit=10,
        )

        return (
            "请严格基于以下证据分析论文方法。\n\n"
            "输出结构：\n"
            "1. 方法目标\n"
            "2. 输入与输出\n"
            "3. 整体流程\n"
            "4. 核心模块\n"
            "5. 训练目标或关键公式\n"
            "6. 与已有方法的区别\n"
            "7. 方法的潜在优点与限制\n\n"
            "要求：每个重要结论尽量标注页码或 chunk_id；"
            "没有证据时明确写无法确定。\n\n"
            f"证据：\n{format_evidence(evidence)}"
        )
    except FileNotFoundError:
        return "方法分析失败：请先为论文建立索引。"
    except Exception as e:
        return f"方法分析失败：{e}"