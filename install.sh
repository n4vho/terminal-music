#!/usr/bin/env bash
set -euo pipefail
command -v python3 >/dev/null || { echo 'Install Python 3.10 or newer first.' >&2; exit 1; }
python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$HOME/.local/bin"
install -m 755 "$source_dir/bin/terminal-music" "$HOME/.local/bin/terminal-music"
printf 'Launcher installed. Starting setup...\n'
"$HOME/.local/bin/terminal-music" setup "$@"
printf '\nStart music with: terminal-music\nIf the command is missing, add ~/.local/bin to your PATH or use ~/.local/bin/terminal-music\n'
