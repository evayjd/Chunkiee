from sentence_transformers import SentenceTransformer
from typing import List
import torch


class EmbeddingModel:

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3", 
        device: str | None = None,
        batch_size: int = 12          
    ):

        if device is None:
            device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.device = device
        self.batch_size = batch_size
        self.model = SentenceTransformer(
            model_name,
            device=device
        )

#给文档文本做embedding
    def embed_documents(self, texts: List[str]) -> List[List[float]]:

        embeddings = self.model.encode(
            texts,                       # 输入文本列表
            batch_size=self.batch_size,  # 批量处理大小
            convert_to_numpy=True,       # 输出 numpy array
            normalize_embeddings=True    # 向量归一化
        )

        # numpy 转为 python list，方便数据库存储
        return embeddings.tolist()

#为用户查询生成embedding向量
    def embed_query(self, query: str) -> List[float]:

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()
    
    
