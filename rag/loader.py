from pathlib import Path
from dataclasses import dataclass

import fitz

from config import settings


from dataclasses import dataclass, field


@dataclass
class DocumentChunk:
    """
    文档片段。

    block_type:
    - page_text
    - title
    - paragraph
    - table
    - formula
    - figure_caption
    - checklist
    - reference
    """

    text: str
    source: str
    page: int | None = None
    section_title: str | None = None
    block_type: str = "page_text"
    metadata: dict = field(default_factory=dict)

_ALLOWED_SUFFIXES = {".pdf", ".txt", ".md"}


def load_document(file_path: str) -> list[DocumentChunk]:
    """
    加载文档。

    支持：
    1. PDF
    2. TXT
    3. Markdown

    返回：
        list[DocumentChunk]
    """

    path = _resolve_project_path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    if not path.is_file():
        raise ValueError(f"目标不是文件：{file_path}")

    suffix = path.suffix.lower()

    if suffix not in _ALLOWED_SUFFIXES:
        raise ValueError(f"不支持的文件类型：{suffix}")

    if suffix == ".pdf":
        return _load_pdf(path)

    if suffix in {".txt", ".md"}:
        return _load_text_file(path)

    raise ValueError(f"不支持的文件类型：{suffix}")


def _load_pdf(path: Path) -> list[DocumentChunk]:
    """
    读取 PDF，按页返回文本。
    """

    chunks: list[DocumentChunk] = []

    with fitz.open(path) as pdf:
        for page_index in range(pdf.page_count):
            page = pdf.load_page(page_index)
            text = page.get_text().strip() # type: ignore

            if not text:
                continue

            chunks.append(
                DocumentChunk(
                    text=text,
                    source=str(path),
                    page=page_index + 1,
                    block_type="page_text",
                )
            )

    return chunks


def _load_text_file(path: Path) -> list[DocumentChunk]:
    """
    读取 txt / md 文件。
    """

    text = path.read_text(encoding="utf-8").strip()

    if not text:
        return []

    return [
        DocumentChunk(
            text=text,
            source=str(path),
            page=None,
        )
    ]


def _resolve_project_path(file_path: str) -> Path:
    """
    将用户输入路径转换为项目内绝对路径。
    """

    path = Path(file_path).expanduser()

    if not path.is_absolute():
        path = settings.base_dir / path

    path = path.resolve()

    if not _is_inside_base_dir(path, settings.base_dir):
        raise PermissionError("不允许读取项目目录之外的文件。")

    return path


def _is_inside_base_dir(path: Path, base_dir: Path) -> bool:
    """
    判断 path 是否在项目根目录内。
    """

    try:
        path.relative_to(base_dir.resolve())
        return True
    except ValueError:
        return False