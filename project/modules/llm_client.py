import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from config import GROQ_API_KEY, LLM_MODEL, LLM_PROVIDER
from modules.retriever import retrieve_context


def is_guardrail_violation(question: str) -> bool:
    text = question.lower()
    risky_patterns = [
        "should i buy",
        "should i sell",
        "which stock should i buy",
        "which stock should i sell",
        "stock prediction",
        "will it rise",
        "will it fall",
        "recommend a stock",
        "buy now",
        "sell now",
        "best stock",
        "tomorrow's stock",
        "trading signal",
    ]

    if any(pattern in text for pattern in risky_patterns):
        return True

    return bool(re.search(r"\b(buy|sell|recommend|prediction|portfolio|signal)\b", text))


def build_prompt(question: str, context_snippets: List[str]) -> str:
    context = "\n\n".join(context_snippets[:3])
    return (
        "You are an Upstox FAQ assistant. Use only the official source context provided below. "
        "Answer in at most 3 sentences. Every answer must include a source link. "
        "Add the exact text 'Last updated from sources: <date>' at the end of the answer. "
        "Do not provide stock recommendations, buy/sell advice, trading forecasts, or investment tips. "
        "If the answer is not available in the context, say that it is unavailable in the indexed official sources.\n\n"
        f"Question: {question}\n\nContext:\n{context}"
    )


def call_groq(prompt: str, model: str = LLM_MODEL) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a factual Upstox assistant. Follow the instructions strictly."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 250,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def generate_answer(
    question: str,
    context_items: Optional[List[Dict[str, Any]]] = None,
) -> str:
    if not question or not question.strip():
        return "Please enter a question about Upstox, NSE, BSE, or SEBI official information."

    if is_guardrail_violation(question):
        return (
            "I can only answer factual questions from official Upstox, NSE, BSE, and SEBI sources. "
            "I cannot provide buy/sell recommendations, trading signals, or stock predictions."
        )

    if context_items is None:
        context_items = retrieve_context(question, top_k=3)
    if not context_items:
        return "I could not find this in the indexed official sources."

    snippets = [item["document"] for item in context_items]
    sources = [item["url"] for item in context_items if item.get("url")]
    source_text = " | ".join(sources[:3]) if sources else "https://upstox.com/faq/"

    if LLM_PROVIDER.lower() == "groq" and GROQ_API_KEY:
        try:
            answer = call_groq(build_prompt(question, snippets))
            if answer:
                return answer if "Last updated from sources:" in answer else f"{answer} Last updated from sources: {datetime.utcnow().strftime('%Y-%m-%d')}."
        except Exception:
            pass

    top_context = snippets[0]
    summary = top_context[:500].strip()
    answer = (
        f"Based on the official sources, {summary}. "
        f"Source: {source_text}."
    )
    return f"{answer} Last updated from sources: {datetime.utcnow().strftime('%Y-%m-%d')}."
