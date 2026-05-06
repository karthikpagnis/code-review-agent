# Deployment Guide

How to deploy the Code Review Agent to Azure App Service for public access.

---

## Prerequisites

- Azure account with active subscription
- Azure CLI installed
- Completed `infra/azure_setup_web.md` or `infra/azure_setup.md`

---

## Step 1 — Create an App Service Plan

```bash
az appservice plan create \
  --name code-review-plan \
  --resource-group code-review-rg \
  --sku B1 \
  --is-linux
```

---

## Step 2 — Create a Web App

```bash
az webapp create \
  --resource-group code-review-rg \
  --plan code-review-plan \
  --name code-review-agent-app \
  --runtime "PYTHON|3.11"
```

Note the URL: `https://code-review-agent-app.azurewebsites.net`

---

## Step 3 — Configure App Service

```bash
# Enable Git deployment
az webapp deployment user set \
  --user-name <username> \
  --password <password>

# Add Azure remote
az webapp deployment source config-local-git \
  --name code-review-agent-app \
  --resource-group code-review-rg
```

---

## Step 4 — Deploy from Git

```bash
# Add Azure remote to your local repo
git remote add azure <git-clone-url-from-previous-step>

# Deploy
git push azure master
```

---

## Step 5 — Add Environment Variables

In Azure Portal:

1. Go to: **App Service** → `code-review-agent-app`
2. **Settings** → **Configuration**
3. **New application settings** for each:
   ```
   TENANT_ID
   CLIENT_ID
   CLIENT_SECRET
   FOUNDRY_ENDPOINT
   FOUNDRY_API_KEY
   FOUNDRY_MODEL
   AZURE_STORAGE_CONNECTION_STRING
   BLOB_CONTAINER_NAME
   FRONTEND_URL=https://code-review-agent-app.azurewebsites.net
   ```
4. Click **Save**

---

## Step 6 — Update Entra ID Redirect URI

1. Go to: **Entra ID** → **App registrations** → `CodeReviewAgent`
2. **Authentication** → Single-page application
3. Add redirect URI: `https://code-review-agent-app.azurewebsites.net`
4. Click **Save**

---

## Step 7 — Update frontend/index.html

Change `FRONTEND_URL` in your code to point to the deployed app:

```javascript
const redirectUri = "https://code-review-agent-app.azurewebsites.net";
```

Push this change:
```bash
git add frontend/index.html
git commit -m "Update redirect URI to production"
git push azure master
```

---

## Step 8 — Verify Deployment

1. Go to: https://code-review-agent-app.azurewebsites.net
2. Click "Sign in with Microsoft"
3. Submit code for review
4. Verify the report is generated

---

## Estimated Monthly Costs

| Resource | Cost | Notes |
|----------|------|-------|
| App Service (B1) | ~$15 | Shared CPU |
| GPT-4o calls | ~$10-15 | ~50 reviews |
| Blob Storage | < $1 | JSON files |
| **Total** | ~$26-31 | |

---

## Troubleshooting

**Deployment fails?**
- Check: `az webapp log tail --name code-review-agent-app --resource-group code-review-rg`

**Still getting 401 errors?**
- Verify environment variables are set
- Check CLIENT_ID, TENANT_ID, and FOUNDRY_API_KEY

**App Service is slow?**
- Upgrade to B2 plan for better performance
- Increase FOUNDRY_MODEL concurrency

---

## Rollback

If something goes wrong:

```bash
git log --oneline azure/master
git revert <commit-hash>
git push azure master
```

---

## CI/CD Pipeline (Optional)

For automatic deployments on push:

1. In Azure Portal: **App Service** → **Deployment Center**
2. Choose **GitHub**
3. Authorize GitHub
4. Select your repo and branch
5. App auto-deploys on each push!

---

## Custom Domain (Optional)

To use your own domain (e.g., `codereview.yourdomain.com`):

1. **App Service** → **Custom domains**
2. Add your domain
3. Update DNS records in your registrar
4. Add HTTPS certificate

---

## Monitoring

Track app health:

```bash
# View logs
az webapp log tail --name code-review-agent-app --resource-group code-review-rg

# View metrics
az monitor metrics list-definitions \
  --resource /subscriptions/<sub-id>/resourceGroups/code-review-rg/providers/Microsoft.Web/sites/code-review-agent-app
```

---

## Scale Up

If you get high traffic:

```bash
az appservice plan update \
  --name code-review-plan \
  --resource-group code-review-rg \
  --sku P1V2
```

More SKU options:
- **B1**: Shared, free tier
- **B2/B3**: Basic (low traffic)
- **S1/S2/S3**: Standard (medium traffic)
- **P1V2/P2V2**: Premium (high traffic, auto-scale)

---

## Cleanup

Delete all resources when done:

```bash
az group delete --name code-review-rg --yes --no-wait
```
