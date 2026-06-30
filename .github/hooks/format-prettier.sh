#!/bin/bash
# Post-tool ruff formatter hook
# Runs ruff format on Python files after tool execution
# Exits with 0 on success, 1 on error, 2 on blocking error

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Determine workspace root (parent of .github)
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT" || { echo "Failed to change to repo root"; exit 2; }

# Check if uv is available
if ! command -v uv &> /dev/null; then
  echo -e "${YELLOW}uv not found. Skipping auto-format.${NC}" >&2
  exit 0
fi

# Check if ruff is available in the venv
if ! uv run ruff --version &> /dev/null; then
  echo -e "${YELLOW}ruff not found in venv. Run: uv sync. Skipping auto-format.${NC}" >&2
  exit 0
fi

echo -e "${YELLOW}Formatting Python files with ruff...${NC}" >&2

if uv run ruff format . > /dev/null 2>&1; then
  echo -e "${GREEN}✓ ruff formatting complete.${NC}" >&2
  exit 0
else
  echo -e "${RED}✗ ruff formatting failed.${NC}" >&2
  exit 1
fi
