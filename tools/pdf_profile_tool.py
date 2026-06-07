from rag.pdf_analyzer import analyze_pdf


def pdf_profile(file_path: str) -> str:
    """
    输出 PDF 类型诊断结果。
    """

    try:
        profile = analyze_pdf(file_path)

        return (
            "PDF 类型诊断结果：\n"
            f"文件：{profile.file_path}\n"
            f"页数：{profile.page_count}\n"
            f"总字符数：{profile.total_text_chars}\n"
            f"平均每页字符数：{profile.avg_chars_per_page:.2f}\n"
            f"空文本页数：{profile.empty_page_count}\n"
            f"是否像扫描版：{profile.is_scanned_like}\n"
            f"是否为文本型 PDF：{profile.is_text_pdf}\n"
            f"是否包含 Checklist / 模板类内容：{profile.has_checklist_like_content}\n"
            f"推荐解析策略：{profile.parse_suggestion}"
        )

    except Exception as e:
        return f"PDF 类型诊断失败：{e}"