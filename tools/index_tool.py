from rag.loader import load_document
from rag.chunker import split_documents
from rag.embedder import embed_texts
from rag.vector_store import VectorStore


def index_status() -> str:
    """
    查看本地向量索引状态。
    """

    store = VectorStore()

    if not store.exists():
        return (
            "当前还没有建立向量索引。\n"
            "请先使用：/index 文件路径\n"
            "例如：/index data/example.md"
        )

    try:
        chunks, embeddings = store.load()

        sources = sorted(set(chunk.source for chunk in chunks))

        lines = [
            "当前向量索引状态：",
            f"chunk 数量：{len(chunks)}",
            f"embedding 形状：{embeddings.shape}",
            "包含来源文件：",
        ]

        for source in sources:
            lines.append(f"- {source}")

        return "\n".join(lines)

    except Exception as e:
        return f"索引状态读取失败：{e}"

def build_index(file_path: str) -> str:
    """
    为指定文档建立本地向量索引。
    """

    try:
        documents = load_document(file_path)
        chunks = split_documents(documents)

        if not chunks:
            return "索引建立失败：文档没有有效文本。"

        texts = [chunk.text for chunk in chunks]
        embeddings = embed_texts(texts)

        store = VectorStore()
        store.save(chunks, embeddings)

        return (
            f"索引建立成功。\n"
            f"文件：{file_path}\n"
            f"chunk 数量：{len(chunks)}\n"
            f"embedding 形状：{embeddings.shape}"
        )

    except Exception as e:
        return f"索引建立失败：{e}"