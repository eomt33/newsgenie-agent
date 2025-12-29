from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

from .llm import get_llm
from .prompts import SYSTEM_BRIEF, SUMMARIZE_ARTICLE, COMPOSE_BRIEFING
from .tools.gdelt import fetch_gdelt_articles, Article
from .utils import iso_to_human

@dataclass
class NewsState:
    query: str
    mode: str = "brief"
    days: int = 7
    max_articles: int = 8

    # populated along the graph
    retrieved: List[Article] = field(default_factory=list)
    ranked: List[Article] = field(default_factory=list)
    summaries: List[Dict[str, Any]] = field(default_factory=list)
    briefing: Optional[str] = None

def retrieve_news(state: NewsState) -> NewsState:
    state.retrieved = fetch_gdelt_articles(
        query=state.query,
        days_back=state.days,
        max_records=max(25, state.max_articles * 4),
    )
    return state

def rank_articles(state: NewsState) -> NewsState:
    """
    Simple relevance + diversity ranking:
    - Prefer distinct domains
    - Prefer more recent (seendate)
    - Use GDELT's provided summary length as a weak quality signal
    """
    # Sort by seendate desc (string sort works for ISO-ish formats)
    items = sorted(state.retrieved, key=lambda a: (a.seendate or ""), reverse=True)

    seen_domains = set()
    ranked: List[Article] = []
    # first pass: unique domains
    for a in items:
        if a.domain and a.domain not in seen_domains:
            ranked.append(a)
            seen_domains.add(a.domain)
        if len(ranked) >= state.max_articles:
            break

    # second pass: fill remaining
    if len(ranked) < state.max_articles:
        for a in items:
            if a not in ranked:
                ranked.append(a)
            if len(ranked) >= state.max_articles:
                break

    state.ranked = ranked
    return state

def summarize_articles(state: NewsState) -> NewsState:
    llm = get_llm()
    if llm is None:
        # No key: degrade gracefully with excerpt-only "summaries"
        state.summaries = [
            {
                "title": a.title,
                "url": a.url,
                "source": a.domain,
                "when": iso_to_human(a.seendate),
                "bullets": [
                    (a.summary or "No summary provided by the feed. Set an LLM key to generate summaries.")
                ],
            }
            for a in state.ranked
        ]
        return state

    summaries = []
    for a in state.ranked:
        prompt = SUMMARIZE_ARTICLE.format(
            title=a.title,
            source=a.domain,
            url=a.url,
            excerpt=(a.summary or "")[:1500],
        )
        msgs = [SystemMessage(content=SYSTEM_BRIEF), HumanMessage(content=prompt)]
        out = llm.invoke(msgs).content
        summaries.append(
            {
                "title": a.title,
                "url": a.url,
                "source": a.domain,
                "when": iso_to_human(a.seendate),
                "summary_text": out.strip(),
            }
        )
    state.summaries = summaries
    return state

def compose_briefing(state: NewsState) -> NewsState:
    llm = get_llm()
    # If no LLM, just stitch together sources
    if llm is None:
        lines = [f"NewsGenie briefing (no LLM configured) for: {state.query}", ""]
        for s in state.summaries:
            lines.append(f"- {s['title']} ({s['source']}, {s['when']}): {s['url']}")
        state.briefing = "\n".join(lines)
        return state

    summaries_block = "\n\n".join(
        [
            f"TITLE: {s['title']}\nWHEN: {s.get('when','')}\nSOURCE: {s['source']}\nURL: {s['url']}\nSUMMARY:\n{s['summary_text']}"
            for s in state.summaries
        ]
    )
    prompt = COMPOSE_BRIEFING.format(query=state.query, mode=state.mode, summaries=summaries_block)
    msgs = [SystemMessage(content=SYSTEM_BRIEF), HumanMessage(content=prompt)]
    out = llm.invoke(msgs).content
    state.briefing = out.strip()
    return state

def build_graph():
    g = StateGraph(NewsState)
    g.add_node("retrieve_news", retrieve_news)
    g.add_node("rank_articles", rank_articles)
    g.add_node("summarize_articles", summarize_articles)
    g.add_node("compose_briefing", compose_briefing)

    g.set_entry_point("retrieve_news")
    g.add_edge("retrieve_news", "rank_articles")
    g.add_edge("rank_articles", "summarize_articles")
    g.add_edge("summarize_articles", "compose_briefing")
    g.add_edge("compose_briefing", END)

    return g.compile()
