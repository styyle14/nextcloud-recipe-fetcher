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

# Create docs directory if it doesn't exist
DOCS_DIR="${PROJECT_ROOT}/docs"
if [ ! -d "$DOCS_DIR" ]; then
    echo "Creating Sphinx documentation structure..."
    mkdir -p "$DOCS_DIR"
    cd "$DOCS_DIR"
    sphinx-quickstart -q \
        -p "Recipito" \
        -a "Your Name" \
        -v "0.1.1" \
        -r "0.1.1" \
        -l "en" \
        --ext-autodoc \
        --ext-viewcode \
        --ext-napoleon \
        --sep
fi

# Update conf.py with theme and extensions
cat > "${DOCS_DIR}/source/conf.py" << 'EOL'
import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

project = 'Recipito'
copyright = '2024, Your Name'
author = 'Your Name'
release = '0.1.1'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
napoleon_google_docstring = True
napoleon_numpy_docstring = False
EOL

# Create index.rst
cat > "${DOCS_DIR}/source/index.rst" << 'EOL'
Welcome to Recipito's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
EOL

# Generate API documentation
cd "$DOCS_DIR"
sphinx-apidoc -f -o source/ ../src/recipito/

# Build HTML documentation
make html

echo "✨ Documentation built in docs/build/html/" 