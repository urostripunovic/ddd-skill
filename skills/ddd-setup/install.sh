#!/usr/bin/env bash
# Usage: <this directory>/install.sh [--lang go,ts | --lang none | --model-only] [repository]
# Copies the kit's cards, model templates and tools into a repository (default:
# the current directory). The strategic cards (docs/ddd/strategic/) are about the
# model, not the code, and are installed with every option.
#   --lang go,ts   the functional cards with the examples and lint configs for these languages
#   --lang none    the functional cards alone: the rules, for a language the kit has no examples for
#   --model-only   no pattern cards: the model template, its checker and the strategic
#                  cards, for a repository that keeps its own coding style
# It installs no programs, changes no lint config and
# never overwrites a file: a file that exists with other content is kept and
# listed, so that somebody decides about it. Safe to run again.
set -euo pipefail

kit="$(cd "$(dirname "$0")" && pwd)/kit"
usage() { echo "usage: $0 [--lang go,ts | --lang none | --model-only] [repository]" >&2; exit 2; }
langs=""
lang_given=""
model_only=""
target=""
# Options and the repository may come in any order; anything unknown stops the
# script, so a misplaced flag is never silently ignored.
while [ "$#" -gt 0 ]; do
  case "$1" in
    --lang|--lang=*)
      [ -z "${lang_given}" ] || { echo "--lang given twice; name every language once: --lang go,ts" >&2; usage; }
      if [ "$1" = "--lang" ]; then
        [ "$#" -ge 2 ] && [ -n "$2" ] || { echo "--lang needs a value: go, ts, go,ts or none" >&2; usage; }
        langs="${2//,/ }"; shift 2
      else
        langs="${1#--lang=}"; langs="${langs//,/ }"; shift
      fi
      lang_given=yes ;;
    --model-only) model_only=yes; shift ;;
    -*) echo "unknown option: $1" >&2; usage ;;
    *)
      [ -z "${target}" ] || { echo "more than one repository given: ${target} and $1" >&2; usage; }
      target="$1"; shift ;;
  esac
done
if [ -n "${model_only}" ] && [ -n "${lang_given}" ]; then
  echo "--model-only installs no cards, so it cannot be combined with --lang" >&2; usage
fi
if [ -n "${lang_given}" ]; then
  [ -n "${langs// /}" ] || { echo "--lang needs a value: go, ts, go,ts or none" >&2; usage; }
  for lang in ${langs}; do
    case "${lang}" in go|ts|none) ;; *) echo "unknown language: ${lang} (expected go, ts or none)" >&2; usage ;; esac
  done
  case " ${langs} " in
    *" none "*) [ "${langs// /}" = "none" ] || { echo "--lang none installs no examples, so it cannot be combined with go or ts" >&2; usage; } ;;
  esac
fi
[ -z "${model_only}" ] || langs=none
cd "${target:-.}"
top="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "not a git repository: $(pwd)" >&2; exit 2; }
# The skills look for docs/domain/ and tools/ at the repository root.
[ "$(pwd -P)" = "$(cd "${top}" && pwd -P)" ] || { echo "not the repository root: $(pwd); run it for ${top}" >&2; exit 2; }

if [ -z "${langs}" ]; then
  # node_modules is skipped because some npm packages ship a go.mod or a tsconfig.json.
  found() { [ -n "$(find . -maxdepth 4 -name "$1" -not -path '*/node_modules/*' -not -path './.cards-check/*' -print -quit)" ]; }
  if found go.mod; then langs="go"; fi
  if found tsconfig.json; then langs="${langs} ts"; fi
fi
[ -n "${langs}" ] || { echo "no Go or TypeScript found; name the languages with --lang go,ts, or use --lang none or --model-only for another language" >&2; exit 2; }
has() { case " ${langs} " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

added=0
same=0
kept=()
put() { # put <path relative to the kit and to the repository>
  if [ ! -e "$1" ]; then
    mkdir -p "$(dirname "$1")"
    cp -p "${kit}/$1" "$1"
    added=$((added + 1))
  elif cmp -s "${kit}/$1" "$1"; then
    same=$((same + 1))
  else
    kept+=("$1")
  fi
}
put_all() { while IFS= read -r file; do put "${file#"${kit}"/}"; done < <(find "${kit}/$1" "${@:2}" -type f | sort); }

put_all docs/domain
put_all docs/ddd/strategic
for file in check-model.sh check_model.py model-hash.sh stamp-model.sh ddd-status.sh ddd_status.py; do put "tools/${file}"; done
if [ -z "${model_only}" ]; then
  put_all docs/ddd/cards -maxdepth 1
  put_all docs/ddd/cards/functional -maxdepth 1
  for file in check-cards.sh extract_cards.py check-domain-paths.sh; do put "tools/${file}"; done
fi
if has go; then put_all docs/ddd/cards/functional/go; put tools/lint/.golangci.yml; fi
if has ts; then put_all docs/ddd/cards/functional/ts; put tools/lint/eslint.config.mjs; put tools/lint/tsconfig.json; fi

if [ -z "${model_only}" ]; then
  if ! grep -qxF '.cards-check/' .gitignore 2>/dev/null; then
    # Without this, a last line with no newline would be merged with the new entry.
    if [ -s .gitignore ] && [ -n "$(tail -c 1 .gitignore)" ]; then echo >> .gitignore; fi
    echo '.cards-check/' >> .gitignore
    echo "added .cards-check/ to .gitignore"
  fi
fi

if [ -n "${model_only}" ]; then echo "model only: no cards, no lint configs"; else echo "languages: ${langs}"; fi
echo "added ${added} files; ${same} were already there and identical"
# Cards from before the style directories sit directly under docs/ddd/cards/. They hold the
# team's Corrections, so they are reported and never moved or overwritten here.
if [ -n "$(find docs/ddd/cards -maxdepth 1 \( -name '[0-9]*.md' -o -name go -o -name ts \) -print -quit 2>/dev/null)" ]; then
  echo "earlier card layout: docs/ddd/cards/ holds cards or language directories that now belong in docs/ddd/cards/functional/;"
  echo "  move them there with git mv, keeping their Corrections, and compare them with the kit's"
fi
if [ "${#kept[@]}" -gt 0 ]; then
  echo "kept, because the repository's version differs from the kit's (compare with ${kit}/<path>):"
  printf '  %s\n' "${kept[@]}"
fi

# Reported, never installed: what is missing decides which checks can run here.
need() { command -v "$1" >/dev/null 2>&1 || echo "not installed: $1 ($2)"; }
need python3 "tools/check-model.sh"
if has go; then need golangci-lint "the Go lint rules"; fi
if has ts; then need node "the TypeScript lint rules"; fi
