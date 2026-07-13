"""Turns chunk text into vectors."""

from sentence_transformers import SentenceTransformer

from . import config

_model = None


def _get_model():
    global _model
    if _model is None:
        print("    loading embedding model, ~2GB, first run downloads it, be patient...")
        _model = SentenceTransformer(config.EMBEDDING_MODEL, token=config.HF_TOKEN)
        print("    embedding model ready")
    return _model


def embed_texts(texts, batch_size=16):
    model = _get_model()
    return model.encode(texts, batch_size=batch_size, normalize_embeddings=True).tolist()