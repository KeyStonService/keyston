#!/usr/bin/env python3
# tools/module_graph_gate.py
# 解析依賴圖、檢測循環、輸出 topo order

import json
import sys
from pathlib import Path
import yaml

def detect_cycle_and_toposort(mods: dict):
    graph = {mid: set((mods[mid].get("dependencies") or [])) for mid in mods}
    temp = set()
    perm = set()
    order = []
    cycle = []

    def visit(n):
        nonlocal cycle
        if n in perm:
            return True
        if n in temp:
            cycle = [n]
            return False
        temp.add(n)
        for d in graph.get(n, []):
            if d not in graph:
                # 依賴不存在也視為錯（Phase 1）
                raise ValueError(f"Unknown dependency: {n} -> {d}")
            if not visit(d):
                cycle.append(n)
                return False
        temp.remove(n)
        perm.add(n)
        order.append(n)
        return True

    for n in graph:
        if n not in perm:
            ok = visit(n)
            if not ok:
                cycle.reverse()
                return False, cycle, []
    return True, [], order

def main():
    repo = Path(".")
    registry_path = repo / "root/registry/root.registry.modules.yaml"
    out_graph = repo / "dist/graph.json"
    out_report = repo / "dist/reports/module-graph.json"
    out_graph.parent.mkdir(parents=True, exist_ok=True)
    out_report.parent.mkdir(parents=True, exist_ok=True)

    reg = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    mods = reg["modules"]

    edges = []
    for m, spec in mods.items():
        for d in spec.get("dependencies") or []:
            edges.append({"from": m, "to": d})

    result = {"gate": "gate-module-graph", "result": "pass", "errors": [], "cycle": []}
    try:
        ok, cycle, order = detect_cycle_and_toposort(mods)
        if not ok:
            result["result"] = "fail"
            result["cycle"] = cycle
        result["topo_order"] = order
    except Exception as e:
        result["result"] = "fail"
        result["errors"].append(str(e))

    graph = {"nodes": list(mods.keys()), "edges": edges}
    out_graph.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    out_report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "pass" else 2

if __name__ == "__main__":
    sys.exit(main())