from __future__ import annotations

import os
from typing import Optional

def get_llm():
    """
    Returns a LangChain chat model instance if an API key is available.
    Supports:
      - OpenAI (OPENAI_API_KEY)
      - Groq (GROQ_API_KEY)
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if openai_key:
        try:
            from langchain_openai import ChatOpenAI
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return ChatOpenAI(model=model, temperature=0.2)
        except Exception as e:
            raise RuntimeError(
                "OPENAI_API_KEY is set, but langchain-openai is not installed or failed to load. "
                "Install requirements.txt and try again."
            ) from e

    if groq_key:
        try:
            from langchain_groq import ChatGroq
            model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
            return ChatGroq(model=model, temperature=0.2)
        except Exception as e:
            raise RuntimeError(
                "GROQ_API_KEY is set, but langchain-groq is not installed or failed to load. "
                "Install requirements.txt and try again."
            ) from e

    return None
