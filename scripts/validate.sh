#!/bin/bash

# Exit on error
set -e

echo "Running fix.sh..."
./scripts/fix.sh

echo -e "\nRunning lint.sh..."
./scripts/lint.sh

echo -e "\nRunning test.sh..."
./scripts/test.sh

echo -e "\n✅ All validation passed!" 