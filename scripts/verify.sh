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
echo "  3. Python Test Suite (secure-url-fetcher & pdf-security-scanner)"
echo "======================================================================"
if command -v uv >/dev/null 2>&1; then
  uv run skills/secure-url-fetcher/run_tests.py
  uv run skills/pdf-security-scanner/run_tests.py
elif command -v python3 >/dev/null 2>&1; then
  python3 skills/secure-url-fetcher/run_tests.py
  python3 skills/pdf-security-scanner/run_tests.py
else
  echo "  ⚠️ Warning: neither uv nor python3 found; skipping python tests."
fi

echo ""
echo "======================================================================"
echo "  4. Shell Scripts & Installer Verification"
echo "======================================================================"
bash -n scripts/install-guardrails.sh
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck scripts/install-guardrails.sh scripts/verify.sh
fi

# Run isolated functional tests for install-guardrails.sh
TEST_HOME="$(mktemp -d 2>/dev/null || mktemp -t 'test_home')"
cleanup_test_home() {
  rm -rf "${TEST_HOME:-}"
}
trap cleanup_test_home INT TERM EXIT

# 4a. Default install
HOME="${TEST_HOME}" ./scripts/install-guardrails.sh --all >/dev/null
test -f "${TEST_HOME}/.gemini/config/AGENTS.md"
test -f "${TEST_HOME}/.agents/AGENTS.md"
grep -q "Global Guardrails: Code Is Law" "${TEST_HOME}/.gemini/config/AGENTS.md"

# 4b. Symlink mode
rm -rf "${TEST_HOME}/.agents"
HOME="${TEST_HOME}" ./scripts/install-guardrails.sh --symlink >/dev/null
test -L "${TEST_HOME}/.agents/AGENTS.md"
test "$(readlink "${TEST_HOME}/.agents/AGENTS.md")" = "${TEST_HOME}/.gemini/config/AGENTS.md"

# 4c. Negative branch (invalid option exits 1)
set +e
HOME="${TEST_HOME}" ./scripts/install-guardrails.sh --invalid-flag >/dev/null 2>&1
INVALID_STATUS=$?
set -e
test "${INVALID_STATUS}" -eq 1

cleanup_test_home
trap - INT TERM EXIT

echo "  ✅ Shell syntax, shellcheck, and installer tests passed."

echo ""
echo "======================================================================"
echo "  🎉 All verification checks passed successfully!"
echo "======================================================================"
