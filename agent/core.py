from agent.memory import ConversationMemory


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

        response = f"我已经收到你的问题：{user_input}\n当前是 Day 1 骨架版本，后续会接入 LLM 和工具调用。"

        self.memory.add_assistant_message(response)

        return response