#!/usr/bin/env bash
# Usage: tools/check-model.sh [docs/domain/contexts/<context>.md ...]   (run from the repository root)
# With no arguments, checks every context file. Requires: python3, git.
# Checks that every template section is present, selected type/signature
# references, incoming/outgoing command mentions, matrix agreement,
# command/decision-failure example mentions, unique example numbers, selected
# glossary names, depth overrides and the place of the notes tail, rejects an
# unconfirmed 'Issued by' or invariant, and prints the
# strict scope of each strict command. See check_model.py for the limits: a
# passing check does not establish model completeness or correctness.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
if [ "$#" -eq 0 ]; then
  # Files starting with an underscore are templates, not models.
  # A read loop and not mapfile: macOS ships bash 3.2, which has no mapfile.
  set --
  while IFS= read -r file; do set -- "$@" "${file}"; done < <(find docs/domain/contexts -name '*.md' ! -name '_*' | sort)
  [ "$#" -gt 0 ] || { echo "no context files under docs/domain/contexts"; exit 1; }
fi
python3 "${here}/check_model.py" "$@"
