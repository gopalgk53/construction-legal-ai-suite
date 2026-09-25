# Frontend

The frontend is a Next.js research-coach interface for new NTO researchers. It provides the guided operational workflow, work-order entry, exception examples and a full-height coach conversation connected to the FastAPI gateway.

## Main experience

- Cinematic portfolio-aligned entry
- Work-order input
- Six research stages
- Contextual task guidance
- Material-conflict teaching visualization
- Full-height ChatGPT-style coach window
- Independent navigation, task and conversation scrolling
- Concise `Answer`, `Why`, and `Next step` rendering

## Source structure

```text
src/
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/nto/
│   ├── CopilotShell.tsx
│   ├── EvidenceConflict.tsx
│   ├── IntroScene.tsx
│   ├── OperationsWorkspace.tsx
│   ├── PromptBar.tsx
│   └── ScenarioRail.tsx
└── data/
    └── demoScenarios.ts
```

## Configuration

Create `.env.local`:

```dotenv
NEXT_PUBLIC_NTO_API_BASE_URL=http://localhost:8000
```

This is a public browser configuration value, not a credential. It is compiled into the production bundle during `npm run build`.

## Development

```bash
npm ci
npm run dev
```

## Validation

```bash
npm run lint
npm run build
```

## Production build

The app uses `output: "standalone"` in `next.config.ts` so it can run as a small Node deployment artifact or container.

```bash
NEXT_PUBLIC_NTO_API_BASE_URL='https://YOUR-API-HOST' npm run build
node .next/standalone/server.js
```

When packaging standalone output, include:

- `.next/standalone`
- `.next/static`
- `public`

## Design system

The UI uses the portfolio’s visual language without copying its project content:

- Slate-white canvas
- Deep navy type and controls
- Blue-to-violet accents
- Inter/system sans-serif typography
- Fine borders and restrained shadows
- Rounded operational surfaces
- Motion that respects `prefers-reduced-motion`

## Interaction boundaries

- The browser never contacts Foundry or MCP directly.
- The work-order ID and question are sent only to the configured API.
- The frontend does not persist chat history.
- Example scenarios must not override evidence retrieved for a manually entered WO.

See the repository [Architecture](../docs/ARCHITECTURE.md) and [Local development](../docs/LOCAL_DEVELOPMENT.md) guides.
