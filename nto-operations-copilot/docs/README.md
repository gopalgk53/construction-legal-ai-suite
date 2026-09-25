# Documentation index

This directory contains the complete product, engineering, deployment and operating documentation for NTO Operations Copilot.

## Start here

- [User guide](USER_GUIDE.md) — how a researcher uses the product
- [Architecture](ARCHITECTURE.md) — system components, request lifecycle and trust boundaries
- [API reference](API_REFERENCE.md) — HTTP endpoints, payloads and errors

## Build and operate

- [Local development](LOCAL_DEVELOPMENT.md) — prerequisites, setup and local troubleshooting
- [Azure deployment](DEPLOYMENT.md) — current resources and repeatable deployment commands
- [Operations runbook](OPERATIONS.md) — health checks, logs, restart, rollback and incident symptoms
- [Testing and acceptance](TESTING.md) — static, API, grounding, UI and live-deployment checks
- [Security](SECURITY.md) — credentials, least privilege, CORS, trust boundaries and known gaps

## Component guides

- [Frontend README](../frontend/README.md)
- [Backend README](../backend/README.md)
- [Project README](../README.md)

## Current live system

- Application: <https://nto-copilot-web-gopalg53.azurewebsites.net>
- API health: <https://nto-copilot-api-gopalg53.azurewebsites.net/health>
- Environment: Azure App Service, Southeast Asia
- Data: synthetic work-order records retrieved through the approved MCP tool

## Documentation maintenance

Update the relevant document whenever any of these change:

- Public URLs or Azure resource names
- Foundry project, agent name or agent version
- MCP server label, tool name or approval policy
- API request or response fields
- Research workflow stages
- Deployment commands or runtime versions
- Security boundaries or known production gaps
- Validation and acceptance requirements

Documentation must never contain credentials, bearer tokens, API keys, customer data or copied Azure CLI authentication output.
