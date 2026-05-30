from tools.calculator import calculator
from tools.file_reader import read_file


TOOL_REGISTRY = {
    "calculator": {
        "name": "calculator",
        "description": "用于计算数学表达式。",
        "function": calculator,
    },
    "read_file": {
        "name": "read_file",
        "description": "用于读取本地文本文件。",
        "function": read_file,
    },
}


def get_tool(name: str):
    """
    根据工具名称获取工具。
    """
    return TOOL_REGISTRY.get(name)


def list_tools():
    """
    返回所有已注册工具的信息。
    """
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
        }
        for tool in TOOL_REGISTRY.values()
    ]