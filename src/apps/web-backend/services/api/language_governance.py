"""
Language Governance API Service
Provides real-time governance data for the dashboard
"""

import json
from datetime import datetime
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Language Governance API",
    description="API for Language Governance Dashboard",
    version="1.0.0"
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Violation(BaseModel):
    file: str
    reason: str
    severity: str
    layer: str | None = None


class SemgrepResult(BaseModel):
    check_id: str
    path: str
    message: str
    severity: str


class SemgrepReport(BaseModel):
    errors: int
    results: list[SemgrepResult]


class HistoryEvent(BaseModel):
    timestamp: str
    event: str
    details: str
    type: str


class Metrics(BaseModel):
    totalViolations: int
    securityFindings: int
    architectureCompliance: int
    fixSuccessRate: int


class GovernanceReport(BaseModel):
    healthScore: int
    violations: list[Violation]
    semgrep: SemgrepReport
    history: list[HistoryEvent]
    generatedAt: str
    metrics: Metrics


def get_project_root() -> Path:
    """Get the project root directory"""
    current = Path(__file__).resolve()
    # Navigate up to project root
    for parent in current.parents:
        if (parent / 'governance').exists():
            return parent
    return Path.cwd()


def extract_violations_from_markdown(md_content: str) -> list[Violation]:
    """Extract violations from markdown governance report"""
    violations = []
    lines = md_content.split('\n')
    
    for line in lines:
        if '❌' in line or 'violation' in line.lower():
            # Try to parse violation from markdown
            parts = line.split('—')
            if len(parts) >= 2:
                file_part = parts[0].strip('- *').strip()
                reason_part = parts[1].strip() if len(parts) > 1 else 'Unknown violation'
                
                severity = 'warning'
                if 'critical' in line.lower():
                    severity = 'critical'
                elif 'error' in line.lower():
                    severity = 'error'
                
                violations.append(Violation(
                    file=file_part,
                    reason=reason_part,
                    severity=severity
                ))
    
    return violations


def load_governance_report() -> GovernanceReport:
    """Load governance report from files or return mock data"""
    project_root = get_project_root()
    
    # Try to load real data
    gov_path = project_root / 'governance' / 'language-governance-report.md'
    semgrep_path = project_root / 'governance' / 'semgrep-report.json'
    history_path = project_root / 'knowledge' / 'language-history.yaml'
    health_path = project_root / 'docs' / 'KNOWLEDGE_HEALTH.md'
    
    violations = []
    semgrep_data = {'errors': 0, 'results': []}
    history = []
    health_score = 85
    
    # Try to load violations from governance report
    if gov_path.exists():
        try:
            with open(gov_path, encoding='utf-8') as f:
                content = f.read()
                violations = extract_violations_from_markdown(content)
        except Exception as e:
            print(f"Error reading governance report: {e}")
    
    # Try to load semgrep results
    if semgrep_path.exists():
        try:
            with open(semgrep_path, encoding='utf-8') as f:
                data = json.load(f)
                semgrep_data = {
                    'errors': data.get('errors', 0),
                    'results': [
                        SemgrepResult(
                            check_id=r.get('check_id', 'unknown'),
                            path=r.get('path', 'unknown'),
                            message=r.get('extra', {}).get('message', 'No message'),
                            severity=r.get('extra', {}).get('severity', 'WARNING')
                        )
                        for r in data.get('results', [])[:10]  # Limit to 10 results
                    ]
                }
        except Exception as e:
            print(f"Error reading semgrep report: {e}")
    
    # Try to load history
    if history_path.exists():
        try:
            with open(history_path, encoding='utf-8') as f:
                history_data = yaml.safe_load(f)
                if isinstance(history_data, list):
                    history = [
                        HistoryEvent(
                            timestamp=event.get('timestamp', datetime.now().isoformat()),
                            event=event.get('event', 'Event'),
                            details=event.get('details', ''),
                            type=event.get('type', 'scan')
                        )
                        for event in history_data[:10]  # Limit to 10 events
                    ]
        except Exception as e:
            print(f"Error reading history: {e}")
    
    # Try to extract health score
    if health_path.exists():
        try:
            with open(health_path, encoding='utf-8') as f:
                content = f.read()
                # Look for score pattern like "85/100"
                import re
                match = re.search(r'(\d+)/100', content)
                if match:
                    health_score = int(match.group(1))
        except Exception as e:
            print(f"Error reading health score: {e}")
    
    # If no data found, return mock data
    if not violations:
        violations = [
            Violation(
                file='apps/web/src/legacy-code.js',
                reason='JavaScript file in TypeScript project',
                severity='warning',
                layer='L5: Applications'
            ),
            Violation(
                file='core/engine/utils.py',
                reason='Python file needs type hints',
                severity='error',
                layer='L1: Core Engine'
            )
        ]
    
    if not semgrep_data['results']:
        semgrep_data = {
            'errors': 1,
            'results': [
                SemgrepResult(
                    check_id='javascript.lang.security.audit.xss',
                    path='apps/web/src/utils/render.ts',
                    message='Potential XSS vulnerability detected',
                    severity='WARNING'
                )
            ]
        }
    
    if not history:
        history = [
            HistoryEvent(
                timestamp=datetime.now().isoformat(),
                event='Auto-fix applied',
                details='Fixed 3 TypeScript violations in core module',
                type='fix'
            ),
            HistoryEvent(
                timestamp=datetime.now().isoformat(),
                event='Language scan completed',
                details='Scanned 1,247 files across 6 layers',
                type='scan'
            ),
            HistoryEvent(
                timestamp=datetime.now().isoformat(),
                event='New violation detected',
                details='Cross-layer import violation in governance module',
                type='violation'
            )
        ]
    
    return GovernanceReport(
        healthScore=health_score,
        violations=violations,
        semgrep=SemgrepReport(**semgrep_data),
        history=history,
        generatedAt=datetime.now().isoformat(),
        metrics=Metrics(
            totalViolations=len(violations),
            securityFindings=len(semgrep_data['results']),
            architectureCompliance=92,
            fixSuccessRate=87
        )
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Language Governance API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/api/language-governance", response_model=GovernanceReport)
async def get_language_governance():
    """Get language governance report"""
    try:
        report = load_governance_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
