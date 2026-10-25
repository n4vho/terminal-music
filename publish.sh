#!/usr/bin/env bash
# Publish this reviewed repository using your GitHub CLI login.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v gh >/dev/null || { echo 'Install GitHub CLI first (Arch/Manjaro: sudo pacman -S github-cli), then run gh auth login.' >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo 'Run gh auth login first, then rerun this script.' >&2; exit 1; }
if git remote get-url origin >/dev/null 2>&1; then
  git push -u origin main
else
  gh repo create terminal-music --public --source=. --remote=origin --push \
    --description 'Spotify in the terminal: Spotatui interface with official Soloist audio playback'
fi
gh repo view --json url --jq .url
