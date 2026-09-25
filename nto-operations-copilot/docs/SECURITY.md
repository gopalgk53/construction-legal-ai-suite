# Security and trust boundaries

## Credentials

- No Azure credential is stored in the frontend.
- No MCP credential is stored in the frontend or committed files.
- Local authentication uses Azure CLI through `DefaultAzureCredential`.
- Azure hosting uses a system-assigned managed identity.
- `.env`, `.env.local` and `.venv` are ignored.

Never commit access tokens, API keys, authorization headers, Azure CLI caches or downloaded production data.

## Least privilege

The API managed identity receives only the roles needed to invoke the configured Foundry agent. The frontend has no managed identity.

MCP approval is restricted in code to:

```text
sunray-wo-mcp.get_work_order
```

An unexpected tool identity causes a hard failure. Approval processing is capped at three rounds.

## Input boundaries

The public API validates:

- WO identifier: 2–80 characters
- Question: 2–4000 characters
- Current-step label: up to 120 characters

The backend selects the Foundry agent reference. Clients cannot choose an agent or agent version.

## Output boundaries

The complete intake report is not returned to the browser. A second grounded pass produces a concise answer with a fixed structure and a 90-word target.

The UI and prompt reinforce these rules:

- Do not invent missing facts.
- Separate verified evidence from claims.
- Preserve material conflicts.
- Identify required human review.
- Keep the researcher responsible for verification and escalation.

## CORS

The API uses an explicit comma-separated allowlist in `FRONTEND_ORIGINS`. Wildcard origins are not enabled.

Production value:

```text
https://nto-copilot-web-gopalg53.azurewebsites.net
```

## Known gaps before production use

- No user authentication or authorization layer
- No rate limiting
- No per-user audit trail
- No durable chat session storage
- No application-level content redaction
- No private network path between App Service and Foundry
- Demonstration hosting tier rather than a production SLA tier

These gaps are acceptable only for the current synthetic demonstration. Do not connect real customer workloads until they are addressed.

## Incident response

If credential exposure is suspected:

1. Stop the affected web app.
2. Revoke or rotate the exposed credential at its source.
3. Review Azure sign-in, Foundry and application logs.
4. Verify managed identity role assignments.
5. Redeploy from a known clean package.

Managed identities do not have a reusable plaintext secret to rotate. Remove unnecessary role assignments if access must be revoked immediately.
