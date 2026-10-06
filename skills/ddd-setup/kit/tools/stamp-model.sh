#!/usr/bin/env bash
# Usage: tools/stamp-model.sh approve docs/domain/contexts/<context>.md "<name>"
#        tools/stamp-model.sh review  docs/domain/contexts/<context>.md
#        tools/stamp-model.sh draft   docs/domain/contexts/<context>.md
# Writes the Status line, so every skill writes it the same way.
#   approve  "approved by <name> on <today>, model-hash <hash>", only after the
#            user said they approve. It runs tools/check-model.sh on the result and
#            leaves the file unchanged if the check fails.
#   review   appends "reviewed <today> at <hash>" once a model review has no
#            blockers left, after its accepted changes are written. The hash ties
#            the review to this version: a later edit makes it out of date.
#   draft    sets the status back to draft after an edit to the approved part,
#            keeping the review, so the checker can tell that it is out of date.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
python3 - "${here}" "$@" <<'PY'
import datetime
import pathlib
import re
import subprocess
import sys

here, args = pathlib.Path(sys.argv[1]), sys.argv[2:]
usage = "usage: tools/stamp-model.sh approve <file> <name> | review <file> | draft <file>"
if not args or args[0] not in ("approve", "review", "draft") or len(args) != (3 if args[0] == "approve" else 2):
    sys.exit(usage)
action, path = args[0], pathlib.Path(args[1])
raw = path.read_text()
status = re.search(r"^Status:[^\n]*$", raw, re.M)
if not status:
    sys.exit(f"{path}: no Status line")
hashed = subprocess.run([str(here / "model-hash.sh"), str(path)], capture_output=True, text=True)
if hashed.returncode:
    sys.exit(hashed.stderr.strip() or f"{path}: model hash failed")
model_hash = hashed.stdout.strip()
today = datetime.date.today().isoformat()

state = status.group(0)[len("Status:"):].strip()
review = re.search(r",?\s*\breviewed\s+[^,]*$", state)
reviewed = review.group(0).strip().lstrip(",").strip() if review else None
base = state[:review.start()].strip() if review else state

if action == "approve":
    name = args[2].strip()
    if not name:
        sys.exit("approve needs the name of the person who approved")
    base = f"approved by {name} on {today}, model-hash {model_hash}"
elif action == "review":
    reviewed = f"reviewed {today} at {model_hash}"
else:
    base = "draft"

line = "Status: " + base + (f", {reviewed}" if reviewed else "")
path.write_text(raw[:status.start()] + line + raw[status.end():])

if action == "approve":
    check = subprocess.run([sys.executable, str(here / "check_model.py"), str(path)], capture_output=True, text=True)
    if check.returncode:
        path.write_text(raw)
        sys.stdout.write(check.stdout)
        sys.exit(f"{path}: not approved, and the file is unchanged. Settle the problems above, then approve again.")
print(f"{path}: {line}")
PY
