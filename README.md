# Code Review Agent

A multi-agent code review system built on **Azure AI Foundry**, **LangGraph**, and **FastAPI**.  
Submit a public GitHub file URL or paste code directly — three specialist AI agents run in parallel
to analyse security vulnerabilities, logic bugs, and code quality issues, then merge their
findings into a structured JSON report persisted to Azure Blob Storage.

Authentication is handled by **Azure Entra ID** (OAuth2) — users sign in with their Microsoft
account before submitting any code.

---

## Architecture

```
Browser (MSAL.js login)
    │
    ▼ Bearer JWT
FastAPI  ──── Entra ID JWT validation
    │
    ▼ LangGraph graph
Orchestrator
    │
    ▼
Ingestion agent  ──  fetch GitHub URL / chunk code by function/class
    │
    ▼ (parallel, asyncio.gather)
┌──────────────┬──────────────┬──────────────┐
│ Security     │ Logic/Bug    │ Quality      │
│ agent        │ agent        │ agent        │
│ (OWASP,      │ (null refs,  │ (docs,       │
│  secrets,    │  exceptions, │  naming,     │
│  injection)  │  race conds) │  complexity) │
└──────────────┴──────────────┴──────────────┘
    │
    ▼
Aggregator agent  ──  deduplicate, severity-sort
    │
    ▼
Azure Blob Storage (JSON report)
    │
    ▼
JSON response → browser renders report table
```

---

## Tech stack

| Component          | Technology                              |
|--------------------|-----------------------------------------|
| Agent runtime      | Azure AI Foundry Agent SDK              |
| Agent graph        | LangGraph                               |
| Authentication     | Azure Entra ID + MSAL.js + python-jose  |
| API layer          | FastAPI + Uvicorn                       |
| Code ingestion     | httpx + Python AST                      |
| Report storage     | Azure Blob Storage                      |
| LLM               | GPT-4o (via Azure AI Foundry)           |
| Frontend           | Plain HTML + MSAL.js                    |

---

## Project structure

```
code-review-agent/
├── app/
│   ├── main.py                  # FastAPI entry point + CORS + static files
│   ├── auth.py                  # Entra ID JWT validation (Depends)
│   ├── routers/
│   │   └── review.py            # POST /api/review, GET /api/review/{id}
│   ├── agents/
│   │   ├── orchestrator.py      # LangGraph graph definition
│   │   ├── security.py          # Security analysis agent
│   │   ├── logic.py             # Logic/bug analysis agent
│   │   ├── quality.py           # Code quality agent
│   │   └── aggregator.py        # Dedup + merge + report builder
│   ├── schemas/
│   │   └── models.py            # Pydantic request/response models
│   └── utils/
│       ├── github_fetcher.py    # GitHub URL → raw code + AST chunking
│       └── blob_storage.py      # Azure Blob upload/download
├── frontend/
│   └── index.html               # MSAL login + review form + report table
├── infra/
│   └── azure_setup.md           # Step-by-step Azure resource creation guide
├── .env.example                 # Environment variable template
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Complete Azure setup

Follow **`infra/azure_setup.md`** to create all required Azure resources.  
This takes ~45 minutes the first time. You will collect:

- `TENANT_ID` and `CLIENT_ID` from Entra ID app registration
- `CLIENT_SECRET` from Entra ID
- `FOUNDRY_ENDPOINT` from Azure AI Foundry project
- `AZURE_STORAGE_CONNECTION_STRING` from Blob Storage

### 2. Clone and install

```bash
git clone <your-repo-url>
cd code-review-agent

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Open .env and fill in all values from Step 1
```

### 4. Update frontend credentials

Open `frontend/index.html` and replace the three placeholders:

```javascript
clientId:  "YOUR_CLIENT_ID",
authority: "https://login.microsoftonline.com/YOUR_TENANT_ID",
// and in scopes:
"api://YOUR_CLIENT_ID/review.read"
```

### 5. Run the server

```bash
# Make sure you're logged into Azure CLI (for DefaultAzureCredential)
az login

uvicorn app.main:app --reload --port 8000
```

Open your browser at **http://localhost:8000**

---

## Usage

1. Click **Sign in with Microsoft** — log in with your Azure/Microsoft account
2. Paste a public GitHub file URL, e.g.:
   ```
   https://github.com/karthikpagnis/PolicyPilot/blob/main/main.py
   ```
   Or paste code directly into the text area
3. Select the language and click **Run review**
4. Wait 20–40 seconds — three agents run in parallel
5. The report renders as a colour-coded table: High / Medium / Low findings with descriptions and fix suggestions
6. The full report is saved to Azure Blob Storage and the URL is shown at the bottom

---

## API reference

The FastAPI auto-generates interactive docs at **http://localhost:8000/docs**

### POST /api/review

Submit code for review. Requires Bearer token from Entra ID.

**Request body:**
```json
{
  "github_url": "https://github.com/user/repo/blob/main/app.py",
  "language": "python"
}
```
Or use `code_snippet` instead of `github_url`.

**Response:**
```json
{
  "status": "success",
  "report": {
    "review_id": "uuid",
    "total_issues": 7,
    "high_count": 2,
    "medium_count": 3,
    "low_count": 2,
    "findings": [
      {
        "severity": "high",
        "category": "security",
        "type": "Hardcoded API key",
        "line_hint": "API_KEY = 'sk-abc123...'",
        "description": "API key is hardcoded in source code...",
        "suggestion": "Move to environment variable and use os.getenv()"
      }
    ],
    "blob_url": "https://codereviewstorage.blob.core.windows.net/reports/...",
    "reviewed_at": "2026-05-06T12:00:00Z"
  }
}
```

### GET /api/review/{review_id}

Retrieve a previously stored report by ID.

### GET /health

Returns `{"status": "ok"}` — use for uptime checks.

---

## Running without Azure (dev/test mode)

If you want to test the FastAPI routes without real Azure credentials, you can temporarily
bypass auth and swap the Foundry agents for a mock:

```python
# In app/auth.py — replace get_current_user with:
async def get_current_user():
    return {"preferred_username": "dev@local"}

# In each agent file — replace the Foundry call with:
async def run_security_agent(code_chunk: str) -> list[dict]:
    return [{"severity": "low", "type": "Mock finding",
             "line_hint": "line 1", "description": "Mock", "suggestion": "Mock"}]
```

Revert before committing.

---

## Troubleshooting

**`DefaultAzureCredential` fails:**  
Run `az login` in your terminal. The credential chain reads from the CLI session.

**JWT validation fails (401):**  
Check that your `CLIENT_ID` and `TENANT_ID` in `.env` match what is in `frontend/index.html`.

**Foundry agent returns empty:**  
Check that your GPT-4o deployment name in Azure AI Foundry matches `FOUNDRY_MODEL` in `.env`.

**Blob upload fails (non-fatal warning in logs):**  
Check `AZURE_STORAGE_CONNECTION_STRING` and that the `reports` container exists.

**GitHub fetch returns 404:**  
The repo must be public. URL format must be `github.com/user/repo/blob/branch/path/file.py`.

---

## Resume context

This project demonstrates:
- Azure AI Foundry Agent SDK (multi-agent creation, thread management, cleanup)
- LangGraph for stateful agent graph orchestration with parallel nodes
- Azure Entra ID OAuth2 authentication wired into FastAPI via JWT validation
- Parallel async agent execution (`asyncio.gather`)
- Azure Blob Storage for report persistence
- AST-based code chunking for Python files
- Pydantic schema validation at every service boundary
- FastAPI with dependency injection for auth

Built independently as a portfolio project using Azure student credits ($100).
