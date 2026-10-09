#!/usr/bin/env bash
# Usage: evals/make-fixture-repo.sh <target-dir> [seeded|clean|clean-ts|model]
# Builds a git repository with two commits and prints both hashes to pass to the reviewers.
#   base: the kit and an approved Ordering model
#   head, seeded (the default): an implementation with seeded violations, and the model edited after approval
#   head, clean: a correct Go implementation, to measure what the reviewers report when nothing is wrong
#   head, clean-ts: the same in TypeScript; the repository then has no Go in it
#   model: the base commit only, for the implementation eval to build on
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
kit="${here}/../skills/ddd-setup/kit"
target="$1"
kind="${2:-seeded}"
case "${kind}" in seeded|clean|clean-ts|model) ;; *) echo "unknown kind: ${kind}" >&2; exit 2 ;; esac

rm -rf "${target}"
mkdir -p "${target}"
cd "${target}"
git init -q -b main

# sed -i takes different arguments on macOS and Linux, so the edit goes through a copy.
edit() { sed "$1" "$2" > "$2.tmp" && mv "$2.tmp" "$2"; }
git config user.email "eval@example.com"
git config user.name "eval"

cp -r "${kit}/." .
cp "${here}/fixture/model/GLOSSARY.md" .
cp "${here}/fixture/model/context-map.md" docs/domain/
cp "${here}/fixture/model/ordering.md" docs/domain/contexts/ordering.md
if [ "${kind}" != clean-ts ]; then
  cp "${here}/fixture/go/go.mod" .
  # The reference configs name a placeholder domain path; this repository's domain is the ordering package.
  sed -e 's#\*\*/internal/domain/\*\*#**/internal/ordering/**#' -e 's#path-except: internal/domain/#path-except: internal/ordering/#' \
    tools/lint/.golangci.yml > .golangci.yml
fi
case "${kind}" in
  seeded) cp "${here}/fixture/ts/package.json" tools/lint/tsconfig.json . ;;
  clean-ts) cp "${here}/fixture-clean/ts/package.json" "${here}/fixture-clean/ts/tsconfig.json" . ;;
esac
if [ -f package.json ]; then
  sed 's#src/domain/\*\*/\*.ts#src/ordering/**/*.ts#' tools/lint/eslint.config.mjs > eslint.config.mjs
fi
printf '.cards-check/\nnode_modules/\npackage-lock.json\n' > .gitignore

# The fixture model is strict, so its approval rests on a review.
edit "s/^Status: draft$/Status: approved 2026-10-03, reviewed 2026-10-03/" docs/domain/contexts/ordering.md
git add -A
git commit -q -m "Kit and approved Ordering model"
base="$(git rev-parse HEAD)"
if [ "${kind}" = model ]; then echo "base=${base}"; exit 0; fi

if [ "${kind}" = seeded ]; then
  cp -r "${here}/fixture/go/internal" .
  cp -r "${here}/fixture/ts/src" .
  # Seeded: the model is edited in the reviewed range and the Status line is left as it was.
  edit 's/| Quantity | integer | 1..1000 | no |/| Quantity | integer | 1..5000 | no |/' docs/domain/contexts/ordering.md
elif [ "${kind}" = clean-ts ]; then
  cp -r "${here}/fixture-clean/ts/src" "${here}/fixture-clean/ts/test" .
else
  cp -r "${here}/fixture-clean/go/internal" .
fi
git add -A
git commit -q -m "Implement ordering"
head="$(git rev-parse HEAD)"

echo "base=${base}"
echo "head=${head}"
