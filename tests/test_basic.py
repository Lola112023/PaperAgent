from config import settings
from tools.registry import list_tools
from agent.memory import ConversationMemory
from tools.calculator import calculator
from tools.file_reader import read_file
from rag.loader import load_document

def test_read_file_success():
    result = read_file("data/example.md")
    assert "PaperAgent" in result


def test_read_file_not_exist():
    result = read_file("data/not_exist.md")
    assert "文件不存在" in result


def test_read_file_not_supported():
    result = read_file("config.py")
    assert "不支持的文件类型" in result
    

def test_calculator_add():
    result = calculator("1 + 2")
    assert "3" in result


def test_calculator_complex():
    result = calculator("12 * (3 + 4)")
    assert "84" in result


def test_calculator_zero_division():
    result = calculator("10 / 0")
    assert "除数不能为 0" in result


def test_calculator_illegal_expression():
    result = calculator('__import__("os").system("dir")')
    assert "计算失败" in result


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




def test_load_markdown_document():
    chunks = load_document("data/example.md")

    assert len(chunks) == 1
    assert "PaperAgent" in chunks[0].text
    assert chunks[0].page is None

from rag.loader import load_document
from rag.chunker import split_documents, split_text


def test_split_text_short():
    chunks = split_text("hello world", chunk_size=100, overlap=10)
    assert len(chunks) == 1
    assert chunks[0] == "hello world"


def test_split_text_long():
    text = "a" * 2000
    chunks = split_text(text, chunk_size=800, overlap=100)

    assert len(chunks) == 3
    assert len(chunks[0]) == 800


def test_split_documents():
    documents = load_document("data/example.md")
    chunks = split_documents(documents, chunk_size=100, overlap=20)

    assert len(chunks) >= 1
    assert "PaperAgent" in chunks[0].text

from rag.embedder import embed_texts, embed_query


def test_embed_texts():
    embeddings = embed_texts(["PaperAgent 是一个智能体项目。", "这是第二段文本。"])

    assert embeddings.shape[0] == 2
    assert embeddings.shape[1] > 0


def test_embed_query():
    embedding = embed_query("什么是 Agent？")

    assert embedding.shape[0] > 0
from rag.vector_store import VectorStore
from rag.retriever import retrieve
from tools.index_tool import build_index


def test_build_index():
    result = build_index("data/example.md")
    assert "索引建立成功" in result


def test_retrieve():
    build_index("data/example.md")
    results = retrieve("PaperAgent 支持什么功能？", top_k=2)

    assert len(results) >= 1
    assert results[0].score > 0
    