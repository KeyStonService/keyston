# Island AI Stage 1

Stage 1 delivers six foundational agents described in `island-ai.md`. This package exposes them as typed modules plus a helper runner.

## Layout

```
island-ai/
├── package.json
├── tsconfig.json
├── src/
│   ├── types.ts
│   ├── index.ts
│   └── agents/
│       ├── architect/
│       ├── security/
│       ├── devops/
│       ├── qa/
│       ├── data-scientist/
│       └── product-manager/
```

Each agent provides an `AgentInsight[]` describing its diagnostics, while shared helpers live in `src/types.ts` and `src/agents/base-agent.ts`.

## Usage

```ts
import { runStageOne } from 'island-ai';

const reports = await runStageOne({
  requestId: 'example',
  timestamp: new Date(),
  payload: { deploymentsPerWeek: 15 }
});
```

## Scripts

- `npm run build` – Emit ESM output under `dist/`
- `npm run lint` – Type-check the codebase
- `npm run clean` – Remove build output
