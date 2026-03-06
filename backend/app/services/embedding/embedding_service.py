from .embedding_model import EmbeddingModel

_model = EmbeddingModel()


def embed_documents(texts):
    return _model.embed_documents(texts)


def embed_query(query):
    return _model.embed_query(query)