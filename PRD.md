# Product Requirements Document (PRD)

## 1. Product Name
Upstox FAQ Assistant

## 2. Overview
The Upstox FAQ Assistant is a small, facts-only RAG-based chatbot designed to answer common questions about the Upstox trading and investment platform using only official public sources. The product helps retail investors, new users, and support teams understand platform features, account processes, charges, order types, fund flows, and reports without relying on unverified or private data.

The assistant must answer only factual, public-information questions and must refuse to provide investment advice, stock recommendations, or trading predictions.

## 3. Problem Statement
Users frequently need quick, reliable, and factual answers about platform features and operational processes on Upstox. However, information is scattered across official documents, help pages, FAQs, and regulatory sources. Users need a trustworthy and concise assistant that can answer questions like:

- What brokerage does Upstox charge for equity delivery?
- How can I open a Demat account?
- How do I add or withdraw funds?
- What is the difference between Market and Limit orders?
- What is a GTT order?
- How can I check my IPO application status?
- Where can I find my contract note or P&L report?

The system must provide answers grounded in official sources and must not provide personalized financial guidance or speculation.

## 4. Goals
- Create a working prototype FAQ assistant for Upstox-related factual questions.
- Answer questions using only official public sources from Upstox, SEBI, NSE, and BSE.
- Include at least one relevant source link in every answer.
- Keep responses brief, factual, and transparent.
- Implement a demonstrable RAG pipeline with staged, inspectable outputs.
- Support configurable LLM and vector search components.

## 5. Non-Goals
- Investment advice, stock recommendations, or trading predictions.
- Personalized portfolio suggestions.
- Return calculations or performance comparisons.
- Use of private app data, third-party blogs, or non-official sources.
- Storage or collection of PII such as PAN, Aadhaar, OTPs, account numbers, email addresses, phone numbers, or passwords.

## 6. Target Users
### 6.1 Retail Investors and Traders
People who need quick clarification on how Upstox features work, charges, orders, account functions, and reports.

### 6.2 New Users
Individuals learning how to onboard, open accounts, add funds, place orders, and navigate the platform.

### 6.3 Customer Support Teams
Teams handling repetitive platform-related questions who need a trustworthy internal FAQ assistant.

## 7. User Needs
- Quick and factual answers to platform-related questions.
- Clear citation links to official sources.
- Short answers that are easy to read.
- Confidence that the response is based on public, official information only.
- Protection from unsupported or risky financial or investment guidance.

## 8. Core Product Requirements
### 8.1 Data and Source Requirements
- Use only official public sources.
- Gather 15–25 source URLs from Upstox, SEBI, NSE, and BSE.
- Use no third-party blogs, no private app data, and no unverified sources.
- Store sources in a structured list for traceability and auditability.

### 8.2 FAQ Behavior
The assistant must answer factual questions such as:
- Brokerage charges for equity delivery
- Account opening and KYC
- Adding or withdrawing funds
- Difference between Market, Limit, SL, and SL-M orders
- GTT orders
- DP charges
- Margin shortfall
- Contract notes
- Profit and loss reports
- IPO application status
- Mutual fund SIP onboarding

### 8.3 Answer Constraints
- Every answer must include at least one relevant source link.
- Answers must be no longer than three sentences.
- Each answer must display: “Last updated from sources:”
- The system must clearly state when information is unavailable in the indexed sources.
- It must refuse investment advice and stock recommendations politely.

### 8.4 Safety and Compliance Requirements
- No PII collection or storage.
- No account authentication flows or personal data input.
- No recommendation of buy/sell actions or stock predictions.
- No personal portfolio advice.
- No unsupported factual claims.

## 9. User Experience Requirements
### 9.1 Tiny UI
The user interface must include:
- Welcome message: “Welcome to Upstox FAQ Assistant.”
- Three example questions
- Chat input field
- Answer display area
- Source link under every answer
- Disclaimer: “Facts-only. No investment or trading advice.”

### 9.2 Example Refusal Behavior
The system must respond with a safe refusal when asked for investment opinions, such as:
“I can explain Upstox features, charges and trading processes, but I cannot recommend whether you should buy or sell a stock. Please consult a qualified financial advisor for personalised investment decisions.”

## 10. RAG System Requirements
The project must be built in separate, demonstrable phases.

### 10.1 Phase 1: Data Loading
- Scrape official Upstox pages and related public sources.
- Save raw HTML/text and metadata.
- Maintain source provenance.

### 10.2 Phase 2: Data Cleaning
- Remove irrelevant content, navigation elements, duplicates, and noisy text.
- Produce cleaned text files ready for chunking.

### 10.3 Phase 3: Data Chunking
- Use a content-aware chunking strategy.
- Keep chunks semantically meaningful for retrieval.
- Store chunk metadata including source URL and chunk ID.

### 10.4 Phase 4: Data Embedding
- Use sentence-transformers/all-MiniLM-L6-v2.
- Generate embeddings for chunks.
- Save vectors and IDs in a structured format.

### 10.5 Phase 5: Vector Database
- Use ChromaDB.
- Persist chunk embeddings and metadata.
- Maintain a vector collection for retrieval.

### 10.6 Phase 6: Data Retrieval
- Use the same embedding model and ChromaDB collection used during ingestion.
- Retrieve relevant chunks using cosine similarity.
- Return similarity scores and metadata for each result.

### 10.7 Phase 7: LLM Generation
- Generate factual answers from retrieved context and the selected LLM.
- Ensure answers are concise, grounded, and cite sources.
- Provide model identity and source information in output metadata.

### 10.8 Phase 8: Evaluation
- Validate retrieval relevance.
- Check factual correctness.
- Test citation quality.
- Verify refusal behavior for financial advice requests.

## 11. Technical Requirements
### 11.1 Programming Language
- Python

### 11.2 UI
- Streamlit

### 11.3 Data Scraping
- Requests
- BeautifulSoup

### 11.4 Chunking
- Configurable content-aware strategy

### 11.5 Embedding Model
- sentence-transformers/all-MiniLM-L6-v2

### 11.6 Vector Database
- ChromaDB

### 11.7 Search Method
- Cosine similarity

### 11.8 LLM Providers
- Groq
- Gemini
- OpenAI
- Anthropic
- Mistral

### 11.9 LLM Config
- Default provider: Groq
- Default model: qwen/qwen3.8-27b (subject to provider availability)
- API keys and model names stored in .env
- Switching providers must not require code changes

## 12. Configurability Requirements
The system must be built with configuration-driven components rather than hardcoded implementation choices.

Required configurable elements:
- Embedding model
- Vector database settings
- LLM provider
- Model name
- API keys
- Retrieval settings
- Chunking strategy

## 13. Demonstration and Output Requirements
The project is a RAG demonstration, so each stage must produce separately stored output that can be inspected.

| Stage | Required Output |
| --- | --- |
| Data loading | Raw HTML/text and source metadata |
| Data cleaning | Cleaned text files |
| Chunking | Individual chunks in JSONL |
| Embedding | Embedding vectors and chunk IDs |
| Vector storage | Persistent ChromaDB collection |
| Retrieval | Retrieved chunks, similarity scores, and metadata |
| Generation | Final answer, source links, and model information |
| Evaluation | Test queries, expected answers, and actual results |

## 14. Deliverables
The final submission must include:
1. Working prototype link or local demo
2. Source list (CSV or Markdown) with 15–25 official URLs
3. README with setup instructions, scope, and known limitations
4. Sample Q&A file containing 5–10 query/answer examples with source links
5. Disclaimer snippet used in the UI
6. Stored intermediate outputs for each RAG phase
7. Configuration file demonstrating configurable embedding model, vector database, and LLM provider

## 15. Acceptance Criteria
The product is successful if all of the following are true:
- It answers platform-related factual questions using official public sources.
- Every answer contains a relevant source link.
- Answers are max three sentences.
- It displays the last updated source date.
- It refuses investment advice and stock recommendations safely.
- It clearly indicates when the answer cannot be supported by indexed sources.
- It uses a demonstrable end-to-end RAG pipeline with intermediate outputs.
- The model/provider configuration is externalized to environment-based settings.
- The prototype can be run locally or via a link.

## 16. Key Risks and Constraints
- Risk of using unverified external sources.
- Risk of generating unsupported factual answers.
- Need to avoid financial advice and regulated-content issues.
- Requirement for transparent citations and explicit source provenance.
- Need to keep answers concise without losing factual grounding.

## 17. Success Metrics
- Retrieval accuracy for relevant source chunks
- Factual correctness across test queries
- Citation quality and presence in each answer
- Refusal accuracy for investment advice prompts
- Clear end-to-end demonstration of all RAG stages

## 18. Summary
This project is a transparent, configurable, RAG-based FAQ assistant for Upstox that answers factual questions using only official public information. It is designed to be a safe, demonstration-ready tool for end users and support teams, while ensuring compliance with financial-content boundaries and clear source attribution.
