import json
import re
from typing import Any


def parse_agent_response(response: str) -> dict[str, Any]:
    """
    解析 LLM 返回的 JSON。

    有些模型可能会在 JSON 外面包一层 ```json，
    所以这里做了简单清洗。
    """

    cleaned = response.strip()

    cleaned = _remove_markdown_code_block(cleaned)

    try:
        data = json.loads(cleaned)
        return data
    except json.JSONDecodeError:
        return {
            "type": "final_answer",
            "content": response,
        }


def _remove_markdown_code_block(text: str) -> str:
    """
    去掉模型可能返回的 Markdown 代码块。

    例如：
    ```json
    {"type": "final_answer", "content": "你好"}
    ```
    """

    pattern = r"^```(?:json)?\s*(.*?)\s*```$"
    match = re.match(pattern, text, flags=re.DOTALL)

    if match:
        return match.group(1).strip()

    return text