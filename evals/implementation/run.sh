#!/usr/bin/env bash
# Usage: evals/implementation/run.sh <work-dir>
# Requires: claude (the Claude Code CLI, signed in), git, go, golangci-lint v2, python3.
#
# Gives ddd-implementation the approved Ordering model and nobody to ask, and
# lets it implement the Order aggregate in Go. Then runs score.sh on the result.
#
# Leaves <work-dir>/repo and <work-dir>/summary.md (the implementer's last message).
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
kit_root="${here}/../.."
work="$(mkdir -p "$1" && cd "$1" && pwd)"
repo="${work}/repo"

"${here}/../make-fixture-repo.sh" "${repo}" model >/dev/null
cd "${repo}"
# Installed in the repository, so the run tests this checkout of the skills and not a copy in the home directory.
mkdir -p .claude/skills
cp -r "${kit_root}/skills/." .claude/skills/
git add -A
git commit -q -m "Skills"
base="$(git rev-parse HEAD)"

# "MODEL GAPS" is what the eval measures: the model claims to leave the implementer no
# business decision, so every gap is either a hole in the fixture model or a decision
# the skill should not have needed.
prompt="Use the ddd-implementation skill. Implement the Order aggregate of the Ordering context in Go: the domain in internal/ordering, and one function per use case in internal/app. The model in docs/domain/ is approved. Nobody can answer questions during this run. If the model leaves something undecided, do not decide it yourself: leave that part out, and list it at the end of your last message under the heading MODEL GAPS, or write 'MODEL GAPS: none'. Do not edit docs/domain/, CONTEXT.md or .golangci.yml. Commit your work when it is done."

claude -p "${prompt}" --output-format json --permission-mode acceptEdits \
  --allowedTools "Bash(go:*)" "Bash(gofmt:*)" "Bash(golangci-lint:*)" "Bash(tools/check-model.sh:*)" "Bash(git add:*)" "Bash(git commit:*)" "Bash(git status:*)" "Bash(git diff:*)" \
  | python3 -c 'import json, sys; print(json.load(sys.stdin)["result"])' > "${work}/summary.md"

echo "summary: ${work}/summary.md"
echo "base: ${base}"
"${here}/score.sh" "${repo}" "${base}"
