#!/usr/bin/env bash
# Usage: evals/implementation/score.sh <repo> <base>
# The part of the implementation eval a script can decide. Prints one line per
# check and exits 1 if any failed. The rest is scored by hand: see scoring.md.
set -uo pipefail

cd "$1"
base="$2"
failed=0
check() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then echo "pass  ${name}"; else echo "FAIL  ${name}"; failed=1; fi
}
count() { { grep -rn --include='*.go' -E "$1" internal 2>/dev/null || true; } | wc -l | tr -d ' '; }

check "work is committed"            test -z "$(git status --porcelain)"
check "something was implemented"    test -n "$(git diff --stat "${base}" HEAD -- internal)"
check "model and glossary untouched" git diff --quiet "${base}" HEAD -- docs/domain CONTEXT.md
check "lint config untouched"        git diff --quiet "${base}" HEAD -- .golangci.yml tools
check "model check"                  tools/check-model.sh
check "go build"                     go build ./...
check "go vet"                       go vet ./...
check "go test"                      go test ./...
check "golangci-lint"                golangci-lint run ./...

# Not failures on their own, but each one has to be looked at.
echo "info  //nolint comments: $(count '//[[:space:]]*nolint')"
echo "info  test functions: $(count '^func Test')"
echo "info  head: $(git rev-parse HEAD)"
exit "${failed}"
