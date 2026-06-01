from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    加载 embedding 模型。

    使用 lru_cache 避免每次调用都重复加载模型。
    """

    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    将多段文本转换为 embedding 向量。

    参数：
        texts: 文本列表

    返回：
        numpy.ndarray，形状为 [文本数量, 向量维度]
    """

    if not texts:
        return np.empty((0, 0), dtype=np.float32)

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.astype(np.float32)


def embed_query(query: str) -> np.ndarray:
    """
    将用户查询转换为 embedding 向量。
    """

    query = query.strip()

    if not query:
        raise ValueError("查询不能为空。")

    embeddings = embed_texts([query])

    return embeddings[0]