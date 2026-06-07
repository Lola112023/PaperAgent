from functools import lru_cache
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from config import settings
import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    加载 embedding 模型。

    如果 settings.embedding_model 是本地路径，则从本地加载；
    否则按 Hugging Face 模型名加载。
    """

    model_name_or_path = settings.embedding_model
    model_path = Path(model_name_or_path)

    if not model_path.is_absolute():
        local_path = settings.base_dir / model_path
    else:
        local_path = model_path

    if local_path.exists():
        return SentenceTransformer(str(local_path))

    return SentenceTransformer(model_name_or_path)


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    将多段文本转换为 embedding 向量。
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