from agent.memory import ConversationMemory
from agent.prompts import SYSTEM_PROMPT
from agent.parser import parse_agent_response
from config import settings
from llm.client import LLMClient
from tools.registry import run_tool
from utils.logger import get_logger
from rag.vector_store import VectorStore

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
        high_level_tool = self._select_high_level_tool(user_input)
        self.memory.add_user_message(user_input)


        if high_level_tool is not None:
            tool_result = run_tool(high_level_tool)

            scratchpad.append({
                "role": "user",
                "content": (
                    f"用户的问题需要使用高级论文分析工具：{high_level_tool}。\n"
                    f"我已经调用该工具，结果如下：\n\n"
                    f"{tool_result}\n\n"
                    f"请严格基于以上工具结果回答用户问题。\n"
                    f"如果信息不足，请明确说明，不要编造。"
                ),
            })

        elif self._should_use_rag_first(user_input):
            tool_result = run_tool("search_index", query=user_input, top_k=5)

            scratchpad.append({
                "role": "user",
                "content": (
                    f"用户的问题很可能需要基于当前已建立索引的文档回答。\n"
                    f"我已经先调用 search_index 工具，结果如下：\n\n"
                    f"{tool_result}\n\n"
                    f"请严格基于以上检索结果回答用户问题。\n"
                    f"如果检索结果足够，请输出 final_answer JSON。\n"
                    f"如果检索结果不足，请在 final_answer 中明确说明。"
                ),
            })

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
    def _select_high_level_tool(self, user_input: str) -> str | None:
        """
        根据用户输入判断是否应该优先调用高级论文分析工具。

        注意：
        高级工具的优先级应该高于普通 search_index。
        """

        text = user_input.lower()

        summary_keywords = [
            "总结",
            "概括",
            "概述",
            "讲了什么",
            "说了什么",
            "主要内容",
            "overview",
            "summary",
            "summarize",
        ]

        method_keywords = [
            "方法",
            "模型",
            "框架",
            "结构",
            "pipeline",
            "method",
            "approach",
            "framework",
            "architecture",
            "algorithm",
        ]

        experiment_keywords = [
            "实验",
            "实验设置",
            "实验结果",
            "数据集",
            "指标",
            "baseline",
            "ablation",
            "消融",
            "evaluation",
            "experiment",
            "benchmark",
            "metric",
            "result",
        ]

        concern_keywords = [
            "不足",
            "缺点",
            "局限",
            "问题",
            "concern",
            "weakness",
            "limitation",
            "critique",
            "审稿意见",
        ]

        ppt_keywords = [
            "ppt",
            "pre",
            "汇报",
            "大纲",
            "presentation",
            "slide",
            "slides",
            "outline",
        ]

        if any(keyword in text for keyword in ppt_keywords):
            return "generate_ppt_outline"

        if any(keyword in text for keyword in concern_keywords):
            return "generate_concerns"

        if any(keyword in text for keyword in experiment_keywords):
            return "analyze_experiment"

        if any(keyword in text for keyword in method_keywords):
            return "analyze_method"

        if any(keyword in text for keyword in summary_keywords):
            return "summarize_paper"

        return None




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
    def _should_use_rag_first(self, user_input: str) -> bool:
        """
        判断当前问题是否应该优先走 RAG 检索。
        """

        keywords = [
            "这篇论文",
            "该论文",
            "当前文档",
            "这个文档",
            "这个文件",
            "这个PDF",
            "pdf",
            "PDF",
            "附件",
            "材料",
            "文中",
            "里面",
            "其中",
            "方法",
            "实验",
            "数据集",
            "baseline",
            "ablation",
            "limitation",
            "创新点",
            "不足",
        ]

        if not any(keyword in user_input for keyword in keywords):
            return False

        store = VectorStore()
        return store.exists()