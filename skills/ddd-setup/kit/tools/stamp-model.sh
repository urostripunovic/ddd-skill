#!/usr/bin/env bash
# Usage: tools/stamp-model.sh approve docs/domain/contexts/<context>.md "<name>"
#        tools/stamp-model.sh review  docs/domain/contexts/<context>.md
#        tools/stamp-model.sh draft   docs/domain/contexts/<context>.md
# Writes the Status line, so every skill writes it the same way.
# The line reads "approved by <name> on <date>, reviewed <date>"; the hashes go in a comment
# at its end, "<!-- model-hash <hash>, reviewed at <hash> -->". A line in the older
# form, with the hashes in the text, is read the same way.
#   approve  "approved by <name> on <today>" with the model-hash, only after the
#            user said they approve. When CLAUDE.md or AGENTS.md has an
#            "Approvers: A, B" line, <name> must be on it. Before that, it
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

if action == "approve":
    # An "Approvers:" line in the agent instructions names who may approve; a name not on it is refused.
    top = subprocess.run(["git", "-C", str(path.resolve().parent), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    root = pathlib.Path(top.stdout.strip()) if top.returncode == 0 else path.resolve().parent
    listed = None
    for name in ("CLAUDE.md", "AGENTS.md"):
        found = re.search(r"^Approvers:[ \t]*(.+)$", (root / name).read_text(), re.M) if (root / name).exists() else None
        if found:
            listed = [n.strip() for n in found.group(1).split(",") if n.strip()]
            break
    if listed is not None and args[2].strip().lower() not in [n.lower() for n in listed]:
        sys.exit(f"{path}: not approved: {args[2].strip()!r} is not on the Approvers line ({', '.join(listed)}). "
                 "Only the user changes that line.")

sys.path.insert(0, str(here))
from check_model import read_status

# The line reads short; the hashes the tools compare go in a comment at its end.
state = read_status(raw)
review = re.search(r"\breviewed\s+([^,\s]+)(?:\s+at\s+([0-9a-f]+))?", state)
reviewed = (review.group(1), review.group(2)) if review else None
base = state[:review.start()].strip().rstrip(",").strip() if review else state
approved_hash = re.search(r",?\s*model-hash\s+([0-9a-f]+)", base)
if approved_hash:
    base, approved_hash = (base[:approved_hash.start()] + base[approved_hash.end():]).strip(), approved_hash.group(1)

if action == "approve":
    name = args[2].strip()
    if not name:
        sys.exit("approve needs the name of the person who approved")
    base, approved_hash = f"approved by {name} on {today}", model_hash
elif action == "review":
    reviewed = (today, model_hash)
else:
    base, approved_hash = "draft", None

hidden = ([f"model-hash {approved_hash}"] if approved_hash else []) + ([f"reviewed at {reviewed[1]}"] if reviewed and reviewed[1] else [])
line = "Status: " + base + (f", reviewed {reviewed[0]}" if reviewed else "") + (f" <!-- {', '.join(hidden)} -->" if hidden else "")
path.write_text(raw[:status.start()] + line + raw[status.end():])

if action == "approve":
    check = subprocess.run([sys.executable, str(here / "check_model.py"), "--approving", str(path)], capture_output=True, text=True)
    if check.returncode:
        path.write_text(raw)
        sys.stdout.write(check.stdout)
        sys.exit(f"{path}: not approved, and the file is unchanged. Settle the problems above, then approve again.")
print(f"{path}: {line}")
PY
