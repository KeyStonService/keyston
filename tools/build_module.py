#!/usr/bin/env python3
# tools/build_module.py
# Phase 1：建置單一 python wheel 模組（python -m build），輸出到 dist/artifacts/...

import shutil
import subprocess
import sys
from pathlib import Path
import yaml

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return p.stdout

def main():
    if len(sys.argv) != 2:
        print("Usage: tools/build_module.py <module-id>")
        return 2

    module_id = sys.argv[1]
    repo = Path(".")
    reg = yaml.safe_load((repo / "root/registry/root.registry.modules.yaml").read_text(encoding="utf-8"))
    spec = reg["modules"][module_id]
    version = spec["version"]
    context = repo / spec["build"]["context"]

    out_dir = repo / "dist/artifacts" / module_id / version
    out_dir.mkdir(parents=True, exist_ok=True)

    # 建置 wheel：需要 build 套件（pip install build）
    # 輸出會在 <context>/dist/
    run([sys.executable, "-m", "build", "--wheel"], cwd=str(context))

    built_dist = context / "dist"
    wheels = list(built_dist.glob("*.whl"))
    if not wheels:
        raise RuntimeError("No wheel produced in engine module dist/")

    for whl in wheels:
        shutil.copy2(whl, out_dir / whl.name)

    print(f"Built wheels -> {out_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())