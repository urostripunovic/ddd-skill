#!/usr/bin/env bash
# Usage: tools/check-range.sh <base>   (run from the repository root)
# The mechanical part of a code review of <base>...HEAD: the model changed without a new
# approval, and, to judge, words the glossary avoids in new code, suppressions, loosened
# lint configs, glossary or context-map changes and example rows no test names.
# Exits 1 on a problem. Requires: python3, git. See check_range.py for what it does not judge.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
python3 "${here}/check_range.py" "$@"
