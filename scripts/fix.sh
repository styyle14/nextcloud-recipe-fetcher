#!/bin/zsh

# Get the directory containing this script
SCRIPT_DIR=${0:a:h}
PROJECT_ROOT=${SCRIPT_DIR:h}

# Ensure virtual environment exists
if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
    echo "Virtual environment not found. Running setup script first..."
    "${SCRIPT_DIR}/setup.sh"
fi

# Activate virtual environment
source "${PROJECT_ROOT}/.venv/bin/activate"

# Run ruff to fix formatting and linting issues
echo "Running ruff to fix issues..."
ruff check --fix src/ tests/
ruff format src/ tests/

# Show remaining issues that couldn't be auto-fixed
echo -e "\nRemaining issues:"
ruff check src/ tests/ 