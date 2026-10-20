"""Usage: check_range.py <base>   (run from the repository root; tools/check-range.sh calls it)

The parts of a code review a script can decide, for the range <base>...HEAD, so the
reviewers spend their reading on judgement. Each line names what it found and where.

Problem (exit status 1):
  model changed      a context file's model, above its notes tail, changed in the range
                     while its Status line stayed as it was: changed without a new approval.

To judge (exit status unaffected; each needs a person to say whether it is right):
  avoided word       an identifier in an added line of code contains a word the glossary
                     lists under _Avoid_. Comments are skipped. Words such as "row" or "line"
                     are also ordinary programming words, so a match is a lead, not a verdict.
  suppression        an added lint, type-check or test suppression: nolint, eslint-disable,
                     @ts-ignore, @ts-expect-error, noqa, a skipped test.
  lint config        a lint or compiler config changed; its removed lines are shown,
                     because a removed rule or domain path loosens a check.
  meaning            the glossary or context map changed: a change of meaning to an approved
                     rule needs approval, and no script can tell.
  example untested   a context the range touches (its file, or its code) has Examples rows that
                     no test names as "example <n>". A ticket may defer them; the review decides.

It reads committed changes only. It does not judge whether a test uses a row's values,
whether a suppression is justified, or whether a word is used in the avoided sense.
"""
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_model  # noqa: E402  (the same model parser the checker uses)
import ddd_status  # noqa: E402  (the same test finder the status uses)

TAIL = re.compile(r"^## (Migration|Amendments|Pending)\s*$")
SUPPRESSION = re.compile(
    r"//\s*nolint|eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck|#\s*noqa|@SuppressWarnings"
    r"|\bt\.Skip\(|\b(it|test|describe)\.skip\(|\bx(it|describe)\(|@pytest\.mark\.skip|@Disabled\b"
)
LINT_CONFIG = re.compile(r"(^|/)(\.golangci\.[a-z]+|eslint\.config\.[a-z]+|\.eslintrc[^/]*|tsconfig[^/]*\.json)$|^tools/lint/")
CODE = re.compile(r"\.(go|[cm]?[jt]sx?|py|java|kt|cs|rb|rs)$")


def git(*args):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def show(ref, path):
    result = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def body(text):
    """The model as an approval covers it: everything above the notes tail, without the Status line."""
    lines = []
    for line in text.splitlines():
        if TAIL.match(line):
            break
        if not line.startswith("Status:"):
            lines.append(line.rstrip())
    return "\n".join(lines).strip()


def added_lines(base):
    """(path, line number, text) for every line the range adds."""
    path, number = None, 0
    for line in git("diff", "--unified=0", "--no-color", f"{base}...HEAD").splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            number = int(re.search(r"\+(\d+)", line).group(1))
        elif line.startswith("+") and path:
            yield path, number, line[1:]
            number += 1


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    base = git("merge-base", argv[0], "HEAD").strip()
    changed = [p for p in git("diff", "--name-only", f"{base}...HEAD").splitlines() if p]
    problems, judge = [], []

    contexts = [p for p in changed if re.match(r"docs/domain/contexts/[^_][^/]*\.md$", p) and pathlib.Path(p).exists()]
    for path in contexts:
        before, after = show(base, path), pathlib.Path(path).read_text()
        if before is None:
            continue
        status_before, status_after = check_model.read_status(before), check_model.read_status(after)
        if (status_before or "").startswith("approved") and status_after == status_before and body(before) != body(after):
            problems.append(f"model changed: {path}: the model above the notes tail changed while the Status line "
                            f"stayed '{status_after}'; approve the change, or revert it (git diff {base[:12]}...HEAD -- {path})")

    for path in changed:
        if path in ("GLOSSARY.md", "GLOSSARY-MAP.md", "docs/domain/context-map.md") or path.endswith("/GLOSSARY.md"):
            judge.append(f"meaning: {path} changed; check whether it changes what an approved rule means")
        if LINT_CONFIG.search(path):
            removed = [l[1:].strip() for l in git("diff", "--unified=0", "--no-color", f"{base}...HEAD", "--", path).splitlines()
                       if l.startswith("-") and not l.startswith("---") and l[1:].strip()]
            judge.append(f"lint config: {path} changed" + (f"; removed: {' | '.join(removed[:5])}" if removed else "; nothing removed"))

    avoid = []
    glossaries = [pathlib.Path("GLOSSARY.md")] + sorted(pathlib.Path(".").glob("**/GLOSSARY.md"))
    for glossary in dict.fromkeys(g for g in glossaries if g.exists() and "node_modules" not in g.parts):
        _, phrases, _ = check_model.parse_glossary(glossary, "")
        avoid += [(phrase, preferred, check_model.words(phrase.replace(" ", "_").title().replace("_", "")))
                  for phrase, preferred in phrases]

    for path, number, text in added_lines(base):
        if path.startswith(("docs/", "tools/")) or path.endswith(".md"):
            continue
        if SUPPRESSION.search(text):
            judge.append(f"suppression: {path}:{number}: {text.strip()[:120]}")
        if CODE.search(path) and avoid:
            code = re.sub(r"//.*$|/\*.*?\*/|#.*$", "", text)
            for identifier in sorted(set(re.findall(r"[A-Za-z][A-Za-z0-9]*", code))):
                for phrase, preferred, needle in avoid:
                    if needle and check_model.contains(check_model.words(identifier), needle):
                        judge.append(f"avoided word: {path}:{number}: {identifier} uses '{phrase}'; the glossary says {preferred}")

    stems = [pathlib.Path(p).stem for p in sorted(pathlib.Path("docs/domain/contexts").glob("*.md")) if not p.name.startswith("_")] \
        if pathlib.Path("docs/domain/contexts").is_dir() else []
    tested, _ = ddd_status.tested_rows(stems) if stems else ({}, [])
    # A context is touched when the range edits its file, or its code: the only context in the repository, or one whose
    # name is a directory in a changed path. The same rule as ddd_status uses to tie tests to a context.
    code_paths = [c for c in changed if CODE.search(c)]
    touched = sorted({f"docs/domain/contexts/{s}.md" for s in stems
                      if f"docs/domain/contexts/{s}.md" in contexts
                      or (code_paths and (len(stems) == 1 or any(s in pathlib.PurePath(c).parts[:-1] for c in code_paths)))})
    for path in touched:
        stem = pathlib.Path(path).stem
        text = re.sub(r"<!--.*?-->", "", pathlib.Path(path).read_text(), flags=re.S)
        top = check_model.split(text, "## ")
        rows = check_model.table(check_model.find(top, "Examples"))
        for title, section in top:
            if title.lower().startswith("aggregate:"):
                rows += check_model.table(check_model.find(check_model.split(section, "### "), "Examples"))
        missing = [r["#"] for r in rows if r.get("#", "").isdigit() and r["#"] not in tested.get(stem, set())]
        if missing:
            judge.append(f"example untested: {path}: rows {ddd_status.compact(missing)} have no test named 'example <n>'")

    print(f"range: {base[:12]}...{git('rev-parse', 'HEAD').strip()[:12]}")
    for line in problems:
        print(line)
    for line in judge:
        print(f"to judge: {line}")
    if not problems and not judge:
        print("nothing found")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
