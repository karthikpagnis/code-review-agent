"""
Logic and bug analysis agent.
Detects runtime errors, logical mistakes, and edge case failures.
"""

import json
import os
import re

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MessageTextContent
from azure.identity import DefaultAzureCredential

FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT", "")
FOUNDRY_MODEL    = os.getenv("FOUNDRY_MODEL", "gpt-4o")

SYSTEM_PROMPT = """
You are an expert software engineer specialising in code correctness and bug detection.

Analyse the provided code chunk for logic errors and runtime issues including:
- Off-by-one errors in loops or slices
- Null / None dereference risks
- Unhandled exceptions and bare except clauses
- Incorrect use of mutable default arguments
- Race conditions or shared state issues
- Unreachable code paths
- Incorrect boolean logic or short-circuit evaluation
- Resource leaks (files, connections not closed)
- Incorrect type assumptions

Return ONLY a valid JSON object. Do not include markdown, backticks, or explanation.
The JSON must exactly match this schema:
{
  "issues": [
    {
      "severity": "high" | "medium" | "low",
      "type": "string — short issue name e.g. Bare except clause",
      "line_hint": "string — relevant line or lines from the code",
      "description": "string — what the bug is and what could go wrong at runtime",
      "suggestion": "string — concrete fix recommendation"
    }
  ]
}

If no issues are found, return: {"issues": []}
"""


def _get_client() -> AIProjectClient:
    return AIProjectClient(
        endpoint=FOUNDRY_ENDPOINT,
        credential=DefaultAzureCredential(),
    )


def _extract_json(raw: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


async def run_logic_agent(code_chunk: str) -> list[dict]:
    """
    Send one code chunk to the logic/bug agent.
    Returns a list of finding dicts (may be empty).
    """
    if not code_chunk.strip():
        return []

    client = _get_client()
    agent = client.agents.create_agent(
        model=FOUNDRY_MODEL,
        name="logic-reviewer",
        instructions=SYSTEM_PROMPT,
    )

    try:
        thread = client.agents.create_thread()
        client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=f"Review this code:\n\n```\n{code_chunk}\n```",
        )
        client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        messages = client.agents.list_messages(thread_id=thread.id)
        for msg in messages.data:
            if msg.role == "assistant":
                for block in msg.content:
                    if isinstance(block, MessageTextContent):
                        result = _extract_json(block.text.value)
                        return result.get("issues", [])
    finally:
        client.agents.delete_agent(agent.id)

    return []
