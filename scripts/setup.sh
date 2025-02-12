#!/bin/zsh

# Get the directory containing this script
SCRIPT_DIR=${0:a:h}
PROJECT_ROOT=${SCRIPT_DIR:h}

echo "🚀 Setting up development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "pip install uv"
    exit 1
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

# Install dependencies
echo "📥 Installing development dependencies..."
uv pip install -e ".[dev]"

echo "✨ Setup complete! You can now run:"
echo "  ./scripts/lint.sh  - to run linting"
echo "  ./scripts/test.sh  - to run tests"

# Make all shell scripts executable
echo "🔑 Making scripts executable..."
chmod +x "${SCRIPT_DIR}"/*.sh

echo "🎉 All done! Your development environment is ready." 