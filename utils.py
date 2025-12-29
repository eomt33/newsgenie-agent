from __future__ import annotations

import re
from datetime import datetime, timezone

def strip_html(text: str) -> str:
    # Simple, dependency-free HTML cleanup
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def iso_to_human(dt: str) -> str:
    # GDELT uses formats like 2025-12-28 13:45:00 or 2025-12-28T13:45:00Z
    if not dt:
        return ""
    try:
        if "T" in dt:
            d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        else:
            d = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return d.astimezone().strftime("%Y-%m-%d %H:%M")
    except Exception:
        return dt
