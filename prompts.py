from __future__ import annotations

SYSTEM_BRIEF = """You are NewsGenie, an AI news assistant.
You produce accurate, source-grounded news briefings.
Rules:
- Do NOT fabricate facts.
- If sources disagree, say so.
- Always cite the source URL after each bullet or paragraph.
- Keep it tight and readable.
"""

SUMMARIZE_ARTICLE = """Summarize the following news article for a busy professional.
Include:
- What happened (1-2 sentences)
- Why it matters (1 sentence)
- Key numbers or dates if present
- Mention uncertainty if the article is speculative
Return 3-5 bullet points.

TITLE: {title}
SOURCE: {source}
URL: {url}
EXCERPT: {excerpt}
"""

COMPOSE_BRIEFING = """Create a news briefing answering the user's query.

User query:
{query}

Mode:
{mode}

You have these article summaries (each includes a URL). Use them to answer.
- In brief mode: 5-8 bullets + 1 short synthesis paragraph.
- In deep mode: 10-14 bullets, then themes, then open questions.

Write clearly. No fluff. Always include the URL at the end of each bullet.

Summaries:
{summaries}
"""
