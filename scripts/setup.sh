#!/bin/bash
# PrettyDiagrams — Setup Script
# Creates venv and installs dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PLUGIN_ROOT"

echo "PrettyDiagrams Setup"
echo "===================="

# Check Python
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "ERROR: Python 3.11+ required but not found"
    exit 1
fi

PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python: $PYTHON ($PY_VERSION)"

# Create venv if missing
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv .venv
fi

# Install deps
echo "Installing dependencies..."
.venv/bin/pip install -q -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Create .env with your API key:"
echo "     echo 'PRETTYDIAGRAMS_BACKEND=gemini' > $PLUGIN_ROOT/.env"
echo "     echo 'GEMINI_API_KEY=your-key-here' >> $PLUGIN_ROOT/.env"
echo "  2. Optional: Add KIE_API_KEY as fallback backend"
echo "  3. Optional: Add TAVILY_API_KEY for reference image search"
echo ""
