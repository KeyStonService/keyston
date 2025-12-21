#!/usr/bin/env python3
# tools/evidence_generator.py
# Phase 1：產出 manifest + provenance stub + 簡化 SBOM（檔案清單）+ gate 聚合報告
# 雜湊：sha3-512（權威）+ sha256（相容）

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def hash_file(path: Path):
    h3 = hashlib.sha3_512()
    h2 = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h3.update(b)
            h2.update(b)
    return {"sha3-512": h3.hexdigest(), "sha256": h2.hexdigest()}

def hash_tree(root: Path):
    items = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            items.append({"path": str(p.relative_to(root)), "hash": hash_file(p), "size": p.stat().st_size})
    # tree hash：以（path + sha3-512）串接再 sha3-512（簡單可重播）
    h3 = hashlib.sha3_512()
    for it in items:
        h3.update((it["path"] + ":" + it["hash"]["sha3-512"]).encode("utf-8"))
    return items, {"sha3-512": h3.hexdigest()}

def main():
    repo = Path(".")
    dist = repo / "dist"
    evidence_dir = dist / "evidence"
    reports_dir = dist / "reports"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # 收集 artifacts
    artifacts = []
    artifacts_root = dist / "artifacts"
    if artifacts_root.exists():
        for p in sorted(artifacts_root.rglob("*")):
            if p.is_file():
                artifacts.append({
                    "path": str(p.relative_to(repo)),
                    "hash": hash_file(p),
                    "size": p.stat().st_size
                })

    # 收集 rootfs
    rootfs = dist / "rootfs"
    rootfs_items, rootfs_hash = ([], {"sha3-512": None})
    if rootfs.exists():
        rootfs_items, rootfs_hash = hash_tree(rootfs)

    # Gate reports（若存在就聚合）
    gate_reports = []
    if reports_dir.exists():
        for p in sorted(reports_dir.glob("*.json")):
            try:
                gate_reports.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                pass

    now = datetime.now(timezone.utc).isoformat()
    provenance = {
        "system": "aaps",
        "repo": os.getenv("GITHUB_REPOSITORY", "machine-native-ops-aaps"),
        "commit": os.getenv("GITHUB_SHA", "local"),
        "run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "timestamp": now,
        "hash_policy": {"authoritative": "sha3-512", "compatibility": "sha256"},
        "inputs": {
            "registry": {"path": "root/registry/root.registry.modules.yaml", "hash": hash_file(repo / "root/registry/root.registry.modules.yaml")},
            "schema": {"path": "root/schemas/modules.schema.json", "hash": hash_file(repo / "root/schemas/modules.schema.json")}
        },
        "outputs": {
            "artifacts": artifacts,
            "rootfs": {"path": str(rootfs.relative_to(repo)) if rootfs.exists() else None, "hash": rootfs_hash}
        },
        "gates": gate_reports
    }

    manifest = {
        "generated_at": now,
        "artifacts": artifacts,
        "rootfs_files": rootfs_items,
        "rootfs_tree_hash": rootfs_hash
    }

    # 簡化 SBOM（Phase 1）：用檔案清單 + hash 代表
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "aaps-phase1-sbom",
        "documentNamespace": f"https://example.local/spdx/aaps/{provenance['commit']}",
        "creationInfo": {
            "created": now,
            "creators": ["Tool: aaps-evidence-generator"]
        },
        "packages": [
            {
                "SPDXID": "SPDXRef-Package-AAPS-Rootfs",
                "name": "aaps-rootfs",
                "versionInfo": provenance["commit"],
                "checksums": [{"algorithm": "SHA3-512", "checksumValue": rootfs_hash["sha3-512"]}] if rootfs_hash["sha3-512"] else []
            }
        ],
        "files": [
            {
                "SPDXID": f"SPDXRef-File-{i}",
                "fileName": it["path"],
                "checksums": [
                    {"algorithm": "SHA3-512", "checksumValue": it["hash"]["sha3-512"]},
                    {"algorithm": "SHA256", "checksumValue": it["hash"]["sha256"]}
                ]
            } for i, it in enumerate(rootfs_items[:5000])  # Phase 1 防爆：上限 5000
        ]
    }

    (dist / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (evidence_dir / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
    (evidence_dir / "sbom.spdx.json").write_text(json.dumps(sbom, ensure_ascii=False, indent=2), encoding="utf-8")
    (evidence_dir / "gate-report.json").write_text(json.dumps({"gates": gate_reports}, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Evidence generated under dist/evidence/")
    return 0

if __name__ == "__main__":
    sys.exit(main())