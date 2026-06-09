from tools.paper_analysis_common import collect_evidence, format_evidence


def generate_ppt_outline() -> str:
    try:
        evidence = collect_evidence(
            [
                "title abstract contribution",
                "background motivation problem definition",
                "method framework architecture",
                "experiment dataset metric baseline results",
                "limitations conclusion future work",
            ],
            limit=12,
        )

        return (
            "请基于证据生成 8-12 页学术汇报 PPT 大纲。\n\n"
            "每页包含：\n"
            "- 页面标题\n"
            "- 3-5 个核心要点\n"
            "- 推荐展示的图、表或公式\n"
            "- 演讲备注\n"
            "- 证据页码或 chunk_id\n\n"
            "推荐结构：标题、背景、问题、方法总览、核心模块、"
            "实验设置、主要结果、消融、优缺点、总结。\n\n"
            f"证据：\n{format_evidence(evidence)}"
        )
    except FileNotFoundError:
        return "PPT 大纲生成失败：请先为论文建立索引。"
    except Exception as e:
        return f"PPT 大纲生成失败：{e}"