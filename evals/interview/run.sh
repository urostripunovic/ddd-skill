#!/usr/bin/env bash
# Usage: evals/interview/run.sh <work-dir> [max-rounds]
# Requires: claude (the Claude Code CLI, signed in), git, python3.
#
# Runs the ddd-modelling interview against a scripted domain expert. One session
# runs the skill in a new repository; a second plays the expert from
# expert-brief.md. Their messages are passed back and forth until the expert
# ends the interview or max-rounds (default 15) is reached.
#
# Leaves <work-dir>/repo (the model the interview produced) and
# <work-dir>/transcript.md. Score the model by hand against answer-key.md.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
kit_root="${here}/../.."
work="$(mkdir -p "$1" && cd "$1" && pwd)"
max_rounds="${2:-15}"

repo="${work}/repo"
# The expert runs in an empty directory so it cannot read the repository or the answer key.
expert_dir="${work}/expert"
transcript="${work}/transcript.md"
rm -rf "${repo}" "${expert_dir}"
mkdir -p "${repo}" "${expert_dir}"

cd "${repo}"
git init -q -b main
cp -r "${kit_root}/skills/ddd-setup/kit/." .
# Installed in the repository, so the run tests this checkout of the skills and not a copy in the home directory.
mkdir -p .claude/skills
cp -r "${kit_root}/skills/." .claude/skills/
git add -A
git -c user.email=eval@example.com -c user.name=eval commit -q -m "Kit"

new_id() { python3 -c 'import uuid; print(uuid.uuid4())'; }
result_of() { python3 -c 'import json, sys; print(json.load(sys.stdin)["result"])'; }

interviewer_id="$(new_id)"
expert_id="$(new_id)"

# say <dir> <first|next> <session-id> <message> [extra claude arguments...]
say() {
  local dir="$1" turn="$2" id="$3" message="$4"
  shift 4
  local session=(--resume "${id}")
  [ "${turn}" = first ] && session=(--session-id "${id}")
  (cd "${dir}" && claude -p "${message}" --output-format json "${session[@]}" "$@") | result_of
}

interviewer() {
  say "${repo}" "$1" "${interviewer_id}" "$2" \
    --permission-mode acceptEdits --allowedTools "Bash(tools/check-model.sh:*)"
}
expert() {
  say "${expert_dir}" "$1" "${expert_id}" "$2" --system-prompt "$(cat "${here}/expert-brief.md")"
}

opening="Use the ddd-modelling skill. I coordinate a neighbourhood tool library, and we want software for lending out our tools. Interview me and build the domain model. I can only answer in writing, so put every question in your reply."

printf '# Interview transcript\n\n## Expert\n\n%s\n' "${opening}" > "${transcript}"
question="$(interviewer first "${opening}")"
turn=first
for round in $(seq 1 "${max_rounds}"); do
  printf '\n## Interviewer, round %s\n\n%s\n' "${round}" "${question}" >> "${transcript}"
  answer="$(expert "${turn}" "${question}")"
  turn=next
  printf '\n## Expert\n\n%s\n' "${answer}" >> "${transcript}"
  case "${answer}" in *"END OF INTERVIEW"*) break ;; esac
  question="$(interviewer next "${answer}")"
done

echo "rounds: ${round}"
echo "model: ${repo}/GLOSSARY.md and ${repo}/docs/domain/"
echo "transcript: ${transcript}"
(cd "${repo}" && tools/check-model.sh) || true
echo "Score the model against ${here}/answer-key.md and record the result in evals/results/."
