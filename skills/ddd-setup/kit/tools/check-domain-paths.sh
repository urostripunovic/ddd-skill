#!/usr/bin/env bash
# Usage: tools/check-domain-paths.sh   (run from the repository root)
# The domain lint rules apply only to the paths a config names, and a path that
# matches nothing checks nothing, silently. This reads the "Domain paths:" line
# that ddd-setup writes under "## Domain code" in CLAUDE.md or AGENTS.md, and
# fails when a path has no files, or a lint config for its language does not
# name it: Go needs it in both places marked DOMAIN-PATHS in .golangci.*, and
# TypeScript in the domain block of eslint.config.*.
# Write "Domain paths: none" when the team chose not to apply the domain rules.
set -euo pipefail

python3 - <<'PY'
import pathlib
import re
import sys

root = pathlib.Path(".")
instructions = [p for p in (root / "CLAUDE.md", root / "AGENTS.md") if p.exists()]
line = None
for path in instructions:
    found = re.search(r"^\s*[-*]?\s*Domain paths:\s*(.+)$", path.read_text(), re.M | re.I)
    if found:
        line = found.group(1)
        break
if line is None:
    sys.exit("no 'Domain paths:' line in CLAUDE.md or AGENTS.md; ddd-setup writes it under '## Domain code', "
             "as 'Domain paths: internal/ordering/domain, ...' or 'Domain paths: none'")
paths = [p.strip().strip("`").rstrip("/") for p in line.split(",") if p.strip()]
if [p.lower() for p in paths] == ["none"]:
    print("domain paths: none recorded; the domain lint rules are not applied to this repository")
    sys.exit(0)


def first(names):
    return next((root / n for n in names if (root / n).exists()), None)


go_config = first([".golangci.yml", ".golangci.yaml", ".golangci.toml", ".golangci.json"])
ts_config = first([f"eslint.config.{ext}" for ext in ("js", "mjs", "cjs", "ts", "mts", "cts")])
problems = []
for path in paths:
    files = [f for f in (root / path).rglob("*") if f.is_file()] if (root / path).is_dir() else []
    if not files:
        problems.append(f"{path}: no files there, so the domain rules check nothing")
        continue
    if any(f.suffix == ".go" for f in files):
        if go_config is None:
            problems.append(f"{path}: holds Go code, but there is no .golangci config at the root")
        else:
            count = go_config.read_text().count(path)
            if count < 2:
                problems.append(f"{path}: named {count} time(s) in {go_config.name}; it belongs in both places marked "
                                "DOMAIN-PATHS (the depguard files and the forbidigo path-except), written out, not as an alternation")
    if any(f.suffix in (".ts", ".tsx", ".mts", ".cts") for f in files):
        if ts_config is None:
            problems.append(f"{path}: holds TypeScript, but there is no eslint.config.* at the root")
        elif path not in ts_config.read_text():
            problems.append(f"{path}: not named in {ts_config.name}; add it to the files of the domain block")

for problem in problems:
    print(problem)
if problems:
    sys.exit(1)
print(f"domain paths: {', '.join(paths)} each hold code and are named in the lint config for their language")
PY
