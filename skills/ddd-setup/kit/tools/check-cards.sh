#!/usr/bin/env bash
# Usage: tools/check-cards.sh   (run from the repository root)
# Requires: python3; for Go: go, gofmt, golangci-lint v2; for TypeScript: node, npm.
# Compiles and lints every card example with the reference configs in tools/lint/.
# Only the languages installed under docs/ddd/cards/ are checked.
set -euo pipefail

root="$(pwd)"
cards="${root}/docs/ddd/cards"
work="${root}/.cards-check"
if [ ! -d "${cards}/go" ] && [ ! -d "${cards}/ts" ]; then
  echo "no language examples installed; nothing checked"
  exit 0
fi
rm -rf "${work}/go" "${work}/ts/src"
# The lint configs are written next to the examples with their DOMAIN-PATHS
# pointing at the extracted domain examples, whatever paths the team set.
python3 "${root}/tools/extract_cards.py" "${cards}" "${work}" "${root}/tools/lint"

if [ -d "${cards}/go" ]; then
  cd "${work}/go"
  printf 'module cards\n\ngo 1.24\n' > go.mod
  unformatted="$(gofmt -l .)"
  if [ -n "${unformatted}" ]; then echo "not gofmt-formatted: ${unformatted}"; exit 1; fi
  go vet ./...
  golangci-lint run ./...
fi

if [ -d "${cards}/ts" ]; then
  cd "${work}/ts"
  cp "${root}/tools/lint/tsconfig.json" .
  # Installed once; node_modules is kept between runs because the install is the slow part.
  [ -d node_modules ] || { npm init -y >/dev/null; npm install --save-dev eslint typescript typescript-eslint >/dev/null; }
  npx tsc -p .
  npx eslint src
fi

echo "all card examples compile and pass lint"
