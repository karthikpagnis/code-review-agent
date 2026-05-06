"""
LangGraph orchestrator.
Defines the agent graph:  ingest → parallel analysis → aggregate → done.

State flows through the graph as a TypedDict.  The parallel_analysis node
fires all three specialist agents concurrently using asyncio.gather so the
overall review time is bounded by the slowest agent, not the sum of all.
"""

from __future__ import annotations

import asyncio
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

from app.agents.security   import run_security_agent
from app.agents.logic      import run_logic_agent
from app.agents.quality    import run_quality_agent
from app.agents.aggregator import build_report
from app.utils.github_fetcher import fetch_code_from_github, chunk_code
from app.schemas.models import ReviewReport


# ── Graph state ──────────────────────────────────────────────────────────────

class ReviewState(TypedDict):
    # Inputs
    github_url:   Optional[str]
    code_snippet: Optional[str]
    language:     str

    # Set by ingestion node
    raw_code:     str
    chunks:       list[str]
    filename:     str

    # Set by analysis node
    security_issues: list[dict]
    logic_issues:    list[dict]
    quality_issues:  list[dict]

    # Set by aggregation node
    report: Optional[ReviewReport]


# ── Nodes ────────────────────────────────────────────────────────────────────

async def ingest_node(state: ReviewState) -> ReviewState:
    """Fetch code from GitHub or use the provided snippet, then chunk it."""
    if state.get("github_url"):
        raw_code, filename = await fetch_code_from_github(state["github_url"])
    elif state.get("code_snippet"):
        raw_code  = state["code_snippet"]
        filename  = f"snippet.{state['language']}"
    else:
        raise ValueError("Either github_url or code_snippet must be provided.")

    chunks = chunk_code(raw_code, language=state["language"])

    return {**state, "raw_code": raw_code, "chunks": chunks, "filename": filename}


async def parallel_analysis_node(state: ReviewState) -> ReviewState:
    """
    Run security, logic, and quality agents concurrently on every chunk.
    Each agent is called once per chunk; results are flattened into one list.
    """
    chunks = state["chunks"]

    # Fire all agents across all chunks simultaneously
    sec_results, log_results, qual_results = await asyncio.gather(
        asyncio.gather(*[run_security_agent(c) for c in chunks]),
        asyncio.gather(*[run_logic_agent(c)    for c in chunks]),
        asyncio.gather(*[run_quality_agent(c)  for c in chunks]),
    )

    return {
        **state,
        "security_issues": [issue for chunk_issues in sec_results  for issue in chunk_issues],
        "logic_issues":    [issue for chunk_issues in log_results   for issue in chunk_issues],
        "quality_issues":  [issue for chunk_issues in qual_results  for issue in chunk_issues],
    }


async def aggregate_node(state: ReviewState) -> ReviewState:
    """Merge, deduplicate, and sort all findings into a final report."""
    report = build_report(
        security_issues=state["security_issues"],
        logic_issues=state["logic_issues"],
        quality_issues=state["quality_issues"],
        repo_url=state.get("github_url"),
        language=state["language"],
        chunks_analysed=len(state["chunks"]),
    )
    return {**state, "report": report}


# ── Graph compilation ────────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(ReviewState)

    g.add_node("ingest",   ingest_node)
    g.add_node("analyse",  parallel_analysis_node)
    g.add_node("aggregate", aggregate_node)

    g.set_entry_point("ingest")
    g.add_edge("ingest",    "analyse")
    g.add_edge("analyse",   "aggregate")
    g.add_edge("aggregate", END)

    return g.compile()


# Module-level compiled graph — import and call .ainvoke()
graph = build_graph()
