import csv
import json
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
LOADED_DIR = os.path.join(ROOT_DIR, "data", "cleaned")
SOURCE_CSV = os.path.join(ROOT_DIR, "data", "sources", "source_list.csv")


def ensure_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(LOADED_DIR, exist_ok=True)


def load_source_metadata(csv_path: str = SOURCE_CSV):
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_raw_documents(raw_dir: str = RAW_DIR):
    documents = []
    for filename in sorted(os.listdir(raw_dir)):
        file_path = os.path.join(raw_dir, filename)
        if not os.path.isfile(file_path):
            continue

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        if not text.strip():
            continue

        doc = {
            "doc_id": filename.replace(".txt", ""),
            "source_file": file_path,
            "title": filename.replace(".txt", "").replace("_", " ").title(),
            "content": text,
            "loaded_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        documents.append(doc)

    return documents


def save_loaded_documents(documents, output_dir: str = LOADED_DIR):
    output_path = os.path.join(output_dir, "loaded_documents.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    return output_path


def load_documents():
    ensure_dirs()
    metadata = load_source_metadata()
    documents = load_raw_documents()

    for doc in documents:
        matched = next((m for m in metadata if m["title"].lower() in doc["title"].lower() or m["url"].split("/")[-2] in doc["doc_id"]), None)
        if matched:
            doc["source_title"] = matched.get("title")
            doc["source_url"] = matched.get("url")
            doc["category"] = matched.get("category")
        else:
            doc["source_title"] = "Unknown"
            doc["source_url"] = "N/A"
            doc["category"] = "general"

    output_path = save_loaded_documents(documents)
    return documents, output_path


if __name__ == "__main__":
    docs, output_path = load_documents()
    print(f"Loaded {len(docs)} documents")
    print(f"Saved to: {output_path}")
