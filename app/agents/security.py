"""
Security analysis agent.
Runs against each code chunk and returns structured findings
covering OWASP Top 10 patterns, secrets, injection, and more.
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
You are an expert security code reviewer specialising in application security.

Analyse the provided code chunk for security vulnerabilities including:
- SQL / command / prompt injection risks
- Hardcoded secrets, API keys, passwords, or tokens
- Insecure use of eval(), exec(), or subprocess with shell=True
- Missing authentication or authorisation checks
- Insecure deserialization
- Path traversal vulnerabilities
- OWASP Top 10 patterns
- Missing input validation or sanitisation

Return ONLY a valid JSON object. Do not include markdown, backticks, or explanation.
The JSON must exactly match this schema:
{
  "issues": [
    {
      "severity": "high" | "medium" | "low",
      "type": "string — short issue name e.g. SQL Injection",
      "line_hint": "string — relevant line or lines from the code",
      "description": "string — what the vulnerability is and why it is dangerous",
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
    """Strip markdown fences if the model wraps output in ```json ... ```"""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


async def run_security_agent(code_chunk: str) -> list[dict]:
    """
    Send one code chunk to the security agent.
    Returns a list of finding dicts (may be empty).
    """
    if not code_chunk.strip():
        return []

    client = _get_client()
    agent = client.agents.create_agent(
        model=FOUNDRY_MODEL,
        name="security-reviewer",
        instructions=SYSTEM_PROMPT,
    )

    try:
        thread = client.agents.create_thread()
        client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=f"Review this code:\n\n```\n{code_chunk}\n```",
        )
        run = client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id,
        )
        messages = client.agents.list_messages(thread_id=thread.id)
        # Most recent assistant message is first
        for msg in messages.data:
            if msg.role == "assistant":
                for block in msg.content:
                    if isinstance(block, MessageTextContent):
                        result = _extract_json(block.text.value)
                        return result.get("issues", [])
    finally:
        # Always clean up the agent to avoid orphaned Foundry resources
        client.agents.delete_agent(agent.id)

    return []
