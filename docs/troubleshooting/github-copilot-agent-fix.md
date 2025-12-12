## GitHub Copilot Agent Fix

When Copilot-triggered lint or TypeScript jobs fail inside the dev container, it
is usually because the Alpine image does not preinstall Node.js/npm or the
global TypeScript compiler. Use the checklist below to bring the tooling back
online and unblock the agent.

### 1. Install Node.js and npm

```sh
sudo apk add --no-cache nodejs npm
```

### 2. Re-run workspace linters

```sh
npm run lint --workspaces --if-present
```

This fans out to every configured workspace and ensures the newly installed Node
runtime is wired into each package.

### 3. Provide a global TypeScript compiler

```sh
sudo npm install -g typescript
```

This avoids `npx` permission errors such as
`EACCES: permission denied, mkdir '/home/node'` when Copilot shells out to
`tsc -b` from the repo root.

### 4. Validate the solution build

```sh
tsc -b tsconfig.json
```

Run this from `/workspaces/unmanned-island` to confirm the solution-style config
still compiles.

### 5. Run the shared test suite

```sh
npm test --workspaces --if-present
```

This guards against regressions after the tooling reinstall.

---

## Alpine Linux: Kubernetes 工具安裝問題

When the devcontainer feature `kubectl-helm-minikube:1` fails to install on
Alpine Linux, you may see errors like:

- `無法安裝 Helm：解壓縮失敗：錯誤原因是 tar 提取`
- `無法安裝 Minikube：下載 Minikube 失敗：錯誤訊息為 EACCES：權限被拒絕，mkdir /home/node`

### Root Causes

1. **Helm 解壓縮失敗** - Alpine 缺少 `openssl` 用於校驗和驗證
2. **Minikube 權限錯誤** - `/home/node` 目錄不存在
3. **Minikube 兼容性問題** - 官方二進制文件使用 glibc，但 Alpine 使用 musl libc

### Solution: Manual Installation

#### Step 1: Create missing directory

```sh
sudo mkdir -p /home/node
sudo chown "$(whoami):$(whoami)" /home/node
```

#### Step 2: Install kubectl

```sh
KUBECTL_VERSION=$(curl -L -s https://dl.k8s.io/release/stable.txt)
curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl
kubectl version --client
```

#### Step 3: Install Helm (skip checksum on Alpine)

```sh
curl -fsSL -o /tmp/get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 /tmp/get_helm.sh
sudo VERIFY_CHECKSUM=false /tmp/get_helm.sh
rm /tmp/get_helm.sh
helm version
```

#### Step 4: Install Minikube with glibc compatibility layer

```sh
# Install gcompat (glibc compatibility layer for musl)
sudo apk add --no-cache gcompat

# Download and install Minikube
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64
minikube version
```

### Alternative: Use the install script

The repository provides a script that handles all these cases automatically:

```sh
bash .devcontainer/install-optional-tools.sh
```

This script detects Alpine Linux and applies the appropriate workarounds.

---

### Keep Every Workspace in Sync

Most packages in this monorepo live inside child folders (for example
`core/advisory-database`, `mcp-servers`, and `frontend/ui`). After completing
the steps above, you can fan out the fix and keep every workspace aligned by
running the workspace-aware scripts from the repo root:

```sh
npm install --workspaces
npm run lint --workspaces --if-present
npm test --workspaces --if-present
npm run build --workspaces --if-present
```

These commands ensure that each child folder receives the updated tooling and
re-runs its own script targets immediately, so Copilot (or any other agent) does
not fall back into stale state when it touches different subdirectories.

### If You Can't Use Terminal Commands

For teammates who prefer the VS Code UI (or cannot type commands), use the
built-in tasks provided in this repo:

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) to open the Command Palette.
2. Type **“Run Task”** and press Enter.
3. Pick the task that matches the fix you need:

- **📦 NPM: 安裝依賴** installs Node.js packages for every workspace.
- **🔍 NPM: Lint**, **🧪 NPM: 測試**, and **🔨 NPM: 建置** run lint, tests, and
  builds across all workspaces.

1. Let the task finish; VS Code streams the logs so you can see progress without
   touching the terminal.

These tasks wrap the same commands shown earlier, ensuring non-CLI users can
repair Copilot failures with a few clicks.

### Quick Reference

- Missing `npm` → install Node.js/npm (step 1)
- `npx typescript` EACCES → install global TypeScript (step 3)
- Copilot keeps rerunning failed jobs → rerun lint/tests after the fixes (steps
  2 and 5)
