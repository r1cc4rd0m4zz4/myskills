#!/usr/bin/env bash
# scripts/link-skills.sh
# Creates local symlinks from this repository into ~/.agents/skills/ for development.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${HOME}/.agents/skills"

mkdir -p "${TARGET_DIR}"

echo "Linking skills from ${REPO_ROOT}/skills to ${TARGET_DIR}..."

for skill_path in "${REPO_ROOT}"/skills/*; do
  if [ -d "${skill_path}" ]; then
    skill_name="$(basename "${skill_path}")"
    dest="${TARGET_DIR}/${skill_name}"

    if [ -L "${dest}" ]; then
      echo "  [updating symlink] ${skill_name} -> ${dest}"
      rm -f "${dest}"
    elif [ -d "${dest}" ]; then
      echo "  [replacing existing folder with symlink] ${skill_name} -> ${dest}"
      rm -rf "${dest}"
    else
      echo "  [creating symlink] ${skill_name} -> ${dest}"
    fi

    ln -s "${skill_path}" "${dest}"
  fi
done

echo "Done! Linked all skills successfully."
