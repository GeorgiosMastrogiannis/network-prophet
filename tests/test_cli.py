import json
from pathlib import Path
import subprocess
import sys


def test_cli_reports_inspection_only():
    path = Path(__file__).parents[1] / "fixtures/subnet-change.json"
    result = subprocess.run([sys.executable, "-m", "network_guardian.cli", str(path)], capture_output=True, text=True)
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "inspection_only"


def test_cli_missing_file_is_input_error(tmp_path):
    result = subprocess.run([sys.executable, "-m", "network_guardian.cli", str(tmp_path / "missing.json")], capture_output=True, text=True)
    assert result.returncode == 2
    assert "error:" in result.stderr
