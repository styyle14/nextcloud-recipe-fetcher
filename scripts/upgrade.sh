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

# Run pyupgrade on all Python files in src/
echo "Running pyupgrade..."
find "${PROJECT_ROOT}/src" -name "*.py" -exec pyupgrade --py39-plus {} \; 