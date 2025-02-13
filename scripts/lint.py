"""Script to run linting checks."""

import subprocess
import sys

from pathlib import Path


def main() -> None:
    """Run ruff linter and mypy type checker."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"

    # Run ruff linter
    sys.stdout.write("Running Ruff linter...\n")
    ruff_result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "ruff", "check", src_dir],
        check=False,
        capture_output=True,
        text=True,
    )

    # Run mypy type checker
    sys.stdout.write("\nRunning MyPy type checker...\n")
    mypy_result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "mypy", src_dir],
        check=False,
        capture_output=True,
        text=True,
    )

    # Print outputs
    if ruff_result.stdout:
        sys.stdout.write(ruff_result.stdout)
    if ruff_result.stderr:
        sys.stderr.write(ruff_result.stderr)
    if mypy_result.stdout:
        sys.stdout.write(mypy_result.stdout)
    if mypy_result.stderr:
        sys.stderr.write(mypy_result.stderr)

    if ruff_result.returncode != 0 or mypy_result.returncode != 0:
        sys.stdout.write("\n❌ Checks failed!\n")
        sys.exit(1)

    sys.stdout.write("\n✅ All checks passed!\n")


if __name__ == "__main__":
    main()
