# Testing and acceptance

## Frontend static validation

```bash
cd frontend
npm run lint
npm run build
```

Acceptance:

- ESLint exits successfully.
- TypeScript compilation succeeds.
- Next.js generates the `/` static route.
- No horizontal page scrolling occurs at supported desktop widths.
- Header, WO context and process controls remain fixed.
- Research content, scenario rail and conversation scroll independently.

## Backend validation

```bash
python -m py_compile backend/app.py
```

Start the API and verify:

```bash
curl http://127.0.0.1:8000/health
```

## API contract cases

### Valid work-order lookup

Expected: HTTP 200 with the normalized `work_order`, `found: true`, and status when available. The UI shows `Loaded` only after this response succeeds.

### Unknown work-order lookup

Expected: HTTP 404. The previously confirmed active WO remains selected and the lookup error appears beside the input.

### Malformed work-order ID

Expected: the frontend shows `Use the format SYN-WO-000023` without making a request. Direct API requests that do not match `SYN-WO-` plus exactly six digits return HTTP 422.

### Valid request

Expected: HTTP 200 with `answer` and matching `work_order`.

### Missing or short question

Expected: HTTP 422 from Pydantic validation.

### Missing Foundry configuration

Expected: HTTP 503.

### Foundry, MCP or timeout failure

Expected: HTTP 502 with a stable user-safe message.

### Unexpected MCP tool

Expected: request fails; the tool is not approved.

## Grounding acceptance

For a known synthetic conflict case:

- The response must use retrieved work-order evidence.
- Researcher-provided facts must not be treated as verified automatically.
- Conflicting sources must remain visible.
- The response must not invent a participant or select a winner without evidence.
- Human review must be identified when the evidence requires it.

## Precision acceptance

The displayed response should:

- Directly answer the query
- Avoid reproducing the complete WO report
- Stay near the 90-word constraint
- Contain `Answer`, `Why`, and `Next step`
- Give one actionable next step

## UI acceptance

- Work-order entry is visible and usable.
- The request queue contains exactly 100 unique IDs from `000121` through `000220`.
- Selecting a queued WO retrieves it before changing the active workspace.
- The intake summary displays customer, address, claimed participants and provided references.
- Submitting a WO shows a retrieval state and prevents duplicate submissions.
- `Loaded` is never shown before the agent confirms the WO exists.
- A failed lookup does not replace the current active WO.
- Active WO is shown in the research workspace and coach header.
- Research steps are compact and clearly highlighted.
- Primary and secondary buttons remain readable.
- The coach spans the full content height on desktop.
- User and assistant messages are visually distinct.
- The composer stays visible at the bottom.
- Long answers scroll inside the conversation, not the entire page.
- Reduced-motion preferences are honored.

## Live Azure acceptance

Verified deployment checks:

- Frontend returned HTTP 200 over HTTPS.
- API `/health` returned `status: ok` and `foundry_configured: true`.
- Production CORS returned the exact frontend origin.
- A live `SYN-WO-000110` request retrieved evidence through the configured MCP tool.
- A live `SYN-WO-000023` lookup returned `UNDER_REVIEW` through the configured MCP tool.
- The deployed agent returned a concise three-section response.

Repeat these checks after every deployment.
