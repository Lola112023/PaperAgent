from config import settings
from tools.registry import list_tools
from agent.memory import ConversationMemory


def test_settings():
    assert settings.project_name == "PaperAgent"


def test_memory_init():
    memory = ConversationMemory()
    assert memory.get_messages() == []


def test_memory_add_message():
    memory = ConversationMemory()
    memory.add_user_message("你好")
    memory.add_assistant_message("你好，我是 PaperAgent")

    messages = memory.get_messages()

    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_list_tools():
    tools = list_tools()
    assert len(tools) >= 2