# Azure Setup Guide

Complete these steps once before running the project.
Total time: ~45 minutes. Cost: well within the $100 student credit.

---

## Prerequisites

- Azure account
- Azure CLI installed: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
- Python 3.11+

---

## Step 1 — Log in to Azure CLI

```bash
az login
az account show   # confirm your subscription is active
```

---

## Step 2 — Create a resource group

All resources live in one group so you can delete everything cleanly when done.

```bash
az group create \
  --name code-review-rg \
  --location eastus
```

---

## Step 3 — Register an app in Entra ID (Azure AD)

This gives you the CLIENT_ID and TENANT_ID for OAuth2 authentication.

```bash
# Create the app registration
az ad app create \
  --display-name "CodeReviewAgent" \
  --sign-in-audience AzureADMyOrg

# Note the appId from the output — this is your CLIENT_ID
# Note the tenantId — this is your TENANT_ID
```

**In Azure Portal (easier for the next steps):**

1. Go to: Azure Portal → Microsoft Entra ID → App registrations → CodeReviewAgent
2. Under "Authentication" → Add platform → Single-page application
   - Redirect URI: `http://localhost:8000`
3. Under "Expose an API":
   - Set Application ID URI: `api://<your-CLIENT_ID>`
   - Add scope: `review.read`
     - Admin consent display name: "Submit code for review"
     - Admin consent description: "Allows the app to submit code for AI review"
4. Under "Certificates & secrets" → New client secret
   - Description: local-dev
   - Note the secret VALUE (shown only once) — this is your CLIENT_SECRET

---

## Step 4 — Create Azure AI Foundry project

This is the core agent runtime.

```bash
# Create an AI hub (required parent resource)
az cognitiveservices account create \
  --name code-review-hub \
  --resource-group code-review-rg \
  --kind AIHub \
  --sku S0 \
  --location eastus

# Create a Foundry project inside the hub
az cognitiveservices account create \
  --name code-review-project \
  --resource-group code-review-rg \
  --kind AIProject \
  --sku S0 \
  --location eastus
```

**Then in Azure Portal:**

1. Go to: Azure AI Foundry → your project → Settings
2. Copy the "Project connection string" — this becomes FOUNDRY_ENDPOINT
3. Go to: Deployments → Deploy model → gpt-4o
   - Deployment name: gpt-4o (keep it simple)
   - This creates the model you'll call in the agents

---

## Step 5 — Create Azure Blob Storage

Reports are saved here after each review.

```bash
# Create a storage account (name must be globally unique, lowercase, 3-24 chars)
az storage account create \
  --name codereviewstorage \
  --resource-group code-review-rg \
  --sku Standard_LRS \
  --location eastus

# Create the container
az storage container create \
  --name reports \
  --account-name codereviewstorage \
  --public-access blob

# Get the connection string
az storage account show-connection-string \
  --name codereviewstorage \
  --resource-group code-review-rg \
  --query connectionString \
  --output tsv
```

Copy the output — this is your AZURE_STORAGE_CONNECTION_STRING.

---

## Step 6 — Fill in your .env file

```bash
cp .env.example .env
# Edit .env with all the values you collected above
```

Your .env should look like:

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

## Step 7 — Update frontend/index.html

Open `frontend/index.html` and replace the two placeholders:

```javascript
clientId:  "YOUR_CLIENT_ID",    // → your CLIENT_ID from Step 3
authority: "https://login.microsoftonline.com/YOUR_TENANT_ID",
// scopes:
"api://YOUR_CLIENT_ID/review.read"
```

---

## Step 8 — Enable DefaultAzureCredential locally

The agents use `DefaultAzureCredential` which reads from your CLI login.

```bash
az login
# You should already be logged in from Step 1 — this refreshes the credential
```

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

Delete the entire resource group to stop all billing:

```bash
az group delete --name code-review-rg --yes --no-wait
```
