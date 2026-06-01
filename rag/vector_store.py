import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from config import settings
from rag.chunker import TextChunk


class VectorStore:
    """
    简单本地向量库。

    保存：
    1. chunks.json：文本片段及元数据
    2. embeddings.npy：对应 embedding 矩阵
    """

    def __init__(self, store_dir: Path | None = None):
        self.store_dir = store_dir or settings.vector_store_dir
        self.chunks_path = self.store_dir / "chunks.json"
        self.embeddings_path = self.store_dir / "embeddings.npy"

    def save(self, chunks: list[TextChunk], embeddings: np.ndarray) -> None:
        """
        保存 chunks 和 embeddings。
        """

        if len(chunks) != embeddings.shape[0]:
            raise ValueError("chunks 数量必须和 embeddings 行数一致。")

        self.store_dir.mkdir(parents=True, exist_ok=True)

        chunk_dicts = [asdict(chunk) for chunk in chunks]

        self.chunks_path.write_text(
            json.dumps(chunk_dicts, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        np.save(self.embeddings_path, embeddings)

    def load(self) -> tuple[list[TextChunk], np.ndarray]:
        """
        加载 chunks 和 embeddings。
        """

        if not self.chunks_path.exists() or not self.embeddings_path.exists():
            raise FileNotFoundError("向量库不存在，请先建立索引。")

        raw_chunks = json.loads(self.chunks_path.read_text(encoding="utf-8"))

        chunks = [
            TextChunk(
                text=item["text"],
                source=item["source"],
                page=item["page"],
                chunk_id=item["chunk_id"],
            )
            for item in raw_chunks
        ]

        embeddings = np.load(self.embeddings_path)

        return chunks, embeddings

    def exists(self) -> bool:
        """
        判断向量库是否存在。
        """

        return self.chunks_path.exists() and self.embeddings_path.exists()