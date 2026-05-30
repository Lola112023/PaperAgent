from typing import List, Dict


class ConversationMemory:
    """
    简单的对话记忆模块。
    当前版本只保存本轮程序运行期间的历史消息。
    """

    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_user_message(self, content: str):
        self.messages.append({
            "role": "user",
            "content": content
        })

    def add_assistant_message(self, content: str):
        self.messages.append({
            "role": "assistant",
            "content": content
        })

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

    def clear(self):
        self.messages.clear()