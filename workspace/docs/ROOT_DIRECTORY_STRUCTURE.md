# Root Directory Structure - Minimal System Skeleton

## Current Root Directory (After Cleanup)

```
/workspace/
├── .env.example          # Environment variables template
├── .git/                 # Git repository
├── .github/              # GitHub workflows and configurations
├── .gitignore            # Git ignore rules
├── .replit               # Replit configuration
├── CNAME                 # Custom domain configuration
├── README.md             # Project documentation
├── root.bootstrap.yaml   # Boot pointer: System bootstrap configuration
├── root.env.sh           # Boot pointer: Environment setup script
├── root.fs.map           # Boot pointer: Filesystem mapping
├── wrangler.toml         # Symlink to workspace/config/wrangler.toml
├── controlplane/         # Governance layer (immutable)
└── workspace/            # Work layer (mutable)
```

## Compliance with Minimal System Skeleton

✅ **Boot Pointers** (3 files):

- `root.bootstrap.yaml`
- `root.env.sh`
- `root.fs.map`

✅ **Git Files** (3 items):

- `.git/`
- `.github/`
- `.gitignore`

✅ **Project Files** (4 files):

- `README.md`
- `CNAME`
- `.env.example`
- `.replit`
- `wrangler.toml` (symlink)

✅ **Primary Directories** (2 directories):

- `controlplane/` - Governance layer
- `workspace/` - Work layer

## Files Moved to Workspace

### Documentation → `workspace/docs/`

- CLOUDFLARE_DEPLOYMENT_FIX.md
- FINAL_COMPLETION_SUMMARY.md
- NAMESPACE_SPECIFICATION_COMPLETE.md
- PROJECT_REORGANIZATION_REPORT.md
- PR_REVIEW_COMPLETION_REPORT.md
- PR_REVIEW_REPORT.md
- WORKSPACE_REORGANIZATION_COMPLETE.md
- reorganize-to-workspace.md
- replit.md
- todo.md

### Configuration → `workspace/config/`

- package.json
- package-lock.json
- postcss.config.js
- tailwind.config.js
- tsconfig.json
- vite.config.ts
- drizzle.config.ts
- .gitignore.prod
- wrangler.toml (original)

### Application Code → `workspace/`

- chatops/ → workspace/chatops/
- client/ → workspace/client/
- db/ → workspace/db/
- server/ → workspace/services/server/
- shared/ → workspace/shared/
- chatops-assistant/ → workspace/chatops-assistant/
- attached_assets/ → workspace/attached_assets/

### Archive → `workspace/archive/`

- Screenshot_20251223_184259.jpg
- fix_indentation.py
- fix_main_function.py
- cleanup-root-directory.sh
- cleanup-workspace-root.sh
- cleanup-root-to-minimal-skeleton.sh
- summarized_conversations/

## Root Directory Rules

### ✅ Allowed in Root

1. Boot pointers (root.*)
2. Git files (.git/, .github/, .gitignore)
3. Essential project files (README.md, LICENSE, CNAME, .env.example, .replit)
4. Symlinks to workspace configs (wrangler.toml)
5. Primary directories (controlplane/, workspace/)

### ❌ Prohibited in Root

1. Governance files (must be in controlplane/baseline/)
2. Source code (must be in workspace/src/)
3. Configuration files (must be in workspace/config/ or controlplane/baseline/config/)
4. Documentation (must be in workspace/docs/)
5. Scripts (must be in workspace/src/scripts/)
6. Build artifacts (must be in workspace/artifacts/ or /var/)
7. Runtime data (must be in /var/ or workspace/runtime/)
8. Temporary files (must be in /tmp/ or workspace/runtime/tmp/)

## Status

✅ **Root directory now complies with Minimal System Skeleton principle**

All non-essential files have been moved to appropriate locations in the workspace.
