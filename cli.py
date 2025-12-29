from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv

from .graph import build_graph, NewsState

app = typer.Typer(add_completion=False)
console = Console()

@app.command()
def ask(
    query: str = typer.Argument(..., help="What you want to know."),
    mode: str = typer.Option("brief", help="brief or deep"),
    max_articles: int = typer.Option(8, help="How many articles to include in the final briefing."),
    days: int = typer.Option(7, help="How far back to search (days)."),
    save_json: Optional[Path] = typer.Option(None, "--save-json", help="Save retrieved/ranked/summaries to a JSON file."),
):
    """
    Ask NewsGenie a question and get a news briefing.
    """
    load_dotenv()

    mode = mode.strip().lower()
    if mode not in {"brief", "deep"}:
        raise typer.BadParameter("mode must be 'brief' or 'deep'")

    state = NewsState(query=query, mode=mode, max_articles=max_articles, days=days)
    graph = build_graph()
    result: NewsState = graph.invoke(state)

    if save_json:
        payload = {
            "query": result.query,
            "mode": result.mode,
            "retrieved_count": len(result.retrieved),
            "ranked": [
                {"title": a.title, "url": a.url, "domain": a.domain, "seendate": a.seendate}
                for a in result.ranked
            ],
            "summaries": result.summaries,
            "briefing": result.briefing,
        }
        save_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        console.print(f"[green]Saved[/green] details to {save_json}")

    console.print(Markdown(result.briefing or ""))

@app.command()
def doctor():
    """
    Quick environment check.
    """
    load_dotenv()
    import os
    keys = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
    }
    console.print("Environment:")
    for k, v in keys.items():
        console.print(f"  - {k}: {'✅ set' if v else '❌ not set'}")
    console.print("\nTip: copy .env.example → .env and set ONE key.")

if __name__ == "__main__":
    app()
