# Replit Deployment Guide

## 📋 Overview

This guide explains how to deploy and run the Unmanned Island System on Replit,
specifically for the "Unmanned-Island-3" project.

**Status:** ✅ **READY FOR DEPLOYMENT**  
**Date:** December 2025  
**Replit Project:** `@unmanned-island/Unmanned-Island-3`

---

## 🚀 Quick Start

### 1. Initial Setup

When you first open the Replit project:

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd apps/web
npm install
cd ../..

# Install Island AI dependencies
cd island-ai
npm install
cd ..
```

### 2. Start the Development Server

Click the **"Run"** button in Replit, or manually run:

```bash
cd apps/web
npm run dev
```

The app will be available at:

- **Replit Preview:** `https://<your-repl>.replit.dev`
- **Local:** `http://localhost:5000`

---

## 📁 Project Structure

```
Unmanned-Island/
├── apps/
│   └── web/              # React frontend (runs on port 5000)
│       ├── src/          # Source code
│       ├── public/       # Static assets
│       ├── dist/         # Build output (gitignored)
│       └── package.json
│
├── island-ai/            # Island AI Stage 1 & 2
│   ├── src/
│   │   ├── agents/       # Stage 1 agents
│   │   ├── collaboration/ # Stage 2 coordinator
│   │   └── __tests__/    # Test suites
│   ├── examples/         # Usage examples
│   └── package.json
│
├── core/                 # SynergyMesh core engine
├── governance/           # Structural governance
├── automation/           # Autonomous systems
└── .replit              # Replit configuration
```

---

## ⚙️ Replit Configuration

### `.replit` File

The project is configured to:

- Use **Node.js 20** runtime
- Run on **port 5000** (frontend)
- Use **esbuild** for fast bundling
- Support **React** with **HashRouter**

```ini
modules = ["bash", "web", "nodejs-20"]

[agent]
expertMode = true

[workflows]
runButton = "Project"

[[workflows.workflow]]
name = "Frontend"
[[workflows.workflow.tasks]]
task = "shell.exec"
args = "cd apps/web && npm run dev"
waitForPort = 5000

[[ports]]
localPort = 5000
externalPort = 80
```

### Environment Variables

No environment variables are required for basic operation. Optional
configurations:

```bash
# .env (optional)
NODE_ENV=development
PORT=5000
```

---

## 🔨 Build Process

### Development Build

```bash
cd apps/web
npm run dev
```

**What happens:**

- Starts esbuild in watch mode
- Bundles React app to `main.js` and `main.css`
- Serves on `http://0.0.0.0:5000`
- Hot reloads on file changes

### Production Build

```bash
cd apps/web
npm run build
```

**Output:**

- `dist/index.html` - Main HTML file
- `dist/main.js` - Bundled JavaScript (~2.9 MB)
- `dist/main.css` - Bundled CSS (~71 KB)

---

## 🧪 Testing

### Frontend Tests

Currently, the frontend doesn't have specific tests. Integration tests are in
Island AI.

### Island AI Tests

```bash
cd island-ai
npm install  # First time only
npm test
```

**Expected Output:**

```
Test Suites: 2 passed, 2 total
Tests:       38 passed, 38 total
Snapshots:   0 total
Time:        ~4s
```

**Test Coverage:**

- Stage 1 Agents: 25 tests
- Stage 2 Coordinator: 13 tests

---

## 📦 Dependencies

### Frontend (`apps/web`)

**Key Dependencies:**

- `react` ^18.3.1
- `react-router` ^7.9.6
- `lucide-react` ^0.556.0 (icons)
- `mermaid` ^11.12.2 (diagrams)
- `recharts` ^2.15.3 (charts)
- `@radix-ui/*` (UI components)

**Dev Dependencies:**

- `esbuild` 0.27.1
- `tailwindcss` ^3.4.18
- `postcss` ^8.5.3

### Island AI (`island-ai`)

**Dev Dependencies:**

- `typescript` ^5.4.0
- `jest` ^29.7.0
- `ts-jest` ^29.1.2

---

## 🔍 Troubleshooting

### Issue: Build fails with "Cannot find module 'esbuild'"

**Solution:**

```bash
cd apps/web
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue: Port 5000 already in use

**Solution:**

```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Or change port in package.json
# "dev": "node scripts/build.mjs --port 3000"
```

### Issue: Island AI tests fail

**Solution:**

```bash
cd island-ai
rm -rf node_modules package-lock.json
npm install
npm test
```

### Issue: "React is not defined" error

**Solution:** Check that `main.tsx` imports React:

```typescript
import React from 'react';
import { createRoot } from 'react-dom/client';
```

### Issue: Routes not working (404 errors)

**Solution:** Ensure `HashRouter` is used (not `BrowserRouter`):

```typescript
import { HashRouter } from 'react-router';
// ... use <HashRouter> in App.tsx
```

---

## 🌐 Deployment

### Replit Static Deployment

1. Go to your Repl settings
2. Click **"Deploy"** → **"Static Site"**
3. Configure:
   - **Build command:** `npm run build --workspace apps/web`
   - **Output directory:** `apps/web/dist`
4. Click **"Deploy"**

### Manual Static Deployment

```bash
# Build the app
cd apps/web
npm run build

# The dist/ folder contains:
# - index.html
# - main.js
# - main.css

# Deploy to any static host:
# - Netlify
# - Vercel
# - GitHub Pages
# - Cloudflare Pages
```

---

## 📊 Performance

### Build Times

| Operation        | Time |
| ---------------- | ---- |
| First install    | ~20s |
| Dev server start | ~3s  |
| Production build | ~5s  |
| Hot reload       | <1s  |

### Bundle Sizes

| File       | Size        | Gzipped     |
| ---------- | ----------- | ----------- |
| `main.js`  | 2.9 MB      | ~600 KB     |
| `main.css` | 71 KB       | ~15 KB      |
| **Total**  | **2.97 MB** | **~615 KB** |

### Runtime Performance

- **Time to Interactive:** ~1.5s
- **First Contentful Paint:** ~0.8s
- **Lighthouse Score:** 85+ (Performance)

---

## 🎯 Features Deployed

### Frontend (`apps/web`)

- ✅ **Home Page** - Project overview
- ✅ **Architecture Page** - System architecture visualization
- ✅ **Frontend Page** - Frontend tech stack info
- ✅ **Backend Page** - Backend services info
- ✅ **Contact Page** - Contact information
- ✅ **Language Governance** - Language governance dashboard

### Island AI

- ✅ **Stage 1 Agents** (6 agents)
  - Architect Agent
  - Security Agent
  - DevOps Agent
  - QA Agent
  - Data Scientist Agent
  - Product Manager Agent

- ✅ **Stage 2 Coordinator** (NEW)
  - Sequential execution
  - Parallel execution
  - Conditional execution
  - Iterative execution
  - Knowledge sharing
  - Synchronization barriers

---

## 🔗 Related Documentation

- [Island AI Stage 2 Documentation](../island-ai/STAGE2_AGENT_COORDINATOR.md)
- [Stage 2 Planning](../island-ai/STAGE2_PLANNING.md)
- [Main README](../README.md)
- [Frontend Phase 2 Improvements](../apps/web/PHASE2_IMPROVEMENTS.md)

---

## 📞 Support

**Project:** Unmanned Island System  
**Maintainer:** SynergyMesh Team  
**Repository:** [SynergyMesh-admin/Unmanned-Island](https://github.com/SynergyMesh-admin/Unmanned-Island)

For issues or questions:

1. Check this deployment guide
2. Review the troubleshooting section
3. Check the related documentation
4. Open a GitHub issue

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] Run `npm install` in all workspaces
- [ ] Run `npm run build --workspace apps/web`
- [ ] Verify `apps/web/dist/` contains all files
- [ ] Test locally: `cd apps/web/dist && python -m http.server 5000`
- [ ] Run Island AI tests: `cd island-ai && npm test`
- [ ] Check CodeQL security scan: No alerts
- [ ] Verify all routes work with HashRouter
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Confirm mobile responsiveness
- [ ] Review performance metrics (Lighthouse)

---

**Status:** 🎉 **Ready for Production Deployment**

Last Updated: December 8, 2025
