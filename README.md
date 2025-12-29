# NewsGenie Agent

An agentic AI system for real-time news retrieval, ranking, and summarization using LangGraph, GDELT, and LLM-based synthesis.

## Overview
NewsGenie is designed to autonomously gather global news signals, reason over them, and produce structured, human-readable summaries.  
The system integrates external data sources with an agentic control flow to support exploratory analysis, trend detection, and narrative synthesis.

## Key Capabilities
- Real-time news ingestion via GDELT
- Agentic reasoning and control flow using LangGraph
- LLM-based summarization and synthesis
- Modular pipeline for retrieval, reasoning, and output
- CLI-based interaction for flexible querying

## System Architecture
The system follows a multi-stage agent pipeline:
1. Data ingestion and filtering (GDELT)
2. Graph-based agent orchestration
3. Prompt-driven reasoning and summarization
4. Structured output generation

## Repository Structure
newsgenie-agent/
│── cli.py
│── gdelt.py
│── graph.py
│── llm.py
│── prompts.py
│── utils.py
│── requirements.txt
│── README.md
│── LICENSE

## Design Decisions
- **Agentic control flow:** LangGraph is used to explicitly model reasoning steps rather than relying on a single prompt call.
- **Modular components:** Ingestion, reasoning, and synthesis are separated for extensibility and testing.
- **External data grounding:** GDELT provides real-world signals to reduce hallucination and improve relevance.
- **Prompt templating:** Prompts are centralized to support iteration and evaluation.
