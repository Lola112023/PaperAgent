from rag.loader import load_document
from rag.chunker import split_documents
from rag.embedder import embed_texts


def embedding_preview(file_path: str) -> str:
    """
    加载文档、切分文本，并生成 embedding 预览信息。
    """

    try:
        documents = load_document(file_path)
        chunks = split_documents(documents)

        if not chunks:
            return "文档没有可用于 embedding 的 chunk。"

        texts = [chunk.text for chunk in chunks]
        embeddings = embed_texts(texts)

        return (
            f"Embedding 生成成功。\n"
            f"chunk 数量：{len(chunks)}\n"
            f"embedding 矩阵形状：{embeddings.shape}\n"
            f"第一个 chunk 前 100 字：\n{chunks[0].text[:100]}"
        )

    except Exception as e:
        return f"Embedding 生成失败：{e}"