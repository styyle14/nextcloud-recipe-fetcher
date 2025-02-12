#!/bin/zsh

# Get the directory containing this script
SCRIPT_DIR=${0:a:h}
PROJECT_ROOT=${SCRIPT_DIR:h}

# Create virtual environment if it doesn't exist
if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
    echo "Creating virtual environment..."
    uv venv "${PROJECT_ROOT}/.venv"
fi

# Activate virtual environment
source "${PROJECT_ROOT}/.venv/bin/activate"

# Run the Python install script
python "${SCRIPT_DIR}/install.py" 