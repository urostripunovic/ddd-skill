"""Usage: extract_cards.py <cards-dir> <out-dir> [<lint-dir>]

Writes examples under go/internal/<role>/<card>/x.go or ts/src/<role>/<card>.ts
so the reference configs' domain paths apply. The default role is domain;
an example may declare 'Check as: boundary' when it demonstrates I/O or parsing.
A language whose directory is not installed is skipped.

With <lint-dir>, it also writes that directory's lint configs next to the
examples, with the lines marked DOMAIN-PATHS pointing at the extracted domain
examples. The team's own rules in those configs are kept; only the paths change,
so setting your own domain paths in tools/lint/ cannot switch the domain rules
off for the cards.
"""
import pathlib
import re
import sys

GO_DOMAIN = ("**/internal/domain/**", "internal/domain/")
TS_DOMAIN = "src/domain/**/*.ts"


def pin_go(text):
    lines, out, i, pinned = text.splitlines(), [], 0, 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        if "DOMAIN-PATHS" not in line:
            continue
        while i < len(lines) and lines[i].lstrip().startswith("#"):
            out.append(lines[i])
            i += 1
        if i >= len(lines):
            continue
        files = re.match(r"^(\s*)files:\s*$", lines[i])
        except_ = re.match(r"^(\s*)- path-except:", lines[i])
        if files:
            out.append(lines[i])
            i += 1
            indent = None
            while i < len(lines) and re.match(r"^\s*(-|#)", lines[i]):
                indent = indent or re.match(r"^(\s*)", lines[i]).group(1)
                if lines[i].lstrip().startswith("#"):
                    out.append(lines[i])
                i += 1
            indent = indent or files.group(1) + "  "
            out += [f'{indent}- "{GO_DOMAIN[0]}"', f'{indent}- "!$test"']
            pinned += 1
        elif except_:
            out.append(f"{except_.group(1)}- path-except: {GO_DOMAIN[1]}")
            i += 1
            pinned += 1
    return "\n".join(out) + "\n", pinned


def pin_ts(text):
    return re.subn(r"(DOMAIN-PATHS[^\n]*\n(?:\s*//[^\n]*\n)*\s*files:\s*)\[[^\]]*\]", rf'\1["{TS_DOMAIN}"]', text)


def write_lint(lint_dir, out, lang):
    if lang == "go":
        name, expected, pin = ".golangci.yml", 2, pin_go
    else:
        name, expected, pin = "eslint.config.mjs", 1, pin_ts
    source = lint_dir / name
    if not source.exists():
        sys.exit(f"no {source}; the card examples are checked with it")
    text, pinned = pin(source.read_text())
    if pinned != expected:
        sys.exit(f"{source}: expected {expected} place(s) marked DOMAIN-PATHS, found {pinned}; keep the markers above the domain paths")
    (out / lang).mkdir(parents=True, exist_ok=True)
    (out / lang / name).write_text(text)


def main(argv):
    cards_dir, out = pathlib.Path(argv[0]), pathlib.Path(argv[1])
    lint_dir = pathlib.Path(argv[2]) if len(argv) > 2 else None
    cards = sorted(p.name for p in cards_dir.glob("[0-9]*.md"))
    missing = []
    for lang in ("go", "ts"):
        if not (cards_dir / lang).is_dir():
            continue
        count = 0
        for card in cards:
            example = cards_dir / lang / card
            text = example.read_text() if example.exists() else ""
            blocks = re.findall(rf"```{lang}\n(.*?)```", text, re.S)
            if not blocks:
                missing.append(f"{lang}/{card}")
                continue
            name = card.removesuffix(".md").replace("-", "_")
            roles = re.findall(r"^Check as:[ \t]*(.*)$", text, re.M)
            role = roles[0].strip() if roles else "domain"
            if len(roles) > 1 or role not in ("domain", "boundary"):
                sys.exit(f"invalid Check as role in {example}: expected domain or boundary")
            if lang == "go":
                # One package per card, because the cards reuse type names.
                target = out / "go" / "internal" / role / ("c" + name) / "x.go"
            else:
                target = out / "ts" / "src" / role / (name + ".ts")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(blocks[-1])
            count += 1
        if lint_dir:
            write_lint(lint_dir, out, lang)
        print(f"{lang}: extracted {count} examples")
    if missing:
        # A card without an example in an installed language would otherwise go unnoticed.
        sys.exit("no example for: " + ", ".join(missing))


if __name__ == "__main__":
    main(sys.argv[1:])
