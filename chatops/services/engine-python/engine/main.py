#!/usr/bin/env python3
import argparse
import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
from pathlib import Path

NAME_PATTERN = re.compile(r"^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\d+\.\d+\.\d+(-[A-Za-z0-9]+)?$")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def discovery(root: Path):
    items = []
    if not root.exists():
        return {"ts": now_iso(), "root": str(root), "resources": [], "summary": {"total": 0, "compliant": 0, "noncompliant": 0, "compliance_rate": 100.0}}
    for p in root.rglob("*.y*ml"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        kind = None
        name = None
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("kind:"):
                kind = s.split(":", 1)[1].strip()
            if s.startswith("name:") and name is None:
                name = s.split(":", 1)[1].strip().strip('"').strip("'")
        if kind and name:
            ok = bool(NAME_PATTERN.match(name))
            items.append({"file": str(p), "kind": kind, "name": name, "pattern": NAME_PATTERN.pattern, "compliant": ok})

    total = len(items)
    compliant = len([x for x in items if x["compliant"]])
    summary = {
        "total": total,
        "compliant": compliant,
        "noncompliant": total - compliant,
        "compliance_rate": round((compliant / total) * 100, 2) if total else 100.0,
    }
    return {"ts": now_iso(), "root": str(root), "resources": items, "summary": summary}

class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: str, ctype: str = "application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        if self.path == "/healthz":
            self._send(200, json.dumps({"ok": True, "ts": now_iso()}))
            return

        if self.path == "/metrics":
            # Minimal metrics (in real prod, integrate with full observability stack)
            root = Path(os.getenv("DISCOVERY_ROOT", "deployments"))
            rep = discovery(root)
            env = os.getenv("ENV", "prod")
            rate = float(rep["summary"]["compliance_rate"]) / 100.0
            violations = int(rep["summary"]["noncompliant"])
            lines = [
                f'chatops_naming_compliance_rate{{env="{env}"}} {rate}',
                f'chatops_naming_violations_total{{env="{env}"}} {violations}',
                f'chatops_naming_autofix_success_rate{{env="{env}"}} 0',
                f'chatops_naming_autofix_failure_rate{{env="{env}"}} 0',
            ]
            self._send(200, "\n".join(lines) + "\n", "text/plain; version=0.0.4; charset=utf-8")
            return

        if self.path == "/api/naming/discovery":
            root = Path(os.getenv("DISCOVERY_ROOT", "deployments"))
            rep = discovery(root)
            rep["trace_id"] = os.getenv("TRACE_ID", "trace-service")
            self._send(200, json.dumps(rep, ensure_ascii=False))
            return

        self._send(404, json.dumps({"error": "not found"}))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")))
    args = ap.parse_args()

    httpd = HTTPServer((args.host, args.port), Handler)
    print(f"engine-python listening on {args.host}:{args.port}")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
