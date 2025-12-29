from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import os
import requests

from ..utils import strip_html

GDELT_DOC_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"

@dataclass
class Article:
    title: str
    url: str
    domain: str
    seendate: str
    source_country: Optional[str] = None
    language: Optional[str] = None
    summary: Optional[str] = None
    tone: Optional[float] = None

def fetch_gdelt_articles(query: str, days_back: int = 7, max_records: int = 25, timeout: int = 20) -> List[Article]:
    """
    Fetch articles from the GDELT 2.1 DOC API.
    No API key required.

    We use mode=ArtList because it returns a list of articles with metadata.
    """
    max_records = max(1, min(int(max_records), 250))
    days_back = max(1, min(int(days_back), 30))

    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": max_records,
        "timelinesmooth": 0,
        "formatdatetime": 1,
        # last X days: using "query" operators is possible; simplest is to rely on GDELT defaults + small days window.
        # DOC API supports "startdatetime" and "enddatetime" but can be finicky; for portfolio, keep robust.
    }

    # Optional env overrides
    params["maxrecords"] = int(os.getenv("GDELT_MAXRECORDS", params["maxrecords"]))

    r = requests.get(GDELT_DOC_ENDPOINT, params=params, timeout=timeout)
    r.raise_for_status()
    data: Dict[str, Any] = r.json()

    articles: List[Article] = []
    for item in (data.get("articles") or []):
        url = item.get("url") or ""
        title = item.get("title") or ""
        domain = item.get("domain") or ""
        seendate = item.get("seendate") or ""
        source_country = item.get("sourceCountry")
        language = item.get("language")
        # 'socialimage' etc exist, but we keep minimal
        summary = strip_html(item.get("summary") or "") if item.get("summary") else None
        tone = item.get("tone")
        if url and title:
            articles.append(
                Article(
                    title=title.strip(),
                    url=url.strip(),
                    domain=domain.strip(),
                    seendate=seendate,
                    source_country=source_country,
                    language=language,
                    summary=summary,
                    tone=tone if isinstance(tone, (int, float)) else None,
                )
            )
    return articles
