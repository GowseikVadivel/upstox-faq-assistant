import json
import os

from sentence_transformers import SentenceTransformer

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHUNK_PATH = os.path.join(ROOT_DIR, "data", "chunks", "chunks.jsonl")
EMBEDDING_DIR = os.path.join(ROOT_DIR, "data", "embeddings")


def ensure_dirs():
    os.makedirs(EMBEDDING_DIR, exist_ok=True)


def generate_embeddings(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    ensure_dirs()
    model = SentenceTransformer(model_name)
    embeddings = []

    with open(CHUNK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            chunk = json.loads(line)
            text = chunk.get("text", "")
            if not text.strip():
                continue

            vector = model.encode(text).tolist()
            embeddings.append({
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "title": chunk["title"],
                "url": chunk["url"],
                "category": chunk["category"],
                "text": text,
                "embedding": vector,
            })

    output_path = os.path.join(EMBEDDING_DIR, "embeddings.json")
    with open(output_path, "w", encoding="utf-8") as fw:
        json.dump(embeddings, fw, ensure_ascii=False, indent=2)

    return embeddings, output_path


if __name__ == "__main__":
    data, output = generate_embeddings()
    print(f"Embedding count: {len(data)}")
    print(f"Saved to: {output}")
