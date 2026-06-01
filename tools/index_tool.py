from rag.loader import load_document
from rag.chunker import split_documents
from rag.embedder import embed_texts
from rag.vector_store import VectorStore


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