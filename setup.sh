#!/usr/bin/env bash
# Setup Claude Code global config on a new machine.
#
# The real logic lives in install.py (JSON merge + symlinks are a poor fit for
# bash). This is a thin entry point kept for muscle memory / docs; you can also
# run `python3 install.py` (add --dry-run to preview) directly.
#
# Usage: ./setup.sh [--dry-run]

set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$DIR/install.py" "$@"
