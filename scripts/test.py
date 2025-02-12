"""Script to run tests with coverage."""
import subprocess
import sys
from pathlib import Path

def main():
    """Run pytest with coverage reporting."""
    project_root = Path(__file__).parent.parent
    
    print("Running tests with coverage...")
    result = subprocess.run([
        sys.executable,  # Use the current Python interpreter
        "-m",  # Run module as script
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/",
    ], cwd=project_root)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        exit(1)

if __name__ == "__main__":
    main() 