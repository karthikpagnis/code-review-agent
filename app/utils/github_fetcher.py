"""
Fetch code from a public GitHub URL and chunk it into reviewable pieces.

Supports:
  - Single file URLs  (github.com/user/repo/blob/branch/path/file.py)
  - Raw URLs          (raw.githubusercontent.com/...)
  - Direct code paste (passed as string, no fetch needed)
"""

import ast
import httpx
from urllib.parse import urlparse


def github_to_raw(url: str) -> str:
    """Convert a github.com blob URL to its raw.githubusercontent.com equivalent."""
    url = url.strip()
    if "raw.githubusercontent.com" in url:
        return url
    # github.com/user/repo/blob/branch/path → raw.githubusercontent.com/user/repo/branch/path
    parsed = urlparse(url)
    parts = parsed.path.lstrip("/").split("/")
    # parts: [user, repo, "blob", branch, *filepath]
    if len(parts) >= 4 and parts[2] == "blob":
        raw_path = "/".join([parts[0], parts[1]] + parts[3:])
        return f"https://raw.githubusercontent.com/{raw_path}"
    raise ValueError(
        f"Cannot convert to raw URL: {url}\n"
        "Expected format: https://github.com/user/repo/blob/branch/path/file.py"
    )


async def fetch_code_from_github(url: str) -> tuple[str, str]:
    """
    Fetch source code from a public GitHub file URL.
    Returns (code: str, filename: str)
    """
    raw_url = github_to_raw(url)
    filename = raw_url.split("/")[-1]

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(raw_url)
        if response.status_code == 404:
            raise ValueError(f"File not found at: {raw_url}\nMake sure the repo is public.")
        response.raise_for_status()
        return response.text, filename


def chunk_python_by_definitions(code: str) -> list[str]:
    """
    Split Python code at function and class boundaries using the AST.
    Falls back to size-based chunking if the file is not valid Python.
    """
    try:
        tree = ast.parse(code)
        lines = code.splitlines()
        chunks = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = node.end_lineno
                chunk = "\n".join(lines[start:end])
                if chunk.strip():
                    chunks.append(chunk)
        # If no top-level definitions found, return whole file as one chunk
        return chunks if chunks else [code]
    except SyntaxError:
        # Non-Python or unparseable file — use size-based splitting
        return size_based_chunks(code)


def size_based_chunks(code: str, max_chars: int = 2500) -> list[str]:
    """Fallback: split code into chunks of max_chars, breaking at newlines."""
    chunks = []
    while len(code) > max_chars:
        split_at = code.rfind("\n", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        chunks.append(code[:split_at])
        code = code[split_at:].lstrip("\n")
    if code.strip():
        chunks.append(code)
    return chunks


def chunk_code(code: str, language: str = "python") -> list[str]:
    """
    Entry point. Dispatch to the right chunking strategy based on language.
    Currently uses AST-based chunking for Python, size-based for everything else.
    """
    if language.lower() == "python":
        return chunk_python_by_definitions(code)
    return size_based_chunks(code)
