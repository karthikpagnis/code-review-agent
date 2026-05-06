# Azure Setup Guide — Web Portal (No CLI)

Complete these steps using only the **Azure Portal** website. No command-line required.
Total time: ~50 minutes. Cost: well within the $100 student credit.

---

## Prerequisites

- Azure account: https://portal.azure.com
- Python 3.11+
- Web browser

---

## Step 1 — Create a resource group

1. Go to: **Azure Portal** → https://portal.azure.com
2. Sign in with your Microsoft account
3. Search for **"Resource groups"** in the top search bar
4. Click **"Create"**
   - **Subscription**: Select your subscription
   - **Resource group name**: `code-review-rg`
   - **Region**: `East US`
5. Click **"Review + Create"** → **"Create"**

---

## Step 2 — Register an app in Entra ID

This gives you the `CLIENT_ID` and `TENANT_ID` for OAuth2.

1. Go to: **Azure Portal** → search for **"App registrations"**
2. Click **"New registration"**
   - **Name**: `CodeReviewAgent`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI (optional)**: Leave blank for now
3. Click **"Register"**

### 2a — Copy your CLIENT_ID and TENANT_ID

On the app registration page, you'll see:
- **Application (client) ID**: Copy this → **CLIENT_ID**
- **Directory (tenant) ID**: Copy this → **TENANT_ID**

### 2b — Add Redirect URI

1. On the app page, go to **"Authentication"** (left sidebar)
2. Click **"Add a platform"** → **"Single-page application"**
   - **Redirect URIs**: `http://localhost:8000`
3. Click **"Configure"**

### 2c — Expose an API

1. Go to **"Expose an API"** (left sidebar)
2. Click **"Set"** next to "Application ID URI"
   - URI: `api://<your-CLIENT_ID>`
   - Click **"Save"**
3. Click **"Add a scope"**
   - **Scope name**: `review.read`
   - **Admin consent display name**: `Submit code for review`
   - **Admin consent description**: `Allows the app to submit code for AI review`
   - Click **"Add scope"**

### 2d — Create a client secret

1. Go to **"Certificates & secrets"** (left sidebar)
2. Click **"New client secret"**
   - **Description**: `local-dev`
   - **Expires**: `6 months`
3. Click **"Add"**
4. Copy the **VALUE** (not the ID) → **CLIENT_SECRET**
   - ⚠️ This secret is only shown once — save it immediately

---

## Step 3 — Create Azure AI Foundry project

1. Go to **Azure Portal** → search for **"AI Foundry"** or **"Azure AI Foundry"**
2. Click **"Create"**
   - **Subscription**: Select your subscription
   - **Resource group**: `code-review-rg`
   - **Name**: `code-review-project`
   - **Region**: `East US`
3. Click **"Review + Create"** → **"Create"**

### 3a — Get the Foundry endpoint

1. Once created, go to the project → **"Settings"**
2. Copy the **"Project connection string"** or **"Endpoint"** → **FOUNDRY_ENDPOINT**
3. Copy the **"API key"** → **FOUNDRY_API_KEY**

### 3b — Deploy GPT-4o model

1. On the project page, go to **"Deployments"** (left sidebar)
2. Click **"Deploy model"** → **"Create new deployment"**
   - **Model**: `gpt-4o`
   - **Deployment name**: `gpt-4o`
   - **Deployment configuration**: Standard (auto-scale)
3. Click **"Deploy"** (this may take 5-10 minutes)
4. Once deployed, note the deployment name: **FOUNDRY_MODEL** = `gpt-4o`

---

## Step 4 — Create Azure Blob Storage

1. Go to **Azure Portal** → search for **"Storage accounts"**
2. Click **"Create"**
   - **Resource group**: `code-review-rg`
   - **Storage account name**: `codereviewstorage` (must be globally unique, lowercase, 3-24 chars)
   - **Region**: `East US`
   - **Performance**: `Standard`
   - **Redundancy**: `Locally-redundant storage (LRS)`
3. Click **"Review + Create"** → **"Create"**

### 4a — Create a blob container

1. Once created, open the storage account
2. Go to **"Containers"** (left sidebar under "Data storage")
3. Click **"+ Container"**
   - **Name**: `reports`
   - **Public access level**: `Blob (anonymous read access for blobs only)`
4. Click **"Create"**

### 4b — Get the connection string

1. On the storage account page, go to **"Access keys"** (left sidebar)
2. Copy the **"Connection string"** under "key1" → **AZURE_STORAGE_CONNECTION_STRING**

---

## Step 5 — Fill in your .env file

1. In your project folder, open or create `.env`
2. Fill in all the values you collected:

```
TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_SECRET=your-secret-value

FOUNDRY_ENDPOINT=https://your-project.services.ai.azure.com
FOUNDRY_API_KEY=your-api-key
FOUNDRY_MODEL=gpt-4o

AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=codereviewstorage;...
BLOB_CONTAINER_NAME=reports

FRONTEND_URL=http://localhost:8000
```

---

## Step 6 — Update frontend/index.html

1. Open `frontend/index.html` in a text editor
2. Find and replace these three lines:

```javascript
// Before:
clientId:  "YOUR_CLIENT_ID",
authority: "https://login.microsoftonline.com/YOUR_TENANT_ID",
// scopes: ["api://YOUR_CLIENT_ID/review.read"]

// After:
clientId:  "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  // your CLIENT_ID
authority: "https://login.microsoftonline.com/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
// scopes: ["api://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/review.read"]
```

---

## Step 7 — Create a virtual environment and install dependencies

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 8 — Run the server

```bash
# Make sure you're logged in to Azure
az login

# Start the server
uvicorn app.main:app --reload --port 8000
```

Open your browser at **http://localhost:8000**

---

## Estimated costs (with $100 student credit)

| Resource            | Estimated monthly | Notes                       |
| ------------------- | ----------------- | --------------------------- |
| GPT-4o (Foundry)    | ~$10–15           | Based on ~50 demo reviews   |
| Blob Storage        | < $1              | Tiny JSON files             |
| App Service (Basic) | ~$5               | Only if you deploy to cloud |
| Entra ID            | Free              | Personal tenant             |
| **Total**           | **~$16–21**       | Leaves $79+ of credit       |

---

## Clean up (when done)

1. Go to **Azure Portal** → **"Resource groups"**
2. Find **`code-review-rg`**
3. Click **"Delete resource group"**
4. Type the resource group name to confirm
5. Click **"Delete"**

All billing stops immediately.

---

## Troubleshooting

**Can't find Foundry?**
Search for "Azure AI Foundry" in the portal search bar.

**Client secret disappeared?**
You'll need to create a new one — the old one can't be retrieved.

**Deployment is taking too long?**
GPT-4o deployments can take 10–15 minutes. Check "Deployments" page and refresh.

**Connection string error?**
Make sure you copied the full "Connection string" from "Access keys", not just "Storage account name".
