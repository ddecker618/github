import subprocess
import sys
from pathlib import Path


def test_cli_module_mode_init_db(tmp_path):
    db_path = tmp_path / "module_mode.db"
    cmd = [sys.executable, "-m", "personnel_scrubber.cli", "--db", str(db_path), "init-db"]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert db_path.exists()
    assert "Initialized database" in result.stdout


def test_cli_script_mode_init_db(tmp_path):
    db_path = tmp_path / "script_mode.db"
    cli_path = Path("personnel_scrubber") / "cli.py"
    cmd = [sys.executable, str(cli_path), "--db", str(db_path), "init-db"]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert db_path.exists()
    assert "Initialized database" in result.stdout
