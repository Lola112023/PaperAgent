from config import settings
from agent.core import PaperAgent
from tools.registry import list_tools


def test_settings():
    assert settings.project_name == "PaperAgent"


def test_agent_init():
    agent = PaperAgent()
    assert agent is not None


def test_list_tools():
    tools = list_tools()
    assert len(tools) >= 2