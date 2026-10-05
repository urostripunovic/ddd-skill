#!/usr/bin/env bash
# Usage: tools/model-hash.sh docs/domain/contexts/<context>.md
# Prints a hash of the approved part of the model file. Record it in the Status
# line at approval; a different value later means that part was edited after it
# was approved.
set -euo pipefail
# Left out of the hash:
# - the Status line, because writing the hash into it would change the hash
# - the trailing "## Amendments" and "## Migration" sections,
#   because those are written after approval: what implementation learned, and
#   the plan for moving existing code. Recording them must not undo the approval.
# - blank lines at the end of what is left, so that adding one of those sections
#   below the model does not change the hash of the model above it
# Validate the tail before hashing. A misplaced notes heading must not silently
# exclude later rules. Ignore headings inside comments and fenced code blocks.
python3 - "$1" <<'PY'
import pathlib
import re
import subprocess
import sys

path = pathlib.Path(sys.argv[1])
raw = path.read_text()
visible = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group()), raw, flags=re.S)
approved = []
tail = False
fence = None
for number, (line, text) in enumerate(zip(raw.splitlines(), visible.splitlines()), 1):
    marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", text)
    if marker:
        run, rest = marker.groups()
        if fence is None:
            fence = run
        elif run[0] == fence[0] and len(run) >= len(fence) and not rest.strip():
            fence = None
    elif fence is None:
        if re.fullmatch(r"## (Amendments|Migration)\s*", text):
            tail = True
            continue
        if tail and re.match(r"^#{1,2} ", text):
            sys.exit(f"{path}:{number}: model section after Migration/Amendments; move it before the notes tail")
        if text.startswith("Status:"):
            continue
    if not tail:
        approved.append(line)

while approved and approved[-1] == "":
    approved.pop()
body = "".join(line + "\n" for line in approved)
result = subprocess.run(["git", "hash-object", "--stdin"], input=body, text=True, capture_output=True, check=True)
print(result.stdout.strip()[:12])
PY
