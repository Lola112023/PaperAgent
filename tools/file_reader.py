from pathlib import Path


def read_file(file_path: str) -> str:
    """
    读取本地文本文件。

    当前是 Day 1 简单版本。
    Day 5 会完善异常处理和文件类型判断。
    """
    path = Path(file_path)

    if not path.exists():
        return f"文件不存在：{file_path}"

    return path.read_text(encoding="utf-8")