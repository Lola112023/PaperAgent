from typing import List, Dict
from openai import OpenAI

from config import settings

class LLMError(RuntimeError):
    pass

class LLMClient:
    """
    LLM 客户端封装。

    当前支持：
    1. DeepSeek
    2. OpenAI

    DeepSeek 使用 OpenAI SDK 的兼容模式：
    - api_key 使用 DEEPSEEK_API_KEY
    - base_url 使用 https://api.deepseek.com
    """

    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.model = settings.llm_model

        if self.provider == "deepseek":
            if not settings.deepseek_api_key:
                raise ValueError(
                    "未检测到 DEEPSEEK_API_KEY。请在 .env 文件中配置 DEEPSEEK_API_KEY。"
                )

            self.client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )

        elif self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError(
                    "未检测到 OPENAI_API_KEY。请在 .env 文件中配置 OPENAI_API_KEY。"
                )

            self.client = OpenAI(
                api_key=settings.openai_api_key,
            )

        else:
            raise ValueError(
                f"不支持的 LLM_PROVIDER：{settings.llm_provider}。当前仅支持 deepseek / openai。"
            )

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        根据 messages 调用大模型，并返回文本结果。
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,# type: ignore[arg-type]
                temperature=settings.temperature,
                max_tokens=settings.max_output_tokens,
            )

            content = response.choices[0].message.content

            if content is None:
                return "模型没有返回有效文本。"

            return content

        except Exception as e:
            raise LLMError(f"LLM 调用失败：{e}") from e