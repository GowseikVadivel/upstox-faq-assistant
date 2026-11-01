import json
import os
from pathlib import Path
from typing import List, Dict, Any

import chromadb

from config import EMBEDDING_MODEL, VECTOR_DB_PATH

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EMBEDDINGS_PATH = os.path.join(ROOT_DIR, "data", "embeddings", "embeddings.json")
COLLECTION_NAME = "upstox_faq"


def ensure_vector_dir() -> str:
    configured_path = Path(VECTOR_DB_PATH)
    path = configured_path if configured_path.is_absolute() else Path(ROOT_DIR) / configured_path
    path = path.resolve()
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def load_embedding_records() -> List[Dict[str, Any]]:
    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_vector_store(reindex: bool = False):
    client = chromadb.PersistentClient(path=ensure_vector_dir())
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    rebuild = (
        reindex
        or collection.count() == 0
        or (collection.metadata or {}).get("hnsw:space") != "cosine"
    )

    if rebuild:
        records = load_embedding_records()
        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for record in records:
            chunk_id = str(record.get("chunk_id", "")).strip()
            text = str(record.get("text", "")).strip()
            embedding = record.get("embedding", [])
            if not chunk_id or not text or not embedding:
                continue

            ids.append(chunk_id)
            documents.append(text)
            embeddings.append(embedding)
            metadatas.append({
                "chunk_id": chunk_id,
                "doc_id": str(record.get("doc_id", "")),
                "title": str(record.get("title", "")),
                "url": str(record.get("url", "")),
                "category": str(record.get("category", "")),
            })

        if ids:
            if collection.count() > 0 or collection.metadata != {"hnsw:space": "cosine"}:
                client.delete_collection(name=COLLECTION_NAME)
                collection = client.create_collection(
                    name=COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )

            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

    return collection


def get_collection():
    return build_vector_store()


if __name__ == "__main__":
    indexed_collection = build_vector_store()
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Indexed chunks: {indexed_collection.count()}")
    print(f"Database path: {ensure_vector_dir()}")
