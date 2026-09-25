# Operations runbook

## Service endpoints

- Frontend: <https://nto-copilot-web-gopalg53.azurewebsites.net>
- API health: <https://nto-copilot-api-gopalg53.azurewebsites.net/health>
- API base: `https://nto-copilot-api-gopalg53.azurewebsites.net`

## Routine health check

1. Confirm the frontend returns HTTP 200.
2. Confirm `/health` returns `status: ok` and `foundry_configured: true`.
3. Submit one known synthetic WO question.
4. Confirm the response contains `Answer`, `Why`, and `Next step`.
5. Confirm verified facts and unverified claims remain distinct.

## View status

```bash
az webapp show -g rg-gopalg53-2640 -n nto-copilot-web-gopalg53 --query state -o tsv
az webapp show -g rg-gopalg53-2640 -n nto-copilot-api-gopalg53 --query state -o tsv
```

## Restart a service

```bash
az webapp restart -g rg-gopalg53-2640 -n nto-copilot-api-gopalg53
az webapp restart -g rg-gopalg53-2640 -n nto-copilot-web-gopalg53
```

Restart the API first, verify health, and then restart the frontend only when necessary.

## Logs

Enable application logging when troubleshooting:

```bash
az webapp log config \
  -g rg-gopalg53-2640 \
  -n nto-copilot-api-gopalg53 \
  --application-logging filesystem \
  --level information
```

Stream logs:

```bash
az webapp log tail -g rg-gopalg53-2640 -n nto-copilot-api-gopalg53
```

Do not paste access tokens, authorization headers or full sensitive payloads into issue reports.

## Symptom: frontend shows `Failed to fetch`

Check in order:

1. API `/health` is reachable.
2. Frontend production build contains the correct API URL.
3. `FRONTEND_ORIGINS` includes the exact frontend origin.
4. The browser request is using HTTPS.
5. The API app is not cold-starting or stopped.

## Symptom: API health works but coach returns 502

Possible causes:

- Managed identity role propagation has not completed.
- Foundry agent name or version is incorrect.
- The agent cannot access its MCP connection.
- MCP returned an error or requested an unapproved tool.
- Foundry exceeded the 90-second timeout.

Check API logs and verify the API managed identity roles.

## Symptom: answers are too long

The API performs two passes. Confirm the second precision prompt is still present and requires:

- No more than 90 words
- Exactly `Answer`, `Why`, and `Next step`
- No repeated work-order inventory

## Symptom: answer conflicts with visible demo text

The retrieved work order is authoritative for the answer. Example scenarios are teaching aids and must not override live synthetic WO evidence. For a manually entered WO, the interface uses the generic `Work order research` title and suppresses scenario-specific evidence cards.

## Rollback

App Service deployments retain deployment history. Inspect deployments before selecting a previous package:

```bash
az webapp log deployment list -g rg-gopalg53-2640 -n nto-copilot-api-gopalg53 -o table
az webapp log deployment list -g rg-gopalg53-2640 -n nto-copilot-web-gopalg53 -o table
```

Prefer redeploying a previously validated package. Do not change the Foundry agent or MCP connection as part of a frontend rollback.

## Free-tier behavior

The current App Service plan can cold-start after inactivity and is intended for demonstration workloads. For production availability, move to an appropriate paid plan or Container Apps deployment after cost and operational review.
