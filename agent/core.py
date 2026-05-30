from agent.memory import ConversationMemory
from llm.client import LLMClient
from agent.prompts import SYSTEM_PROMPT

class PaperAgent:
    """
    PaperAgent 核心类。

    Day 1 版本：
    - 暂时不接入真实 LLM；
    - 暂时不调用工具；
    - 只完成基础结构。
    """

    def __init__(self):
        self.memory = ConversationMemory()
        self.llm = LLMClient()

    def run(self, user_input: str) -> str:
        """
        运行一次 Agent。

        当前版本只返回固定响应。
        后续会在这里加入：
        1. LLM 调用；
        2. 工具选择；
        3. 工具执行；
        4. 多轮 Agent Loop。
        """
        self.memory.add_user_message(user_input)

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        messages.extend(self.memory.get_messages())

        response = self.llm.chat(messages)

        self.memory.add_assistant_message(response)

        return response