#!/usr/bin/env python3
# tools/rootfs_assembler.py
# Phase 1：組裝 dist/rootfs（FHS） + 生成檔案清單 manifest（含來源標註）

import json
import os
import shutil
import sys
from pathlib import Path
import yaml

def copy_tree(src: Path, dst: Path):
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        for d in dirs:
            (dst / rel / d).mkdir(parents=True, exist_ok=True)
        for f in files:
            s = Path(root) / f
            t = dst / rel / f
            t.parent.mkdir(parents=True, exist_ok=True)
            if t.exists():
                # Phase 1：衝突直接 fail
                raise RuntimeError(f"Rootfs path conflict: {t}")
            shutil.copy2(s, t)

def main():
    repo = Path(".")
    reg = yaml.safe_load((repo / "root/registry/root.registry.modules.yaml").read_text(encoding="utf-8"))
    modules = reg["modules"]

    rootfs = repo / "dist/rootfs"
    if rootfs.exists():
        shutil.rmtree(rootfs)
    rootfs.mkdir(parents=True, exist_ok=True)

    # 建立最小 FHS 目錄（避免空目錄被忽略）
    for d in ["bin", "sbin", "etc", "lib", "var", "usr/bin", "usr/lib", "tmp", "opt", "srv", "home"]:
        (rootfs / d).mkdir(parents=True, exist_ok=True)

    manifest = []

    for mid, spec in modules.items():
        frag = spec["install"]["rootfs_fragment"]
        if not frag.get("enabled", False):
            continue
        for rule in frag["paths"]:
            src = repo / rule["from"]
            dst = rootfs / rule["to"].lstrip("/")
            if not src.exists():
                raise RuntimeError(f"Missing rootfs fragment template: {src}")
            copy_tree(src, dst)

    # 產出 tree/manifest（先不 hash，hash 交給 evidence gate）
    for p in sorted(rootfs.rglob("*")):
        if p.is_file():
            manifest.append({"path": str(p.relative_to(rootfs)), "size": p.stat().st_size})

    (repo / "dist/reports").mkdir(parents=True, exist_ok=True)
    (repo / "dist/reports/rootfs.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Assembled rootfs -> {rootfs}")
    return 0

if __name__ == "__main__":
    sys.exit(main())