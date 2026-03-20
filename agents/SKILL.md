---
name: LexSimple Agent Orchestration
description: Multi-agent LangGraph pipeline for legal document analysis using Google Gemini models
---

# LexSimple Agent Orchestration

## Overview
LexSimple uses a **LangGraph StateGraph** with 9 specialized agents powered by Google Gemini models.
Each agent lives in its own module under `agents/` and follows a consistent interface.

## Agent Inventory

| Agent | Model | Role |
|-------|-------|------|
| **Classifier** | Gemini Flash Lite | Detect doc type, jurisdiction, party roles |
| **Simplifier** | Gemini Flash Lite | Plain-English rewrites at 9th-grade level |
| **Risk Scanner** | Gemini Flash | ReAct loop for risk flag detection |
| **Extractor** | Gemini Flash Lite | Structured fact extraction |
| **Comparator** | Gemini Flash | Benchmark flagged clauses against market norms |
| **Report Builder** | Gemini Flash | Synthesize all agent outputs into final report |
| **Q&A Agent** | Gemini Flash | Conversational doc Q&A with clause citations |
| **Draft Generator** | Gemini Flash | Generate revised clause language on demand |
| **Orchestrator** | — | LangGraph graph definition and state management |

## Architecture

```
agents/
├── SKILL.md                  # This file
├── orchestrator/
│   ├── graph.py              # LangGraph StateGraph definition
│   └── state.py              # LexSimpleState TypedDict
├── classifier/
│   ├── agent.py              # Classifier agent function
│   └── prompts.py            # System/user prompt templates
├── simplifier/
│   ├── agent.py
│   └── prompts.py
├── risk_scanner/
│   ├── agent.py              # ReAct loop implementation
│   ├── prompts.py
│   └── taxonomy.py           # Risk flag taxonomy definitions
├── extractor/
│   ├── agent.py
│   └── prompts.py
├── comparator/
│   ├── agent.py
│   └── prompts.py
├── report_builder/
│   ├── agent.py
│   └── prompts.py
├── qa_agent/
│   ├── agent.py
│   └── prompts.py
├── draft_generator/
│   ├── agent.py
│   └── prompts.py
├── tools/
│   ├── tool_schemas.py       # JSON schemas for all function-calling tools
│   ├── rag.py                # Agentic RAG: MemoryVectorStore setup & retrieval
│   └── parsers.py            # PDF/DOCX text extraction utilities
└── config/
    ├── models.py             # Model name constants & OpenRouter client setup
    └── prompts.py            # Master system prompt (Section 7 of PRD)
```

## How to Add a New Agent
1. Create a new folder under `agents/` with the agent name (snake_case)
2. Add `agent.py` — must export a function with signature `def run(state: LexSimpleState) -> dict`
3. Add `prompts.py` — must export `SYSTEM_PROMPT` and optionally `USER_PROMPT_TEMPLATE`
4. Register the node in `orchestrator/graph.py`
5. Add edges to connect it in the pipeline

## Model Routing
- **Fast tasks** (Classifier, Simplifier, Extractor): Use `gemini-2.5-flash-lite`
- **Reasoning tasks** (Risk Scanner, Comparator, Report Builder, Q&A, Draft Gen): Use `gemini-2.5-flash`
- All models accessed via OpenRouter API (`https://openrouter.ai/api/v1`)
