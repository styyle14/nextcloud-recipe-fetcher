"""Script to run tests with coverage."""

import subprocess
import sys

from pathlib import Path


def main() -> None:
    """Run pytest with coverage reporting."""
    project_root = Path(__file__).parent.parent

    sys.stdout.write("Running tests with coverage...\n")
    result = subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "pytest",
        ],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )

    # Print outputs
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)

    if result.returncode == 0:
        sys.stdout.write("\n✅ All tests passed!\n")
    else:
        sys.stdout.write("\n❌ Tests failed!\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
