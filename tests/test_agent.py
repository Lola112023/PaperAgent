from typing import Any, cast

from agent.core import PaperAgent
from llm.client import LLMError
from utils.logger import get_logger
from agent.memory import ConversationMemory



class FakeLLM:
    def chat(self, messages):
        return '{"type":"final_answer","content":"测试回答"}'


def test_agent_only_saves_user_message_once():
    agent = cast(Any, PaperAgent.__new__(PaperAgent))

    agent.memory = __import__(
        "agent.memory", fromlist=["ConversationMemory"]
    ).ConversationMemory()
    agent.llm = FakeLLM()
    agent.logger = __import__(
        "utils.logger", fromlist=["get_logger"]
    ).get_logger("test-agent")

    result = agent.run("你好")
    history = agent.get_history()

    assert result == "测试回答"
    assert [item["role"] for item in history] == ["user", "assistant"]


class FailingLLM:
    def chat(self, messages):
        raise LLMError("LLM 调用失败：测试错误")


def test_agent_returns_clear_llm_error():
    agent = cast(Any, PaperAgent.__new__(PaperAgent))
    agent.memory = ConversationMemory()
    agent.llm = FailingLLM()
    agent.logger = get_logger("test-agent-error")

    result = agent.run("你好")

    assert result == "LLM 调用失败：测试错误"
    