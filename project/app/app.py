import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import html
import re
from urllib.parse import urlparse

import streamlit as st

from modules.llm_client import generate_answer, is_guardrail_violation
from modules.retriever import retrieve_context

st.set_page_config(page_title="Upstox FAQ Assistant", page_icon="U", layout="centered")

SAMPLE_QUESTIONS = [
    ("％", "Brokerage & Charges", "What are the brokerage charges?"),
    ("▣", "Funds & Withdrawals", "How can I withdraw my funds?"),
    ("⇄", "Orders & Trading", "What is the difference between Market and Limit orders?"),
    ("▤", "Reports & Statements", "How can I download my contract note?"),
]

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    :root {
        --ink: #171b27;
        --muted: #64748b;
        --line: #e2e8f0;
        --paper: #ffffff;
        --canvas: #f6f8fc;
        --accent: #63319b;
        --accent-dark: #4f247f;
        --accent-soft: #f0eafa;
    }

    html, body, [class*="css"] {
        font-family: "DM Sans", "Segoe UI", sans-serif;
        color: var(--ink);
    }
    [data-testid="stAppViewContainer"] { background: var(--canvas); }
    [data-testid="stHeader"] { background: var(--canvas); }
    [data-testid="stMain"] { background: var(--canvas); }
    [data-testid="stMainBlockContainer"] {
        max-width: 860px;
        padding-top: 2rem;
        padding-bottom: 5.5rem;
    }
    .topbar {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 18px 4px 20px;
        border-bottom: 1px solid var(--line);
        background: var(--paper);
    }
    .brand-name {
        color: var(--accent);
        font-size: 23px;
        font-weight: 700;
        letter-spacing: 0;
    }
    .brand-divider { width: 1px; height: 38px; background: var(--line); }
    .brand-copy { display: flex; flex-direction: column; gap: 2px; }
    .brand-copy strong { font-size: 19px; line-height: 1.2; }
    .brand-copy span { color: var(--muted); font-size: 14px; }
    .hero { text-align: center; padding: 72px 10px 42px; }
    .hero h1 { font-size: 38px; line-height: 1.2; margin: 0 0 14px; letter-spacing: 0; }
    .hero p { color: #55586a; font-size: 18px; line-height: 1.55; margin: 0 auto; max-width: 620px; }
    .section-label { color: var(--muted); font-size: 13px; font-weight: 600; margin: 0 0 10px; }
    [data-testid="stHorizontalBlock"] { gap: 14px; }
    .stButton > button {
        min-height: 118px;
        height: auto;
        width: 100%;
        padding: 17px 18px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--paper);
        color: var(--ink);
        box-shadow: 0 1px 2px rgba(20, 30, 50, .04);
        text-align: left;
        white-space: pre-wrap;
        line-height: 1.55;
        transition: border-color .16s ease, box-shadow .16s ease, transform .16s ease;
    }
    .stButton > button:hover {
        border-color: #bca3d8;
        box-shadow: 0 5px 16px rgba(49, 32, 71, .08);
        color: var(--ink);
        transform: translateY(-1px);
    }
    .stButton > button:focus-visible { outline: 3px solid #cdb8e6; outline-offset: 2px; }
    [data-testid="stChatInput"] { max-width: 820px; margin: 12px auto 0; }
    [data-testid="stChatInput"] textarea {
        border-color: var(--line);
        border-radius: 10px;
        background: var(--paper);
        font-family: "DM Sans", "Segoe UI", sans-serif;
    }
    [data-testid="stChatInput"] button {
        background: var(--accent);
        border-radius: 8px;
    }
    [data-testid="stChatInput"] button:hover { background: var(--accent-dark); }
    [data-testid="stChatMessage"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: var(--paper);
        padding: 16px 18px;
    }
    .user-message [data-testid="stChatMessage"] { background: var(--accent); color: white; }
    .source-label { color: var(--muted); font-size: 13px; font-weight: 600; margin: 14px 0 8px; }
    .source-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        padding: 13px 15px;
        margin: 8px 0;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #f9fafc;
        color: var(--ink);
        text-decoration: none !important;
    }
    .source-card:hover { border-color: #bca3d8; background: var(--paper); }
    .source-card small { display: block; color: var(--muted); font-size: 12px; margin-top: 3px; }
    .source-arrow { color: var(--accent); font-size: 18px; }
    .disclaimer { color: var(--muted); text-align: center; font-size: 13px; padding: 22px 4px 8px; }
    .new-chat-row { display: flex; justify-content: flex-end; margin: 8px 0 18px; }
    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding: 2rem 1rem 5rem; }
        .topbar { gap: 11px; padding: 16px 2px; }
        .brand-name { font-size: 20px; }
        .brand-copy strong { font-size: 16px; }
        .brand-copy span { font-size: 13px; }
        .hero { padding: 54px 2px 30px; }
        .hero h1 { font-size: 29px; }
        .hero p { font-size: 16px; }
        [data-testid="stHorizontalBlock"] { flex-direction: column; gap: 10px; }
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        .stButton > button { min-height: 96px; padding: 14px 15px; }
        [data-testid="stChatMessage"] { padding: 13px 14px; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_header() -> None:
    st.markdown(
        """
        <div class="topbar">
            <div class="brand-name">upstox</div>
            <div class="brand-divider"></div>
            <div class="brand-copy">
                <strong>Upstox FAQ Assistant</strong>
                <span>Your platform guide</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def answer_question(question: str) -> dict:
    context_items = []
    if not is_guardrail_violation(question):
        context_items = retrieve_context(question, top_k=3)

    answer = generate_answer(question, context_items=context_items)
    sources = []
    seen_urls = set()
    for item in context_items:
        url = item.get("url", "")
        if url and url not in seen_urls:
            sources.append(item)
            seen_urls.add(url)

    updated_match = re.search(r"Last updated from sources:\s*([^\n.]+)", answer)
    updated = updated_match.group(1).strip() if updated_match else "Date not provided"
    return {"answer": answer, "sources": sources, "updated": updated}


def render_sources(sources: list) -> None:
    if not sources:
        return

    st.markdown('<div class="source-label">Official sources</div>', unsafe_allow_html=True)
    for source in sources:
        url = source.get("url", "")
        if not url:
            continue
        title = html.escape(str(source.get("title") or "Official source"))
        safe_url = html.escape(url, quote=True)
        host = html.escape(urlparse(url).hostname or url)
        st.markdown(
            f'<a class="source-card" href="{safe_url}" target="_blank" rel="noopener noreferrer">'
            f'<span><strong>{title}</strong><small>{host}</small></span>'
            '<span class="source-arrow" aria-hidden="true">↗</span></a>',
            unsafe_allow_html=True,
        )


def render_messages(messages: list) -> None:
    for message in messages:
        role = message["role"]
        with st.chat_message(role):
            st.markdown(message["content"])
            if role == "assistant":
                render_sources(message.get("sources", []))
                st.caption(f"Last updated from sources: {message.get('updated', 'Date not provided')}")


if "messages" not in st.session_state:
    st.session_state.messages = []

render_header()
messages = st.session_state.messages
question_to_submit = None

if not messages:
    st.markdown(
        """
        <section class="hero">
            <h1>How can we help you today?</h1>
            <p>Ask us anything about Upstox. Get simple answers backed by official sources.</p>
        </section>
        <p class="section-label">POPULAR QUESTIONS</p>
        """,
        unsafe_allow_html=True,
    )
    for row_start in (0, 2):
        columns = st.columns(2)
        for column, item in zip(columns, SAMPLE_QUESTIONS[row_start:row_start + 2]):
            icon, category, sample_question = item
            with column:
                if st.button(
                    f"{icon}  **{category}**\n\n{sample_question}",
                    key=f"sample_{row_start}_{category}",
                    use_container_width=True,
                ):
                    question_to_submit = sample_question
else:
    if st.button("← New conversation", key="new_conversation"):
        st.session_state.messages = []
        st.rerun()
    render_messages(messages)

st.markdown('<div class="disclaimer">Facts-only. No investment or trading advice.</div>', unsafe_allow_html=True)
typed_question = st.chat_input("Type your question here...")
if typed_question:
    question_to_submit = typed_question

if question_to_submit:
    with st.spinner("Checking official sources..."):
        response = answer_question(question_to_submit)
    st.session_state.messages.extend(
        [
            {"role": "user", "content": question_to_submit},
            {
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"],
                "updated": response["updated"],
            },
        ]
    )
    st.rerun()
