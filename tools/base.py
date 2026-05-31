from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class Tool:
    """
    工具数据结构。

    每个工具都包含：
    1. name：工具名称
    2. description：工具描述
    3. function：真正执行的函数
    """
    name: str
    description: str
    function: Callable[..., Any]