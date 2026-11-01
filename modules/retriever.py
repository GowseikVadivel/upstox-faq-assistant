from functools import lru_cache
from typing import List, Dict, Any
from urllib.parse import urlparse

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL
from modules.vector_store import get_collection

OFFICIAL_DOMAINS = ("upstox.com", "nseindia.com", "bseindia.com", "sebi.gov.in")


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def is_official_source(url: str) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    return any(hostname == domain or hostname.endswith(f".{domain}") for domain in OFFICIAL_DOMAINS)


def retrieve_context(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    query = query.strip()
    if not query:
        return []
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    collection = get_collection()
    collection_count = collection.count()
    if collection_count == 0:
        return []

    model = get_embedding_model()
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection_count),
        include=["documents", "metadatas", "distances"],
    )

    contexts = []
    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        meta = metadata or {}
        url = str(meta.get("url", ""))
        if not is_official_source(url):
            continue

        source = {
            "document": document,
            "title": meta.get("title", "Unknown"),
            "url": url,
            "section": meta.get("section") or meta.get("title", ""),
            "category": meta.get("category", "general"),
            "distance": distance,
            "similarity_score": 1.0 - distance,
        }
        contexts.append(source)

    return contexts


def get_top_snippets(query: str, top_k: int = 3) -> List[str]:
    contexts = retrieve_context(query, top_k=top_k)
    return [item["document"] for item in contexts]
