import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

def get_embedder():
    try:
        from fastembed import TextEmbedding
        print("Using FastEmbed TextEmbedding (BAAI/bge-small-en-v1.5)")
        model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        def embed_fn(texts):
            return list(model.embed(texts))
        return embed_fn
    except Exception as e1:
        print("FastEmbed error:", e1)

    try:
        from sentence_transformers import SentenceTransformer
        print("Using SentenceTransformer (BAAI/bge-large-en-v1.5)")
        model = SentenceTransformer("BAAI/bge-large-en-v1.5")
        def embed_fn(texts):
            return model.encode(texts, normalize_embeddings=True)
        return embed_fn
    except Exception as e2:
        print("SentenceTransformer error:", e2)

    return None

if __name__ == "__main__":
    embedder = get_embedder()
    if embedder:
        vecs = embedder(["segregation of duties in software release", "separation of duties"])
        print("Vectors generated successfully, shape/len:", len(vecs))
    else:
        print("No neural embedder available!")
