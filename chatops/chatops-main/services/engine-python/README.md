# engine-python

Local HTTP service:
- `/healthz`
- `/metrics` (Prometheus text format)
- `/api/naming/discovery` (runs discovery on deployments/)

Run:
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m engine.main --port 8080
```
