#!/usr/bin/env bash
# Rebuild the generated parts of this public release (no network needed).
# The SQLite FTS index (~100 MB) is not committed; this regenerates it from texts/ and data/.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_index.py      # SQLite FTS5 -> index/verne.db
python3 scripts/stats.py || true    # counts -> sources/stats.json
python3 persona/validate_persona.py # persona references resolve
