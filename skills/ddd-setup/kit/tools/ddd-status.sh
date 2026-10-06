#!/usr/bin/env bash
# Usage: tools/ddd-status.sh   (run from the repository root)
# Prints where the repository stands in the DDD workflow, as facts: setup, each
# context's status, depth, review, check result, open questions, amendments,
# pending gaps, migration steps, which example rows have a test, and the branch.
# Changes nothing. The ddd-next skill reads it and recommends one next step.
# See ddd_status.py for how tests are matched to example rows. Requires: python3, git.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
python3 "${here}/ddd_status.py" "$@"
