from typing import Any

from tools.base import Tool
from tools.calculator import calculator
from tools.file_reader import read_file
from tools.document_loader import load_document_preview
from tools.chunk_tool import chunk_document_preview

TOOL_REGISTRY: dict[str, Tool] = {
    "calculator": Tool(
        name="calculator",
        description="用于计算数学表达式，例如 12 * (3 + 4)。",
        function=calculator,
    ),
    "read_file": Tool(
        name="read_file",
        description="用于读取本地 txt / md 文件内容。",
        function=read_file,
    ),
    "load_document": Tool(
        name="load_document",
        description="用于加载 PDF / TXT / Markdown 文档，并返回文本预览。",
        function=load_document_preview,
    ),
    "chunk_document": Tool(
        name="chunk_document",
        description="用于加载并切分 PDF / TXT / Markdown 文档。",
        function=chunk_document_preview,
    ),
}


def get_tool(name: str) -> Tool | None:
    """
    根据工具名称获取工具对象。
    """

    return TOOL_REGISTRY.get(name)

def list_tools() -> list[dict[str, str]]:
    """
    返回所有工具的名称和描述。

    这个函数主要用于展示给用户，或者后续提供给 LLM 判断可用工具。
    """

    return [
        {
            "name": tool.name,
            "description": tool.description,
        }
        for tool in TOOL_REGISTRY.values()
    ]


def run_tool(name: str, **kwargs: Any) -> str:
    """
    根据工具名称和参数执行工具。

    参数：
        name: 工具名称
        kwargs: 工具参数

    返回：
        工具执行结果，统一转换为字符串。
    """

    tool = get_tool(name)

    if tool is None:
        return f"工具不存在：{name}"

    try:
        result = tool.function(**kwargs)
        return str(result)
    except TypeError as e:
        return f"工具参数错误：{e}"
    except Exception as e:
        return f"工具执行失败：{e}"