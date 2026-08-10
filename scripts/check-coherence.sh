#!/usr/bin/env sh
# Coherence guard: docs must match the canonical model in
# archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx
# (unique IDs on the Consolidated Mapping sheet:
#  7 BG, 7 EP, 23 US, 17 NFR-US, 23 FR, 17 NFR;
#  plus BG->EP->story->requirement chains and MVP/Future scope).
# Parses the workbook and compares it to markdown inventories, chains, and scope.
# Runnable locally: `sh scripts/check-coherence.sh`
#               or: `python scripts/check_coherence.py`
set -u

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
cd "$ROOT" || exit 1

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "FAIL: python3/python required to parse the canonical xlsx."
  exit 1
fi

exec "$PY" scripts/check_coherence.py
