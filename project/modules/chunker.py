import json
import os
import re
from typing import List, Dict

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOADED_PATH = os.path.join(ROOT_DIR, "data", "cleaned", "loaded_documents.json")
CHUNK_DIR = os.path.join(ROOT_DIR, "data", "chunks")


def ensure_dirs():
    os.makedirs(CHUNK_DIR, exist_ok=True)


def clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\u00a0", " ")
    return text.strip()


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    text = clean_text(text)
    if len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start += chunk_size - overlap

    return chunks


def chunk_documents():
    ensure_dirs()
    chunks = []

    with open(LOADED_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)

    for doc in documents:
        content = doc.get("content", "")
        title = doc.get("source_title", doc.get("title", "Unknown"))
        url = doc.get("source_url", "N/A")
        category = doc.get("category", "general")

        parts = split_into_chunks(content)
        for idx, part in enumerate(parts, start=1):
            chunk = {
                "chunk_id": f"{doc.get('doc_id', 'doc')}_chunk_{idx}",
                "doc_id": doc.get("doc_id", "doc"),
                "title": title,
                "url": url,
                "category": category,
                "text": part,
                "chunk_index": idx,
            }
            chunks.append(chunk)

    output_path = os.path.join(CHUNK_DIR, "chunks.jsonl")
    with open(output_path, "w", encoding="utf-8") as f:
        for item in chunks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return chunks, output_path


if __name__ == "__main__":
    result, output_path = chunk_documents()
    print(f"Chunk count: {len(result)}")
    print(f"Saved at: {output_path}")
