from typing import Dict, List
import ast
import numpy as np


def _to_float_array(x) -> np.ndarray:
    """
    把输入统一转换成 numpy float 向量

    支持：
    1. list / tuple
    2. numpy array
    3. 字符串形式的向量，例如 "[0.1, 0.2, -0.3]"
    """
    if x is None:
        return np.array([], dtype=float)

    if isinstance(x, np.ndarray):
        return x.astype(float)

    if isinstance(x, (list, tuple)):
        return np.array([float(v) for v in x], dtype=float)

    if isinstance(x, str):
        text = x.strip()

        if not text:
            return np.array([], dtype=float)

        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, (list, tuple)):
                return np.array([float(v) for v in parsed], dtype=float)
        except Exception:
            pass

        text = text.strip("[]")
        if not text:
            return np.array([], dtype=float)

        return np.array(
            [float(v.strip()) for v in text.split(",") if v.strip()],
            dtype=float
        )

    try:
        return np.array([float(v) for v in x], dtype=float)
    except Exception as e:
        raise ValueError(f"无法把输入转换为向量：{type(x)}") from e


def _cosine(a, b) -> float:
    """
    计算 cosine similarity
    """
    a = _to_float_array(a)
    b = _to_float_array(b)

    # 任一向量为空，直接返回最小相似度
    if a.size == 0 or b.size == 0:
        return -1.0

    # 维度不一致时直接报错，便于尽早发现 embedding 维度问题
    if a.shape[0] != b.shape[0]:
        raise ValueError(
            f"向量维度不一致: {a.shape[0]} vs {b.shape[0]}"
        )

    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return -1.0

    return float(np.dot(a, b) / (denom + 1e-10))


def mmr_select(
    query_embedding: List[float],
    chunks: List[Dict],
    k: int,
    lambda_param: float = 0.7
) -> List[Dict]:
    """
    使用 MMR（Maximal Marginal Relevance）选择最终 chunks

    参数：
    - query_embedding: 查询向量
    - chunks: 候选 chunks，每个 chunk 里应包含 embedding
    - k: 最终返回数量
    - lambda_param: relevance 与 diversity 的权衡参数
    """
    if not chunks:
        return []

    # 只保留有 embedding 的 chunk，并提前做向量归一化
    valid_chunks: List[Dict] = []
    valid_embeddings: List[np.ndarray] = []

    for chunk in chunks:
        emb = chunk.get("embedding")

        if emb is None:
            continue

        emb_array = _to_float_array(emb)

        if emb_array.size == 0:
            continue

        copied = dict(chunk)
        copied["embedding"] = emb_array.tolist()

        valid_chunks.append(copied)
        valid_embeddings.append(emb_array)

    # 如果没有有效 embedding，直接返回前 k 个
    if not valid_chunks:
        return chunks[:k]

    query_vec = _to_float_array(query_embedding)

    selected_indices: List[int] = []
    candidate_indices = list(range(len(valid_chunks)))

    target_k = min(k, len(valid_chunks))

    while len(selected_indices) < target_k:
        best_score = -1e9
        best_idx = None

        for i in candidate_indices:
            relevance = _cosine(query_vec, valid_embeddings[i])

            redundancy = 0.0
            for j in selected_indices:
                redundancy = max(
                    redundancy,
                    _cosine(valid_embeddings[i], valid_embeddings[j])
                )

            score = (
                lambda_param * relevance
                - (1 - lambda_param) * redundancy
            )

            if score > best_score:
                best_score = score
                best_idx = i

        if best_idx is None:
            break

        selected_indices.append(best_idx)
        candidate_indices.remove(best_idx)

    return [valid_chunks[i] for i in selected_indices]