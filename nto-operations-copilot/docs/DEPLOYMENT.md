# Azure deployment

## Current deployment

| Component | Azure resource | Public URL |
|---|---|---|
| Frontend | `nto-copilot-web-gopalg53` | <https://nto-copilot-web-gopalg53.azurewebsites.net> |
| API | `nto-copilot-api-gopalg53` | <https://nto-copilot-api-gopalg53.azurewebsites.net> |
| Plan | `nto-copilot-free-plan` | Azure App Service Free, Linux |
| Resource group | `rg-gopalg53-2640` | Southeast Asia |

The existing Container Apps environment and registry were not modified. Azure ACR Tasks were unavailable for the registry and no local container runtime was installed, so the application was deployed through direct App Service zip deployment.

## Backend deployment

Create the package:

```bash
deploy_dir=$(mktemp -d)
cp backend/app.py backend/requirements.txt "$deploy_dir/"
(cd "$deploy_dir" && zip -q api.zip app.py requirements.txt)
```

Configure the API:

```bash
az webapp config appsettings set \
  --resource-group rg-gopalg53-2640 \
  --name nto-copilot-api-gopalg53 \
  --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    AZURE_AI_PROJECT_ENDPOINT='https://gopalg53-5366-resource.services.ai.azure.com/api/projects/gopalg53-5366' \
    AZURE_AI_AGENT_NAME='wo-intake-agent' \
    AZURE_AI_AGENT_VERSION='3' \
    FRONTEND_ORIGINS='https://nto-copilot-web-gopalg53.azurewebsites.net'

az webapp config set \
  --resource-group rg-gopalg53-2640 \
  --name nto-copilot-api-gopalg53 \
  --startup-file 'python -m uvicorn app:app --host 0.0.0.0 --port 8000'
```

Deploy:

```bash
az webapp deploy \
  --resource-group rg-gopalg53-2640 \
  --name nto-copilot-api-gopalg53 \
  --src-path "$deploy_dir/api.zip" \
  --type zip \
  --timeout 900000
```

## Frontend deployment

Build with the production API URL. `NEXT_PUBLIC_` values are compiled into the browser bundle, so this must be set during the build:

```bash
cd frontend
NEXT_PUBLIC_NTO_API_BASE_URL='https://nto-copilot-api-gopalg53.azurewebsites.net' npm run build
```

Package the standalone Next.js server:

```bash
deploy_dir=$(mktemp -d)
cp -R .next/standalone/. "$deploy_dir/"
mkdir -p "$deploy_dir/.next"
cp -R .next/static "$deploy_dir/.next/static"
cp -R public "$deploy_dir/public"
(cd "$deploy_dir" && zip -qr web.zip . -x web.zip)
```

Configure and deploy:

```bash
az webapp config appsettings set \
  --resource-group rg-gopalg53-2640 \
  --name nto-copilot-web-gopalg53 \
  --settings NODE_ENV=production WEBSITE_NODE_DEFAULT_VERSION='22-lts'

az webapp config set \
  --resource-group rg-gopalg53-2640 \
  --name nto-copilot-web-gopalg53 \
  --startup-file 'node server.js'

az webapp deploy \
  --resource-group rg-gopalg53-2640 \
  --name nto-copilot-web-gopalg53 \
  --src-path "$deploy_dir/web.zip" \
  --type zip \
  --timeout 900000
```

## Managed identity roles

The API system-assigned managed identity requires:

- `Foundry Agent Consumer` at the Foundry project scope
- `Foundry User` at the Foundry project scope
- `Cognitive Services OpenAI User` at the parent Foundry resource scope

The frontend does not need an Azure identity.

## Post-deployment verification

```bash
curl -I https://nto-copilot-web-gopalg53.azurewebsites.net
curl https://nto-copilot-api-gopalg53.azurewebsites.net/health
```

Verify production CORS:

```bash
curl -D - -o /dev/null -X OPTIONS \
  https://nto-copilot-api-gopalg53.azurewebsites.net/api/coach \
  -H 'Origin: https://nto-copilot-web-gopalg53.azurewebsites.net' \
  -H 'Access-Control-Request-Method: POST'
```

Finally, submit one synthetic WO question through the live UI and confirm a grounded concise response.

## Container images

Dockerfiles are included for a future move to Azure Container Apps or another OCI platform. The current App Service deployment uses zip packages and does not depend on those Dockerfiles.
