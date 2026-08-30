import subprocess
from pathlib import Path

def run_command(args: list[str], root: Path) -> tuple[int, str, str]:
    proc = subprocess.run(args, cwd=root, text=True, capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr
