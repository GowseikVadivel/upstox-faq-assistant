import csv
import os
from datetime import datetime
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
SOURCE_CSV = os.path.join(ROOT_DIR, "data", "sources", "source_list.csv")


def ensure_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)


def is_valid_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not url:
        return False
    parsed = urlsplit(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def fetch_single_source(url: str, title: str = "", category: str = "") -> dict:
    if not is_valid_url(url):
        raise ValueError(f"Invalid source URL: {url!r}")

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    html = response.text
    text = extract_text_from_html(html)

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    filename = f"{title.lower().replace(' ', '_').replace('/', '_') or 'source'}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
    file_path = os.path.join(RAW_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    return {
        "title": title,
        "url": url,
        "category": category,
        "raw_file": file_path,
        "fetched_at": timestamp,
        "source_length_chars": len(text),
    }


def read_sources(csv_path: str = SOURCE_CSV):
    rows = []
    with open(csv_path, "r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = (row.get("url") or "").strip()
            title = (row.get("title") or "").strip()
            category = (row.get("category") or "").strip()
            if is_valid_url(url):
                rows.append({"title": title, "url": url, "category": category})
    return rows


def scrape_source_list(csv_path: str = SOURCE_CSV):
    ensure_dirs()
    rows = read_sources(csv_path)
    scraped = []

    for row in rows:
        url = row["url"]
        title = row.get("title") or "Untitled Source"
        category = row.get("category") or "general"

        try:
            result = fetch_single_source(url, title=title, category=category)
            scraped.append(result)
            print(f"Scraped: {title} -> {url}")
        except Exception as exc:
            print(f"Skipped: {title} ({url}) -> {exc}")

    return scraped


if __name__ == "__main__":
    scrape_source_list()
