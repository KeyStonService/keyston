# Island AI Stage 1-4

Stage 1 delivers six foundational agents described in `island-ai.md`. Stage 2 adds the productionized multi-agent **AgentCoordinator** for sequential/parallel/conditional/iterative orchestration, while Stage 3-4 layer self-learning + observability hooks for production readiness. This package exposes them as typed modules plus a helper runner.

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

## Stage 2-4 capabilities

- **Stage 2 – Collaboration**: `AgentCoordinator` (exported from `collaboration`) supports sequential, parallel, conditional, and iterative runs with knowledge sharing and barriers.
- **Stage 3 – Self-learning hooks**: Shared knowledge base enables iterative refinement loops you can persist in your runtime.
- **Stage 4 – Productionization**: Orchestration defaults are wired into `synergymesh.yaml` with the production artifact path (`dist/collaboration/agent-coordinator.js`) and the development source (`src/collaboration/agent-coordinator.ts`) plus strategy list, ready for dashboard/observability pipelines.

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
