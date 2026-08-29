#!/usr/bin/env bash
# scripts/verify.sh
# Comprehensive verification gate: Privacy/PII Audit + Python Tests + Node Tests.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

echo "======================================================================"
echo "  1. Privacy & Zero-PII Audit"
echo "======================================================================"

# Check for accidental hardcoded local user paths or names
if git grep -I -E "(/Users/[a-zA-Z0-9_-]+|/home/[a-zA-Z0-9_-]+)" -- ':!scripts/verify.sh' ':!.git' >/dev/null 2>&1; then
  echo "  ❌ ERROR: Potential hardcoded local user path found in repository:"
  git grep -I -E "(/Users/[a-zA-Z0-9_-]+|/home/[a-zA-Z0-9_-]+)" -- ':!scripts/verify.sh' ':!.git'
  exit 1
fi

echo "  ✅ Privacy audit passed: 0 host/user leaks detected."

echo ""
echo "======================================================================"
echo "  2. Node.js Test Suite (web-search)"
echo "======================================================================"
node skills/web-search/run_tests.mjs

echo ""
echo "======================================================================"
echo "  3. Python Test Suite (secure-url-fetcher)"
echo "======================================================================"
if command -v uv >/dev/null 2>&1; then
  uv run skills/secure-url-fetcher/run_tests.py
elif command -v python3 >/dev/null 2>&1; then
  python3 skills/secure-url-fetcher/run_tests.py
else
  echo "  ⚠️ Warning: neither uv nor python3 found; skipping python tests."
fi

echo ""
echo "======================================================================"
echo "  🎉 All verification checks passed successfully!"
echo "======================================================================"
