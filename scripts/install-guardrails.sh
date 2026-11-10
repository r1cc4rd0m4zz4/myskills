#!/usr/bin/env bash
# scripts/install-guardrails.sh
# Dual-mode installer for AGENTS.md guardrails (Antigravity CLI & Generic Agents).
# Works both locally (BASH_SOURCE) and remotely via pipe (curl -fsSL ... | bash).

set -euo pipefail

TMP_FILE="$(mktemp 2>/dev/null || mktemp -t 'agents_md')"
cleanup() {
  rm -f "${TMP_FILE:-}"
}
trap cleanup INT TERM EXIT

TARGET="all"
USE_SYMLINK=0
MODE="append"

usage() {
  cat <<'EOF'
Usage: install-guardrails.sh [OPTIONS]

Dual-mode installer for AGENTS.md universal guardrails.

Options:
  --all         Install for both Antigravity CLI and generic agents (default)
  --agy         Install only for Antigravity CLI (~/.gemini/config/AGENTS.md)
  --generic     Install only for generic agents (~/.agents/AGENTS.md)
  --symlink     Canonicalize ~/.gemini/config/AGENTS.md and symlink ~/.agents/AGENTS.md
  --replace     Overwrite target file instead of appending
  --append      Append guardrails to target file if not present (default)
  -h, --help    Show this help message
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      TARGET="all"
      shift
      ;;
    --agy)
      TARGET="agy"
      shift
      ;;
    --generic)
      TARGET="generic"
      shift
      ;;
    --symlink)
      USE_SYMLINK=1
      shift
      ;;
    --replace)
      MODE="replace"
      shift
      ;;
    --append)
      MODE="append"
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Error: unrecognized option '$1'" >&2
      exit 1
      ;;
  esac
done

# Resolve template content (local repository or remote download)
SCRIPT_SOURCE="${BASH_SOURCE[0]:-}"
LOCAL_TEMPLATE=""

if [[ -n "${SCRIPT_SOURCE}" && -f "${SCRIPT_SOURCE}" ]]; then
  LOCAL_REPO="$(cd "$(dirname "${SCRIPT_SOURCE}")/.." 2>/dev/null && pwd)"
  if [[ -f "${LOCAL_REPO}/templates/AGENTS.md" ]]; then
    LOCAL_TEMPLATE="${LOCAL_REPO}/templates/AGENTS.md"
  fi
elif [[ -f "./templates/AGENTS.md" ]]; then
  LOCAL_TEMPLATE="./templates/AGENTS.md"
fi

if [[ -n "${LOCAL_TEMPLATE}" ]]; then
  cp "${LOCAL_TEMPLATE}" "${TMP_FILE}"
else
  TEMPLATE_URL="${GUARDRAILS_TEMPLATE_URL:-https://raw.githubusercontent.com/r1cc4rd0m4zz4/myskills/main/templates/AGENTS.md}"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --connect-timeout 10 "${TEMPLATE_URL}" -o "${TMP_FILE}"
  elif command -v wget >/dev/null 2>&1; then
    wget -q --timeout=10 -O "${TMP_FILE}" "${TEMPLATE_URL}"
  else
    echo "Error: neither curl nor wget found to download guardrails template." >&2
    exit 1
  fi
fi

if [[ ! -s "${TMP_FILE}" ]]; then
  echo "Error: guardrails template is empty or failed to download." >&2
  exit 1
fi

AGY_DEST="${HOME}/.gemini/config/AGENTS.md"
GENERIC_DEST="${HOME}/.agents/AGENTS.md"

install_file() {
  local dest="$1"
  local dest_dir
  dest_dir="$(dirname "${dest}")"
  mkdir -p "${dest_dir}"

  if [[ "${MODE}" == "replace" || ! -f "${dest}" ]]; then
    cp "${TMP_FILE}" "${dest}"
    echo "  ✅ Installed guardrails in ${dest}"
  else
    if grep -Fq "Global Guardrails: Code Is Law" "${dest}"; then
      echo "  ℹ️  Guardrails already present in ${dest} (skipped)"
    else
      # Ensure clean newline separation before appending
      if [[ -s "${dest}" ]] && [[ -n "$(tail -c 1 "${dest}")" ]]; then
        printf "\n\n" >> "${dest}"
      else
        printf "\n" >> "${dest}"
      fi
      cat "${TMP_FILE}" >> "${dest}"
      echo "  ✅ Appended guardrails to ${dest}"
    fi
  fi
}

link_generic_to_agy() {
  mkdir -p "${HOME}/.agents"
  if [[ -L "${GENERIC_DEST}" ]]; then
    local current_target
    current_target="$(readlink "${GENERIC_DEST}")"
    if [[ "${current_target}" == "${AGY_DEST}" ]]; then
      echo "  ℹ️  Symlink already up to date: ${GENERIC_DEST} -> ${AGY_DEST}"
      return
    fi
    rm -f "${GENERIC_DEST}"
  elif [[ -f "${GENERIC_DEST}" ]]; then
    if cmp -s "${GENERIC_DEST}" "${AGY_DEST}"; then
      rm -f "${GENERIC_DEST}"
    else
      mv "${GENERIC_DEST}" "${GENERIC_DEST}.bak"
      echo "  ⚠️  Preserved existing ${GENERIC_DEST} as ${GENERIC_DEST}.bak"
    fi
  fi
  ln -sf "${AGY_DEST}" "${GENERIC_DEST}"
  echo "  🔗 Linked: ${GENERIC_DEST} -> ${AGY_DEST}"
}

echo "==> Universal Agent Guardrails Installer"

if [[ ${USE_SYMLINK} -eq 1 ]]; then
  install_file "${AGY_DEST}"
  link_generic_to_agy
elif [[ "${TARGET}" == "agy" ]]; then
  install_file "${AGY_DEST}"
elif [[ "${TARGET}" == "generic" ]]; then
  install_file "${GENERIC_DEST}"
else
  install_file "${AGY_DEST}"
  install_file "${GENERIC_DEST}"
fi

echo "==> Guardrails configuration complete."
