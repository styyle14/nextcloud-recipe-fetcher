"""Installation script for development environment."""
import subprocess
import sys
from pathlib import Path

def main():
    """Install the project in development mode with all dependencies."""
    project_root = Path(__file__).parent.parent
    
    try:
        print("Installing project in development mode with all dependencies...")
        subprocess.run(
            [sys.executable, "-m", "uv", "pip", "install", "-e", ".[dev]"],
            cwd=project_root,
            check=True,
        )
        print("Installation completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 