"""Script to run linting checks."""
import subprocess
import sys
from pathlib import Path

def main():
    """Run ruff linter and mypy type checker."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    
    print("Running Ruff linter...")
    ruff_result = subprocess.run([
        sys.executable,
        "-m",
        "ruff",
        "check",
        src_dir
    ])
    
    print("\nRunning MyPy type checker...")
    mypy_result = subprocess.run([
        sys.executable,
        "-m",
        "mypy",
        src_dir
    ])
    
    if ruff_result.returncode != 0 or mypy_result.returncode != 0:
        print("\n❌ Checks failed!")
        exit(1)
    
    print("\n✅ All checks passed!")

if __name__ == "__main__":
    main() 