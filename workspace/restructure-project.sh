#!/bin/bash
# 項目重構腳本：將根層簡化為 FHS 骨架 + 引導文件

set -e

echo "🚀 開始項目重構..."
echo "=" | tr '=' '=' | head -c 60; echo

# 定義 FHS 標準目錄（保留在根層）
FHS_DIRS=("bin" "sbin" "etc" "lib" "var" "usr" "home" "tmp" "opt" "srv" "init.d")

# 定義引導文件（保留在根層）
BOOTSTRAP_FILES=("root.bootstrap.yaml" "root.fs.map" "root.env.sh")

# 定義需要移到 controlplane/config/ 的文件
CONTROLPLANE_CONFIG_FILES=(
    "root.config.yaml"
    "root.governance.yaml"
    "root.modules.yaml"
    "root.super-execution.yaml"
    "root.trust.yaml"
    "root.provenance.yaml"
    "root.integrity.yaml"
    "root.naming-policy.yaml"
    "root.devices.map"
    "root.kernel.map"
)

# 定義需要移到 controlplane/specifications/ 的文件
CONTROLPLANE_SPECS_FILES=(
    "root.specs.naming.yaml"
    "root.specs.references.yaml"
    "root.specs.mapping.yaml"
    "root.specs.logic.yaml"
    "root.specs.context.yaml"
)

# 定義需要移到 controlplane/registries/ 的文件
CONTROLPLANE_REGISTRIES_FILES=(
    "root.registry.modules.yaml"
    "root.registry.urns.yaml"
)

# 定義需要移到 controlplane/validation/ 的文件
CONTROLPLANE_VALIDATION_FILES=(
    "root.validator.schema.yaml"
    "validate-root-specs.py"
    "verify_refactoring.py"
    "supply-chain-complete-verifier.py"
)

# 定義需要移到 workspace/ 的目錄
WORKSPACE_DIRS=(
    "archive"
    "cloudflare"
    "config"
    "deploy"
    "docs"
    "engine"
    "examples"
    "governance"
    "ops"
    "outputs"
    "root"
    "schemas"
    "scripts"
    "src"
    "teams"
    "templates"
    "tests"
    "tools"
)

echo "📋 步驟 1: 移動文件到 controlplane/"
echo ""

# 移動配置文件到 controlplane/config/
echo "  → 移動配置文件到 controlplane/config/..."
for file in "${CONTROLPLANE_CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" controlplane/config/
        echo "    ✅ $file"
    fi
done

# 移動規格文件到 controlplane/specifications/
echo "  → 移動規格文件到 controlplane/specifications/..."
for file in "${CONTROLPLANE_SPECS_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" controlplane/specifications/
        echo "    ✅ $file"
    fi
done

# 移動註冊文件到 controlplane/registries/
echo "  → 移動註冊文件到 controlplane/registries/..."
for file in "${CONTROLPLANE_REGISTRIES_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" controlplane/registries/
        echo "    ✅ $file"
    fi
done

# 移動驗證文件到 controlplane/validation/
echo "  → 移動驗證文件到 controlplane/validation/..."
for file in "${CONTROLPLANE_VALIDATION_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" controlplane/validation/
        echo "    ✅ $file"
    fi
done

echo ""
echo "📋 步驟 2: 移動目錄到 workspace/"
echo ""

# 移動目錄到 workspace/
for dir in "${WORKSPACE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        mv "$dir" workspace/
        echo "  ✅ $dir/"
    fi
done

echo ""
echo "📋 步驟 3: 移動其他文件到 workspace/"
echo ""

# 移動所有其他文件到 workspace/（排除 FHS 目錄、引導文件、隱藏文件）
for item in *; do
    # 跳過目錄
    [ -d "$item" ] && continue
    
    # 跳過隱藏文件
    [[ "$item" == .* ]] && continue
    
    # 跳過引導文件
    skip=false
    for bootstrap in "${BOOTSTRAP_FILES[@]}"; do
        if [ "$item" == "$bootstrap" ]; then
            skip=true
            break
        fi
    done
    [ "$skip" = true ] && continue
    
    # 移動到 workspace/
    if [ -f "$item" ]; then
        mv "$item" workspace/
        echo "  ✅ $item"
    fi
done

echo ""
echo "📋 步驟 4: 創建引導文件"
echo ""

# 創建 root.bootstrap.yaml
cat > root.bootstrap.yaml << 'EOF'
# Root Bootstrap Configuration
# 根層引導配置 - 只負責指向 controlplane 入口

apiVersion: root.bootstrap/v1
kind: RootBootstrap

metadata:
  name: machine-native-ops-bootstrap
  version: v1.0.0
  description: Root layer bootstrap configuration for MachineNativeOps

controlplane:
  # Controlplane 路徑
  path: "./controlplane"
  
  # 必需文件檢查
  requiredFiles:
    - "config/root.config.yaml"
    - "config/root.governance.yaml"
    - "registries/root.registry.modules.yaml"
    - "validation/root.validator.schema.yaml"
  
  # 入口點配置
  entrypoint:
    superExecution: "config/root.super-execution.yaml"
    governance: "config/root.governance.yaml"
    modules: "config/root.modules.yaml"
  
  # 版本鎖定
  versionLock:
    controlplaneVersion: "v1.0.0"
    minCompatibleVersion: "v1.0.0"

# 啟動模式
bootMode:
  mode: "production"  # production | development | testing
  strictValidation: true
  autoRepair: false

# 健康檢查
healthCheck:
  enabled: true
  interval: 60  # seconds
  timeout: 10   # seconds
EOF
echo "  ✅ root.bootstrap.yaml"

# 創建 root.fs.map
cat > root.fs.map << 'EOF'
# Root Filesystem Mapping
# 根層文件系統映射 - 只負責 controlplane 掛載

apiVersion: root.fs.map/v1
kind: FilesystemMapping

metadata:
  name: root-filesystem-mapping
  version: v1.0.0

# 掛載點配置
mounts:
  - name: controlplane
    from: "./controlplane"
    to: "/controlplane"
    mode: "ro"  # read-only during runtime
    description: "Control plane configuration and governance"
  
  - name: workspace
    from: "./workspace"
    to: "/workspace"
    mode: "rw"  # read-write
    description: "Working directory for all project files"

# FHS 標準目錄映射
fhsDirectories:
  - name: bin
    path: "./bin"
    description: "Essential user command binaries"
  
  - name: sbin
    path: "./sbin"
    description: "System administration binaries"
  
  - name: etc
    path: "./etc"
    description: "System configuration files"
  
  - name: lib
    path: "./lib"
    description: "Shared libraries"
  
  - name: var
    path: "./var"
    description: "Variable data"
  
  - name: usr
    path: "./usr"
    description: "User programs"
  
  - name: home
    path: "./home"
    description: "User home directories"
  
  - name: tmp
    path: "./tmp"
    description: "Temporary files"
  
  - name: opt
    path: "./opt"
    description: "Optional application packages"
  
  - name: srv
    path: "./srv"
    description: "Service data"
  
  - name: init.d
    path: "./init.d"
    description: "Initialization scripts"
EOF
echo "  ✅ root.fs.map"

# 創建 root.env.sh
cat > root.env.sh << 'EOF'
#!/bin/bash
# Root Environment Configuration
# 根層環境配置 - 只負責啟動時環境變數

# Controlplane 路徑
export CONTROLPLANE_PATH="./controlplane"
export CONTROLPLANE_CONFIG="${CONTROLPLANE_PATH}/config"
export CONTROLPLANE_SPECS="${CONTROLPLANE_PATH}/specifications"
export CONTROLPLANE_REGISTRIES="${CONTROLPLANE_PATH}/registries"
export CONTROLPLANE_VALIDATION="${CONTROLPLANE_PATH}/validation"

# Workspace 路徑
export WORKSPACE_PATH="./workspace"

# FHS 路徑
export FHS_BIN="./bin"
export FHS_SBIN="./sbin"
export FHS_ETC="./etc"
export FHS_LIB="./lib"
export FHS_VAR="./var"
export FHS_USR="./usr"
export FHS_HOME="./home"
export FHS_TMP="./tmp"
export FHS_OPT="./opt"
export FHS_SRV="./srv"
export FHS_INITD="./init.d"

# 啟動模式
export BOOT_MODE="${BOOT_MODE:-production}"

# 版本信息
export MACHINENATIVEOPS_VERSION="v1.0.0"
export CONTROLPLANE_VERSION="v1.0.0"

echo "✅ MachineNativeOps 環境已加載"
echo "   Controlplane: ${CONTROLPLANE_PATH}"
echo "   Workspace: ${WORKSPACE_PATH}"
echo "   Boot Mode: ${BOOT_MODE}"
EOF
chmod +x root.env.sh
echo "  ✅ root.env.sh"

echo ""
echo "=" | tr '=' '=' | head -c 60; echo
echo "✅ 項目重構完成！"
echo ""
echo "📊 重構結果："
echo "  根層 FHS 目錄: $(ls -d */ 2>/dev/null | grep -E "^(bin|sbin|etc|lib|var|usr|home|tmp|opt|srv|init\.d)/" | wc -l) 個"
echo "  引導文件: $(ls root.*.{yaml,map,sh} 2>/dev/null | wc -l) 個"
echo "  Controlplane 文件: $(find controlplane -type f 2>/dev/null | wc -l) 個"
echo "  Workspace 項目: $(ls -1 workspace 2>/dev/null | wc -l) 個"
echo ""
echo "🎯 下一步："
echo "  1. 檢查重構結果: ls -la"
echo "  2. 驗證 controlplane: ls -la controlplane/"
echo "  3. 驗證 workspace: ls -la workspace/"
echo "  4. 提交變更: git add . && git commit -m 'refactor: Restructure to FHS + controlplane + workspace'"