from pathlib import Path

from config import settings


_ALLOWED_SUFFIXES = {".txt", ".md"}
_MAX_FILE_SIZE = 200_000


def read_file(file_path: str) -> str:
    """
    读取本地 txt / md 文件。

    安全限制：
    1. 只允许读取项目目录内的文件；
    2. 只支持 .txt 和 .md；
    3. 文件大小不能超过 200KB。
    """

    try:
        path = Path(file_path).expanduser()

        if not path.is_absolute():
            path = settings.base_dir / path

        path = path.resolve()

        if not _is_inside_base_dir(path, settings.base_dir):
            return "读取失败：不允许读取项目目录之外的文件。"

        if not path.exists():
            return f"读取失败：文件不存在：{file_path}"

        if not path.is_file():
            return f"读取失败：目标不是文件：{file_path}"

        if path.suffix.lower() not in _ALLOWED_SUFFIXES:
            return f"读取失败：不支持的文件类型：{path.suffix}。当前只支持 .txt 和 .md。"

        if path.stat().st_size > _MAX_FILE_SIZE:
            return "读取失败：文件过大，当前最大支持 200KB。"

        content = path.read_text(encoding="utf-8")

        if not content.strip():
            return "读取成功，但文件内容为空。"

        return content

    except UnicodeDecodeError:
        return "读取失败：文件编码不是 UTF-8，请转换编码后重试。"
    except Exception as e:
        return f"读取失败：{e}"


def _is_inside_base_dir(path: Path, base_dir: Path) -> bool:
    """
    判断 path 是否位于项目根目录 base_dir 内。
    """

    try:
        path.relative_to(base_dir.resolve())
        return True
    except ValueError:
        return False