from agent.memory import ConversationMemory
from agent.prompts import SYSTEM_PROMPT
from agent.parser import parse_agent_response
from config import settings
from llm.client import LLMClient
from tools.registry import run_tool
from utils.logger import get_logger

class PaperAgent:
    """
    PaperAgent 核心类。

    Day 6 版本：
    - 支持 LLM 自动判断是否调用工具；
    - 支持 calculator 和 read_file；
    - 支持最小 Agent Loop。
    """

    def __init__(self):
        self.memory = ConversationMemory()
        self.llm = LLMClient()
        self.logger = get_logger("PaperAgent")

    def run(self, user_input: str) -> str:
        """
        运行一次 Agent。

        流程：
        1. 保存用户输入；
        2. 让 LLM 判断是否需要调用工具；
        3. 如果需要工具，执行工具；
        4. 把工具结果交给 LLM；
        5. 返回最终答案。
        """
        self.logger.info(f"User input: {user_input}")

        self.memory.add_user_message(user_input)

        scratchpad: list[dict[str, str]] = []
        tool_trace: list[str] = []

        for step in range(settings.max_agent_steps):
            messages = self._build_messages(scratchpad)

            raw_response = self.llm.chat(messages)
            parsed_response = parse_agent_response(raw_response)

            response_type = parsed_response.get("type")

            if response_type == "final_answer":
                final_answer = parsed_response.get("content", "")

                if not final_answer:
                    final_answer = raw_response

                self.memory.add_assistant_message(final_answer)
                return final_answer

            if response_type == "tool_call":
                tool_name = parsed_response.get("tool_name")
                tool_args = parsed_response.get("tool_args", {})
                tool_trace.append(f"{tool_name}: {tool_args}")


                if not isinstance(tool_args, dict):
                    tool_result = "工具参数格式错误：tool_args 必须是字典。"
                else:
                    tool_result = run_tool(tool_name, **tool_args) # type: ignore

                scratchpad.append({
                    "role": "assistant",
                    "content": raw_response,
                })

                scratchpad.append({
                    "role": "user",
                    "content": (
                        f"工具 {tool_name} 的执行结果如下：\n\n"
                        f"{tool_result}\n\n"
                        f"请基于以上工具结果继续完成任务。\n"
                        f"如果信息已经足够，请输出 final_answer JSON。\n"
                        f"如果信息仍不足，并且还需要其他工具，请继续输出 tool_call JSON。\n"
                        f"注意：final_answer 中不要编造工具结果之外的信息。"
                    ),
                })
                self.logger.info(f"Tool call: {tool_name}, args: {tool_args}")
                self.logger.info(f"Tool result: {tool_result[:300]}")

                continue

            final_answer = f"无法识别模型输出：{raw_response}"
            self.memory.add_assistant_message(final_answer)
            if tool_trace:
                self.logger.info(f"Tool trace: {tool_trace}")
            return final_answer

        final_answer = "已达到最大 Agent 执行步数，任务未完成。"
        self.logger.info(f"Final answer: {final_answer[:300]}")
        self.memory.add_assistant_message(final_answer)
        if tool_trace:
                self.logger.info(f"Tool trace: {tool_trace}")
        return final_answer

    def _build_messages(self, scratchpad: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        构造发送给 LLM 的 messages。
        """

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        messages.extend(self.memory.get_messages())
        messages.extend(scratchpad)

        return messages

    def clear_memory(self):
        """
        清空对话记忆。
        """

        self.memory.clear()

    def get_history(self):
        """
        获取对话历史。
        """

        return self.memory.get_messages()