#!/bin/zsh

# Get the directory containing this script
SCRIPT_DIR=${0:a:h}
PROJECT_ROOT=${SCRIPT_DIR:h}

echo "🚀 Setting up development environment..."

# Check if uv is installed globally
if ! command -v uv &> /dev/null; then
    echo "📥 Installing uv package installer..."
    pip install uv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv "${PROJECT_ROOT}/.venv"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "${PROJECT_ROOT}/.venv/bin/activate"

# Install the project and dev dependencies
echo "📥 Installing project in development mode..."
uv pip install -e ".[dev]"

# Make all shell scripts executable
echo "🔑 Making scripts executable..."
chmod +x "${SCRIPT_DIR}"/*.sh

echo "✨ Setup complete! You can now run:"
echo "  ./scripts/lint.sh  - to run linting"
echo "  ./scripts/test.sh  - to run tests"

echo "🎉 All done! Your development environment is ready." 