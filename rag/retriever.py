from dataclasses import dataclass

import numpy as np

from rag.embedder import embed_query
from rag.vector_store import VectorStore


@dataclass
class RetrievedChunk:
    text: str
    source: str
    page: int | None
    chunk_id: int
    score: float
    section_title: str | None = None
    block_type: str = "content"

def retrieve(query: str, top_k: int = 5) -> list[RetrievedChunk]:
    """
    根据 query 从本地向量库中检索最相关 chunk。
    """

    if top_k <= 0:
        raise ValueError("top_k 必须大于 0。")

    store = VectorStore()
    chunks, embeddings = store.load()

    if not chunks:
        return []

    query_embedding = embed_query(query)

    scores = embeddings @ query_embedding

    top_indices = np.argsort(scores)[::-1][:top_k]

    results: list[RetrievedChunk] = []

    for index in top_indices:
        chunk = chunks[int(index)]

        results.append(
            RetrievedChunk(
            text=chunk.text,
            source=chunk.source,
            page=chunk.page,
            chunk_id=chunk.chunk_id,
            score=float(scores[index]),
            section_title=chunk.section_title,
            block_type=chunk.block_type,
        )
        )

    return results