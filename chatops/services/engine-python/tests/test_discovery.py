from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.main import discovery

def test_discovery_empty(tmp_path: Path):
    rep = discovery(tmp_path / "missing")
    assert rep["summary"]["total"] == 0
    assert rep["summary"]["compliance_rate"] == 100.0
