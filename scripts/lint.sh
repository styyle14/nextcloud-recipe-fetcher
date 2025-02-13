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

# Run ruff for linting and formatting
echo "Running ruff..."
ruff check src/ tests/
ruff format src/ tests/

# Run pyright for type checking
echo -e "\nRunning pyright..."
pyright src/ tests/
