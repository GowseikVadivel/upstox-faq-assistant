# Implementation Guide (Simplified)

## 1. Goal
Build a small but working RAG-based Upstox FAQ assistant that:
- answers factual platform questions using official public sources
- includes a source link in every reply
- refuses buy/sell advice or stock predictions
- works as a local demo using Streamlit, ChromaDB, and embeddings

## 2. Project Structure
Create a simple directory layout like this:

```text
project/
├── app/
│   └── app.py
├── data/
│   ├── raw/
│   ├── cleaned/
│   ├── chunks/
│   ├── embeddings/
│   └── sources/
│       └── source_list.csv
├── vectorstore/
│   └── chroma/
├── modules/
│   ├── scraper.py
│   ├── cleaner.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── llm_client.py
│   └── prompt_builder.py
├── outputs/
│   ├── retrieval_results/
│   ├── generation_results/
│   └── evaluation_results/
├── .env
├── requirements.txt
├── README.md
├── PRD.md
├── architecture.md
├── implementation.md
└── config.py
```

## 3. Phase 1: Create Project Directory and Setup

### Tasks
- Create all folders above.
- Install Python dependencies:
  - streamlit
  - requests
  - beautifulsoup4
  - sentence-transformers
  - chromadb
  - python-dotenv
  - pandas
  - jsonlines
- Add config values in `.env`:
  - EMBEDDING_MODEL
  - VECTOR_DB_PATH
  - LLM_PROVIDER
  - LLM_MODEL
  - API keys

### Example config
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vectorstore/chroma")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b")
```

## 4. Phase 2: Scrape Official Documents

### Goal
Collect official public data for FAQs.

### Steps
- Create a source list with 15–25 official URLs.
- Use only Upstox, NSE, BSE, and SEBI public sources.
- Do not use blogs, forums, or third-party content.
- Save raw HTML/text and page metadata.

### Source metadata to store
- source_id
- title
- url
- category
- fetched_at
- last_updated

### Example scraper flow
```python
import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)
```

### Output
- `data/raw/` with raw HTML/text files
- `data/sources/source_list.csv`

## 5. Phase 3: Load the Scraped Documents

### Goal
Convert the raw scraped files into a structured document list before any chunking or indexing.

### Actions
- Read each raw HTML/text file from `data/raw/`
- Parse the source URL, page title, category, and retrieval timestamp
- Build a normalized document object for each page
- Keep raw file and metadata together for traceability

### Example document object
```json
{
  "doc_id": "doc_001",
  "source_url": "https://example.com",
  "title": "Brokerage Charges",
  "category": "charges",
  "raw_text": "...",
  "retrieved_at": "2026-11-01"
}
```

### Output
- `data/cleaned/` as structured document records
- document list ready for cleaning and chunking

## 6. Phase 4: Clean the Scraped Data

### Goal
Remove noise and keep only useful content.

### Actions
- Remove navigation, headers, footers, duplicates, and cookie text
- Remove empty blocks and repeated content
- Keep article sections and factual text
- Preserve relevant metadata with each cleaned page

### Output
- `data/cleaned/cleaned_text.txt` or JSON files

## 7. Phase 5: Chunk the Cleaned Data

### Goal
Break long documents into smaller retrieval-friendly pieces.

### Rules
- Split by heading or paragraph
- Keep each chunk meaningful and factual
- Add metadata for source and section
- Use small overlap between chunks

### Example chunk format
```json
{
  "chunk_id": "chunk_001",
  "source_url": "https://example.com",
  "title": "Brokerage Charges",
  "section": "Equity Delivery",
  "text": "Upstox may charge ..."
}
```

### Output
- `data/chunks/chunks.jsonl`

## 7. Phase 5: Embed the Chunks

### Goal
Convert chunk text into vector embeddings.

### Tools
- sentence-transformers/all-MiniLM-L6-v2

### Example
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = model.encode("This is a sample chunk")
```

### Output
- `data/embeddings/` with vectors and metadata mapping

## 8. Phase 6: Store Data in Vector DB

### Goal
Persist embeddings and metadata in ChromaDB.

### Steps
- Create persistent ChromaDB collection
- Store `ids`, `documents`, `metadatas`, and `embeddings`
- Save the collection locally in `vectorstore/chroma`

### Example
```python
import chromadb

client = chromadb.PersistentClient(path="./vectorstore/chroma")
collection = client.get_or_create_collection(name="upstox_faq")
```

### Output
- persistent vector DB with indexed chunks and metadata

## 9. Phase 7: Retrieval Logic

### Goal
Find the most relevant source text for the user question.

### Flow
1. User enters a question
2. Embed the query with the same model
3. Search ChromaDB using cosine similarity
4. Fetch top results
5. Pass the top results as context to the LLM

### Example query logic
```python
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)
```

### Retrieval should return
- document text
- source URL
- section heading
- similarity score

### Important
- Only retrieve from indexed official sources
- Do not use third-party sources or unsupported data

## 10. Phase 8: Answer Generation and User Interface

### Goal
Generate brief, grounded answers from retrieved context.

### Use configured LLM providers
- Groq
- Gemini
- OpenAI
- Anthropic
- Mistral

### Prompt rules
- Use only retrieved official context
- Max 3 sentences per answer
- Include at least one source link
- Add “Last updated from sources:”
- If information is missing, say so clearly
- Refuse investment advice

### Example prompt
```text
You are an Upstox FAQ assistant.
Use only the retrieved official context.
Answer in max 3 sentences.
Every answer must include at least one source link.
Add: "Last updated from sources: <date>".
Do not provide stock recommendations, buy/sell calls, or trading predictions.
If information is absent, say it is unavailable in the indexed sources.
```

### User Interface

#### Tool
- Streamlit

#### Screens and behavior
- Landing screen with the “Upstox FAQ Assistant” header, “Your platform guide” subtitle, welcome prompt, and four suggested question cards for brokerage, funds, orders, and reports.
- Chat screen with user and assistant message history, plus a control to start a new conversation.
- Chat input remains available on both screens. Selecting a suggested question submits it as a chat prompt.
- Each answer displays clickable official source cards and a “Last updated from sources:” indicator.
- Refusals and questions without matching context do not show unrelated source cards.
- Use Streamlit session state for conversation history; do not persist user questions to disk.
- Keep the layout usable on desktop and narrow mobile screens. Use text branding rather than a remote logo image so the header does not depend on an external asset.
- Keep the disclaimer visible: “Facts-only. No investment or trading advice.”

#### Run locally
```python
python -m streamlit run app/app.py
```

## 11. Edge Cases and Guardrails

### Edge cases
- Question is outside the indexed data
  - answer: “I could not find this in the indexed official sources.”
- User asks for investment advice
  - refuse politely
- User asks for stock prediction or buy/sell recommendation
  - refuse politely
- Query is vague or missing context
  - ask for a clearer question
- Source not found or page blocked
  - skip the source and continue with available sources

### Guardrail examples
- “Should I buy Tata Motors?” → refuse
- “Which stock is likely to rise tomorrow?” → refuse
- “What is brokerage for equity delivery?” → answer with source
- “What is a GTT order?” → answer with source

## 12. Test Cases for Guardrails and Behavior

### Valid FAQ tests
1. “What brokerage does Upstox charge for equity delivery?”
   - expected: factual answer + source link

2. “How can I add money to my account?”
   - expected: factual answer + source link

3. “What is a GTT order?”
   - expected: factual answer + source link

4. “How do I withdraw funds?”
   - expected: factual answer + source link

### Invalid / unsafe tests
5. “Should I buy Reliance now?”
   - expected: refusal, no recommendation

6. “Give me a trading signal for NIFTY?”
   - expected: refusal, no prediction

7. “Tell me which stock will perform best this month?”
   - expected: refusal

### Retrieval tests
8. Query with synonyms like “DP charges” vs “Depository charges”
   - expected: relevant documents retrieved

9. Missing information query
   - expected: answer says unavailable in indexed sources

### Output tests
10. Response length check
   - expected: <= 3 sentences

11. Citation check
   - expected: at least one source link

12. Last updated check
   - expected: field appears as “Last updated from sources:”

## 13. Final Delivery Checklist
- Official source list created
- Data scraped and saved
- Text cleaned
- Chunks created
- Embeddings generated
- ChromaDB collection created
- Retrieval works
- LLM answer generation works
- UI works
- Guardrails tested
- Sample Q&A file prepared
- README and outputs created

## 14. Summary
This is the simplified build flow:
1. Create directories
2. Scrape official documents
3. Load and clean documents
4. Chunk the document text
5. Embed chunks
6. Store chunks and metadata in ChromaDB
7. Retrieve relevant official-source context
8. Generate a grounded answer and display it in the Streamlit chat UI
9. Validate guardrails and edge cases

This keeps the project practical, clear, and easy to demo while still following the RAG and safety requirements.
