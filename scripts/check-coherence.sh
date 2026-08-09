#!/usr/bin/env sh
# Coherence guard: docs must match the canonical model in
# archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx
# (7 business goals, 23 functional + 17 non-functional user stories,
#  23 FR + 17 NFR). Runnable locally: `sh scripts/check-coherence.sh`
set -u

BG=docs/02-business-analysis/business-goals-epics-stories.md
REQ=docs/02-business-analysis/requirements.md

fail=0
check() { # $1 label  $2 actual  $3 expected
  if [ "$2" -ne "$3" ]; then
    echo "FAIL: $1 = $2 (expected $3)"
    fail=1
  else
    echo "ok:   $1 = $2"
  fi
}

check "BG rows"      "$(grep -c '^| BG-' "$BG")"       7
check "US rows"      "$(grep -c '^| US-[0-9]' "$BG")"  23
check "NFR-US rows"  "$(grep -c '^| NFR-US-' "$BG")"   17
check "FR rows"      "$(grep -c '^| FR-[0-9]' "$REQ")" 23
check "NFR rows"     "$(grep -c '^| NFR-[0-9]' "$REQ")" 17

if [ "$fail" -ne 0 ]; then
  echo "Coherence guard FAILED - docs diverge from the canonical model."
  exit 1
fi
echo "Coherence guard passed."
