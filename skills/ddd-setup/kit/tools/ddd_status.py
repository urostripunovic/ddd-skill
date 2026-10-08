"""Usage: ddd_status.py   (run from the repository root; tools/ddd-status.sh calls it)

Prints where the repository stands in the DDD workflow, as facts, one per line:
what setup installed, each context file's status, depth, review, check result,
open questions, assumptions, amendments, pending gaps and migration steps, which
example rows have a test, and the branch. It decides nothing and changes nothing;
the ddd-next skill reads the output and recommends the next step.

A test counts for an example row when a test file names it: "example 3", "examples 3
and 4", "TestExample3" or "TestExamples9And10". With more than one context file, a
test file counts for a context when it names docs/domain/contexts/<context>.md or
sits under a directory named after the context. Finding no test does not prove there
is none; it means none was named the way ddd-implementation names them.

Exit status is 2 outside a git repository, otherwise 0.
"""
import os
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # a status check leaves no __pycache__ in the repository
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_model  # noqa: E402  (shares the model parser, so both tools read a model the same way)

TEST_FILE = re.compile(
    r"(_test\.go|\.(test|spec)\.[cm]?[jt]sx?|(^|/)test_[^/]*\.py|_test\.py|Tests?\.(java|kt|cs)|_spec\.rb)$"
    r"|(^|/)(__tests?__|tests?|spec)/"
)
EXAMPLE_REF = re.compile(r"examples?[ _-]*(\d+(?:[ _-]*(?:,|and|&)[ _-]*\d+)*)", re.I)
SKIP = ("node_modules/", "vendor/", ".cards-check/", "docs/", ".claude/")


def git(*args):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def plural(count, word):
    return f"{count} {word}" + ("" if count == 1 else "s")


def numbers(found):
    """'3 and 4' -> {'3', '4'}"""
    return set(re.findall(r"\d+", found))


def compact(values):
    """['1', '2', '3', '5'] -> '1-3, 5'"""
    ints = sorted(int(v) for v in values)
    runs, start = [], None
    for i, n in enumerate(ints):
        if start is None:
            start = n
        if i + 1 == len(ints) or ints[i + 1] != n + 1:
            runs.append(str(start) if start == n else f"{start}-{n}")
            start = None
    return ", ".join(runs)


def section_rows(top, title):
    body = check_model.find(top, title)
    return check_model.table(body) if body is not None else []


def setup_lines():
    lines = []
    cards = pathlib.Path("docs/ddd/cards")
    styles = sorted(p for p in cards.iterdir() if p.is_dir() and (p / "README.md").exists()) if cards.is_dir() else []
    earlier = cards.is_dir() and any(cards.glob("[0-9]*.md"))
    for style in styles:
        langs = sorted(p.name for p in style.iterdir() if p.is_dir())
        lines.append(f"cards: {style.name}" + (f", examples for {', '.join(langs)}" if langs else ", no language examples"))
    if earlier:
        lines.append("cards: earlier layout, directly under docs/ddd/cards/; they belong in docs/ddd/cards/functional/")
    if not styles and not earlier:
        lines.append("cards: not installed (model only)")
    if not pathlib.Path("docs/ddd/strategic").is_dir():
        lines.append("strategic cards: not installed")

    instructions = next((p for p in (pathlib.Path("CLAUDE.md"), pathlib.Path("AGENTS.md")) if p.exists()), None)
    text = instructions.read_text() if instructions else ""
    if re.search(r"^## Domain code\s*$", text, re.M):
        style = re.search(r"^\s*[-*]?\s*Code style:\s*(.+)$", text, re.M)
        paths = re.search(r"^\s*[-*]?\s*Domain paths:\s*(.+)$", text, re.M)
        lines.append(f"conventions: recorded in {instructions.name}"
                     + (f"; code style: {style.group(1).strip()}" if style else "")
                     + (f"; domain paths: {paths.group(1).strip()}" if paths else "; no 'Domain paths:' line"))
    else:
        lines.append("conventions: not recorded (no '## Domain code' in CLAUDE.md or AGENTS.md)")

    names = os.listdir(".")
    found = next((n for n in ("GLOSSARY-MAP.md", "GLOSSARY.md", "CONTEXT-MAP.md", "CONTEXT.md") if n in names), None)
    if found and found.startswith("CONTEXT"):
        lines.append(f"glossary: earlier name, {found}; it belongs in {found.replace('CONTEXT', 'GLOSSARY')}")
    elif found and "CONTEXT.md" in names:
        lines.append(f"glossary: {found}; CONTEXT.md, its earlier name, is still there and is no longer read")
    else:
        lines.append(f"glossary: {found or 'none yet'}")

    context_map = pathlib.Path("docs/domain/context-map.md")
    if context_map.exists():
        top = check_model.split(re.sub(r"<!--.*?-->", "", context_map.read_text(), flags=re.S), "## ")
        contexts = [r for r in section_rows(top, "Bounded contexts") if r.get("Context")]
        prototypes = [r for r in section_rows(top, "Prototypes") if r.get("Scope")]
        line = f"context map: {plural(len(contexts), 'context')}"
        if prototypes:
            line += "; prototypes (modelling postponed): " + "; ".join(r["Scope"] for r in prototypes)
        lines.append(line)
    return lines


def test_files():
    listed = git("ls-files", "-co", "--exclude-standard")
    for name in (listed or "").splitlines():
        if TEST_FILE.search(name) and not name.startswith(SKIP) and not any(f"/{s}" in name for s in SKIP):
            path = pathlib.Path(name)
            try:
                yield name, path.read_text(errors="replace")
            except OSError:
                continue


def tested_rows(contexts):
    """Example row numbers named by test files, per context, and the files that could not be tied to one."""
    tested = {stem: set() for stem in contexts}
    loose = []
    for name, text in test_files():
        found = set().union(*(numbers(m.group(1)) for m in EXAMPLE_REF.finditer(text)))
        if not found:
            continue
        if len(contexts) == 1:
            owners = list(contexts)
        else:
            parts = set(pathlib.PurePath(name).parts[:-1])
            owners = [s for s in contexts if f"contexts/{s}.md" in text or s in parts]
        for owner in owners:
            tested[owner] |= found
        if not owners:
            loose.append(name)
    return tested, loose


def context_lines(path, tested):
    raw = path.read_text()
    text = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    top = check_model.split(text, "## ")
    lines = []

    state = check_model.read_status(raw) or "no Status line"
    # Shown as the file reads; the hashes are compared below and by the check.
    lines.append("status: " + re.sub(r",\s*model-hash\s+[0-9a-f]+|\s+at\s+[0-9a-f]+", "", state))

    depth = re.search(r"^Depth:\s*(.+)$", text, re.M)
    strict = re.search(r"^Strict commands:[ \t]*(.+)$", text, re.M)
    lines.append("depth: " + (depth.group(1).strip() if depth else "strict (no Depth line)")
                 + (f"; strict commands: {strict.group(1).strip()}" if strict else ""))

    problems, warnings, _ = check_model.check(path, None)
    if problems:
        edited = [p for p in problems if p.startswith("edited after approval")]
        core = [p for p in problems if "is not confirmed" in p]
        line = f"model check: {plural(len(problems), 'problem')}"
        if edited:
            line += "; edited after approval, so it needs approving again"
        if core:
            line += f"; {len(core)} of them unconfirmed core (Issued by, invariant or Believed when)"
        lines.append(line)
        lines.extend(f"  {p}" for p in problems[:3])
        if len(problems) > 3:
            lines.append(f"  ... run tools/check-model.sh {path} for the rest")
    else:
        lines.append("model check: passed")
    lines.extend(f"  warning: {w}" for w in warnings if "review" in w)

    review = re.search(r"\breviewed\s+([^,\s]+)(?:\s+at\s+([0-9a-f]+))?", state)
    if review:
        current = subprocess.run(
            [str(pathlib.Path(check_model.__file__).with_name("model-hash.sh")), str(path)],
            capture_output=True, text=True).stdout.strip()
        if review.group(2) and current and review.group(2) != current:
            lines.append(f"review: {review.group(1)}, of an earlier version (model changed since)")
        else:
            lines.append(f"review: {review.group(1)}")
    else:
        lines.append("review: none")

    questions = check_model.find(top, "Open questions")
    if questions and questions.strip() and not check_model.NONE.search(questions):
        items = [l for l in questions.splitlines() if re.match(r"\s*([-*]|\d+\.)\s+\S", l)]
        lines.append(f"open questions: {len(items) or 'yes'}")
    else:
        lines.append("open questions: none")

    assumed = len(re.findall(r"\(assumed\)", text))
    amendments = section_rows(top, "Amendments")
    pending = section_rows(top, "Pending")
    lines.append(f"assumed: {assumed}; amendments: {len(amendments)}; pending gaps: {len(pending)}")
    for row in pending:
        lines.append(f"  pending: {row.get('Command', '?')}: {row.get('The gap, and the question for the user', '')}")

    migration = check_model.find(top, "Migration")
    if migration is not None:
        steps = re.findall(r"^\s*(\d+)\.\s+(.+)$", migration, re.M)
        done = [n for n, s in steps if "(done" in s]
        todo = [(n, s) for n, s in steps if "(done" not in s]
        line = f"migration: {len(done)} of {len(steps)} steps done"
        if todo:
            line += f"; next: step {todo[0][0]}: {todo[0][1].strip()}"
        lines.append(line)

    examples, commands = [], set()
    for title, body in top:
        if title.lower().startswith("aggregate:"):
            subs = check_model.split(body, "### ")
            examples += [r for r in check_model.table(check_model.find(subs, "Examples")) if r.get("#")]
            for line in check_model.code(check_model.find(subs, "Commands")).splitlines():
                sig = re.match(r"\s*(\w+)\s*:", line)
                if sig:
                    commands.add(sig.group(1))
    if examples:
        rows = [r["#"] for r in examples if r["#"].isdigit()]
        have = [n for n in rows if n in tested]
        missing = [r for r in examples if r["#"].isdigit() and r["#"] not in tested]
        line = f"examples: {len(rows)} rows; with a test: {compact(have) if have else 'none'}"
        if missing:
            todo_commands = sorted({c for r in missing for c in check_model.names_in(r.get("Covers", "") + " " + r.get("When", ""))
                                    if c in commands})
            line += f"; without: {compact(r['#'] for r in missing)}"
            if todo_commands:
                line += f" (commands: {', '.join(todo_commands)})"
        lines.append(line)
    return lines


def branch_lines():
    if git("rev-parse", "--verify", "--quiet", "HEAD") is None:
        return ["branch: no commits yet"]
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "?"
    base = None
    remote_head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    for candidate in ([remote_head] if remote_head else []) + ["main", "master"]:
        if git("rev-parse", "--verify", "--quiet", candidate) is not None:
            base = candidate
            break
    line = f"branch: {branch}"
    if base and branch not in (base, base.split("/")[-1]):
        ahead = git("rev-list", "--count", f"{base}..HEAD")
        line += f", {ahead} commit(s) ahead of {base}"
    elif base:
        line += " (the default branch)"
    changed = git("status", "--porcelain")
    if changed:
        line += f"; {plural(len(changed.splitlines()), 'uncommitted change')}"
    return [line]


def main():
    if git("rev-parse", "--show-toplevel") is None:
        print("not a git repository", file=sys.stderr)
        return 2
    if not pathlib.Path("docs/domain").is_dir():
        print("setup: not done (no docs/domain/)")
        print(*branch_lines(), sep="\n")
        return 0

    print("setup: done")
    print(*setup_lines(), sep="\n")
    files = sorted(p for p in pathlib.Path("docs/domain/contexts").glob("*.md") if not p.name.startswith("_"))
    if not files:
        print("contexts: none modelled yet")
    tested, loose = tested_rows([p.stem for p in files])
    for path in files:
        print(f"\ncontext {path.stem} ({path}):")
        for line in context_lines(path, tested[path.stem]):
            print(f"  {line}")
    if loose:
        print(f"\ntests naming example rows but tied to no context: {', '.join(loose[:5])}"
              + (" ..." if len(loose) > 5 else "")
              + "; name docs/domain/contexts/<context>.md in them")
    print()
    print(*branch_lines(), sep="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
