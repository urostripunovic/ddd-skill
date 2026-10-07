"""Usage: check_model.py [--glossary PATH] [--approving] <context-file>...

Checks selected structural properties: that every section of the template is
present (with "None." where there is nothing), state-field type references, command
signature/table agreement, incoming/outgoing command mentions, matrix cells,
example mentions for commands and decision failures, unique example numbers,
selected glossary names, rejected synonyms and the terms each context-map row says cross
this context's boundary, depth override names, approval
hash boundaries, and that no 'Issued by' cell, invariant or 'Believed when' cell of
a fact from outside is marked (assumed) or left as a placeholder such as TBD. For each name on a "Strict commands:" line it
prints the strict scope: the command's own rows, the rows that name it, and every
primitive its states and inputs use.

An approved status is checked against its depth. At strict depth it may not rest
on (assumed) entries, open questions, amendment rows or a missing or out-of-date
review. With strict commands, the same holds for their strict scope.

It does not prove reachability from creation, resolve event/failure payload
types, judge whether an outside fact's trust rule is sufficient, cover use-case failures or all glossary
terms, or judge examples against rules. Review those at the chosen depth.

A missing or unconfirmed 'Believed when' cell joined the core after models were approved without
it, so in an approved model it is a warning, to settle at the next change. It is an
error in a draft, and with --approving, which tools/stamp-model.sh passes, so no new
approval rests on it.

Exit status is 1 when any problem is found. Lines starting with "warning:" and the
strict-scope lines do not change the exit status.
"""
import os
import pathlib
import re
import subprocess
import sys

BUILTIN = {"Timestamp", "Boolean", "NonEmpty", "List", "Set", "Map", "Optional"}
NONE = re.compile(r"^\s*none\b", re.I | re.M)
PLACEHOLDER = re.compile(r"tbd|tbc|to be (decided|confirmed)|unknown|open( question)?|see open questions|\?+")


def read_status(raw):
    """The Status line in its long form, "approved by X on D, model-hash H, reviewed D at H", whichever form
    the file uses. tools/stamp-model.sh writes the hashes in a comment at the end of the line, so the line
    reads short; models stamped before that have them in the text. None without a Status line."""
    line = re.search(r"^Status:([^\n]*)$", raw, re.M)
    if not line:
        return None
    hidden = " ".join(re.findall(r"<!--(.*?)-->", line.group(1)))
    state = re.sub(r"<!--.*?-->", "", line.group(1)).strip().rstrip(",").strip()
    approved_hash = re.search(r"model-hash\s+([0-9a-f]+)", hidden)
    review_hash = re.search(r"reviewed at\s+([0-9a-f]+)", hidden)
    review = re.search(r"\breviewed\s+[^,\s]+", state)
    if approved_hash and "model-hash" not in state:
        end = review.start() if review else len(state)
        state = state[:end].rstrip().rstrip(",") + f", model-hash {approved_hash.group(1)}" + (", " + state[end:] if review else "")
        review = re.search(r"\breviewed\s+[^,\s]+", state)
    if review_hash and review and not re.search(r"\breviewed\s+[^,\s]+\s+at\s", state):
        state = state[:review.end()] + f" at {review_hash.group(1)}" + state[review.end():]
    return state


def unconfirmed(cell):
    """True for a core cell nobody confirmed: marked (assumed), or a placeholder standing in for an answer."""
    text = (cell or "").strip().rstrip(".").strip().lower()
    return "(assumed)" in text or bool(PLACEHOLDER.fullmatch(text))


def split(text, marker):
    """Sections under headings that start with marker ('## ' or '### '), as (title, body) pairs."""
    parts = re.split(rf"^{re.escape(marker)}(.+)$", text, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def find(sections, title):
    for name, body in sections:
        if name.lower().startswith(title.lower()):
            return body
    return None


def table(body):
    """Rows of the first markdown table in body, as dicts keyed by header. Rows with no content are dropped."""
    lines = [l.strip() for l in (body or "").splitlines() if l.strip().startswith("|")]
    if len(lines) < 2:
        return []
    cells = lambda l: [c.strip() for c in l.strip("|").split("|")]
    header = cells(lines[0])
    rows = []
    for line in lines[2:]:
        row = dict(zip(header, cells(line)))
        if any(row.values()):
            rows.append(row)
    return rows


def code(body):
    m = re.search(r"```[^\n]*\n(.*?)```", body or "", re.S)
    return m.group(1) if m else ""


def names_in(cell):
    return re.findall(r"[A-Z][A-Za-z0-9]*", cell or "")


def words(name):
    """'SubmittedOrders' -> ['submitted', 'order'], so 'Submitted order' in an Avoid list matches it."""
    parts = re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+", name)
    return [p.lower()[:-1] if len(p) > 3 and p.lower().endswith("s") else p.lower() for p in parts]


def contains(haystack, needle):
    return any(haystack[i:i + len(needle)] == needle for i in range(len(haystack) - len(needle) + 1))


# CONTEXT.md is the name Matt Pocock's skills read; GLOSSARY.md is the name earlier versions of the kit wrote.
GLOSSARY_NAMES = [("CONTEXT-MAP.md", "CONTEXT.md"), ("GLOSSARY-MAP.md", "GLOSSARY.md")]


def load_glossary(context_file, context_name, override):
    """Follows the layout of the shared glossary: a root CONTEXT.md, or a CONTEXT-MAP.md that links to one per context.
    Returns the glossary's path and the name of the file that led to it."""
    if override:
        return pathlib.Path(override), None
    for folder in [context_file.resolve().parent, *context_file.resolve().parents]:
        # Exact names: on a case-insensitive file system, docs/domain/context-map.md would pass for CONTEXT-MAP.md.
        names = set(os.listdir(folder))
        for map_name, glossary_name in GLOSSARY_NAMES:
            glossary_map = folder / map_name
            if map_name in names:
                for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", glossary_map.read_text()):
                    if label.strip().lower() == context_name.lower():
                        return (folder / target).resolve(), map_name
                return None, map_name
            if glossary_name in names:
                return folder / glossary_name, glossary_name
        if (folder / ".git").exists():
            return None, None
    return None, None


def parse_glossary(path, context_name):
    """An _Avoid_ or a term under another context's '# <Context>' heading is that context's, when the file has one for
    this context: Billing may avoid a word that Payments uses. Without a heading for this context, all of them apply.
    Returns every term, the _Avoid_ entries that apply, and this context's own terms."""
    terms, avoid, scoped, placed = set(), [], [], []
    current, section, sections = None, None, set()
    for line in path.read_text().splitlines():
        heading = re.match(r"#\s+(.+?)\s*$", line)
        if heading:
            section = heading.group(1).lower()
            sections.add(section)
        term = re.match(r"\*\*(.+?)\*\*\s*:", line)
        if term:
            current = term.group(1).strip()
            terms.add(re.sub(r"[^a-z0-9]", "", current.lower()))
            placed.append((re.sub(r"[^a-z0-9]", "", current.lower()), section))
        rejected = re.match(r"_Avoid_\s*:\s*(.+)", line.strip())
        if rejected and current:
            for phrase in rejected.group(1).split(","):
                if phrase.strip():
                    scoped.append((phrase.strip(), current, section))
    applies = lambda where: context_name.lower() not in sections or where in (None, context_name.lower())
    avoid = [(phrase, preferred) for phrase, preferred, where in scoped if applies(where)]
    return terms, avoid, {term for term, where in placed if applies(where)}


def crossing_terms(path, context):
    """The terms this context's glossary must hold for its rows in docs/domain/context-map.md, as (term, why) pairs.

    Upstream: every term under 'What crosses the boundary'. Downstream: the same terms when Translation is 'none'
    (conformist), otherwise the CamelCase names Translation gives, such as 'arrives in the domain as a ChargeOutcome'.
    A side that is an outside system has no glossary and is not checked; nothing syncs the two glossaries' other terms.
    Separate ways crosses nothing, and a published language's row names the language, not terms: neither is checked."""
    context_map = path.resolve().parent.parent / "context-map.md"
    if not context_map.exists():
        return []
    top = split(re.sub(r"<!--.*?-->", "", context_map.read_text(), flags=re.S), "## ")
    needed = []
    for row in table(find(top, "Relationships")):
        upstream, downstream = row.get("Upstream", "").strip(), row.get("Downstream", "").strip()
        if re.search(r"separate ways|published language", row.get("Pattern", ""), re.I):
            continue
        crossing = [re.split(r"[{(]", term)[0].strip() for term in row.get("What crosses the boundary", "").split(",")]
        crossing = [term for term in crossing if term and term.rstrip(".").lower() not in ("nothing", "none")]
        translation = row.get("Translation", "").strip()
        if upstream.lower() == context.lower():
            needed += [(term, f"crosses the boundary to {downstream}") for term in crossing]
        elif downstream.lower() == context.lower():
            if translation.rstrip(".").lower() == "none":
                needed += [(term, f"arrives from {upstream} untranslated") for term in crossing]
            else:
                sides = {upstream.replace(" ", "").lower(), downstream.replace(" ", "").lower()}
                needed += [(name, f"is how {upstream} arrives, the Translation says")
                           for name in re.findall(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+\b", translation)
                           if name.lower() not in sides]
    return needed


def strict_scope(command, signature, subs, examples, primitives, defs, policies):
    """What a strict command pulls into strict depth: its own rows, the rows that name it and the primitives it touches.

    Returns the command, the parts to print, the text of every row in the scope, and the names in it."""
    named = lambda cell: bool(re.search(rf"\b{command}\b", cell or ""))
    parts, cells, names = [], [], {command}

    def take(label, rows, key, separator=", "):
        if rows:
            parts.append(label + " " + separator.join(key(r) for r in rows))
            cells.extend(value for r in rows for value in r.values())

    take("issued by:", [r for r in table(find(subs, "Commands")) if r.get("Command") == command],
         lambda r: r.get("Issued by", "") or "?")
    matrix = table(next((b for t, b in subs if t.lower().startswith("command") and "matrix" in t.lower()), None))
    column = [r for r in matrix if r.get(command) is not None]
    if column:
        parts.append("matrix column " + command)
        cells.extend(r[command] for r in column)
    take("examples", [r for r in examples if named(r.get("Covers")) or named(r.get("When"))], lambda r: r.get("#", "?"))
    take("invariants", [r for r in table(find(subs, "Invariants"))
                        if named(r.get("Commands that could break it")) or named(r.get("Enforced by"))],
         lambda r: r.get("#", "?"))
    take("failures", [r for r in table(find(subs, "Failures")) if r.get("Failure") in signature["failures"]],
         lambda r: r.get("Failure", ""))
    take("use-case failures", [r for r in table(find(subs, "Use-case failures")) if named(" ".join(r.values()))],
         lambda r: r.get("Failure", "?"))
    take("events", [r for r in table(find(subs, "Events")) if r.get("Event") in signature["events"]],
         lambda r: r.get("Event", ""))
    take("races", [r for r in table(find(subs, "Races")) if named(r.get("Commands"))],
         lambda r: r.get("Commands", ""), "; ")
    take("facts", [r for r in table(find(subs, "Facts from outside"))
                   if named(r.get("Used by")) or re.search(r"\b(every|all)\b", r.get("Used by", ""), re.I)],
         lambda r: (names_in(r.get("Fact", "")) or ["?"])[0])
    take("policies", [r for r in policies if named(r.get("Then (command)"))
                      or any(re.search(rf"\b{e}\b", r.get("When (event)", "")) for e in signature["events"])],
         lambda r: f"{r.get('When (event)', '')} -> {r.get('Then (command)', '')}", "; ")

    # Every primitive the command reads, writes or takes as input: a value that already exists in the
    # state it starts from (the amount being charged, say) is as much in scope as one it adds.
    found, todo = set(), [*signature["sources"], *signature["targets"], *signature["inputs"]]
    while todo:
        name = todo.pop()
        if name in found:
            continue
        found.add(name)
        todo.extend(defs.get(name, []))
    touched = sorted(found & set(primitives))
    take("primitives", [primitives[name] for name in touched], lambda r: r.get("Name", ""))
    names.update(signature["failures"], signature["events"], touched)
    return command, parts, cells, names


def check_approval(state, hashed, depth, strict_commands, scopes, top, assumed, err, warnings):
    """What an approved status may rest on. Strict depth is held to 'everything confirmed and reviewed'."""
    actual = hashed.stdout.strip() if hashed.returncode == 0 else None
    review = re.search(r"\breviewed\s+[^,\s]+(?:\s+at\s+([0-9a-f]+))?", state)
    review_hash = review.group(1) if review else None
    stale = bool(review_hash and actual and review_hash != actual)
    restamp = "review the changed rows with ddd-model-review, then run tools/stamp-model.sh review <file>"

    if not state.lower().startswith("approved"):
        if stale:
            warnings.append(f"the review on the Status line is of model-hash {review_hash}; the model has changed since, so {restamp}")
        return

    recorded = re.search(r"model-hash\s+([0-9a-f]+)", state)
    if not recorded:
        err("approved without a model-hash, so the approval cannot be verified; approve with tools/stamp-model.sh approve <file> <name>")
    elif actual and actual != recorded.group(1):
        err(f"edited after approval: the Status line records model-hash {recorded.group(1)}, the file now hashes to {actual}")

    questions = find(top, "Open questions")
    open_questions = bool(questions and questions.strip() and not NONE.search(questions))
    amendments = table(find(top, "Amendments"))
    pending = table(find(top, "Pending"))
    if pending:
        warnings.append(f"{len(pending)} gap(s) under Pending: implementation is waiting for them to be settled in the model")

    if not depth or depth.group(1).strip() == "strict":
        if assumed:
            err(f"strict depth, approved with {assumed} (assumed) marker(s): at strict depth everything is confirmed")
        if open_questions:
            err("strict depth, approved with open questions: answer them before approval")
        if amendments:
            err(f"strict depth, {len(amendments)} amendment row(s): at strict depth a gap stops implementation and changes the model through ddd-modelling")
        if not review:
            err("strict depth, approved without a review: run ddd-model-review in a fresh session, then tools/stamp-model.sh review <file>")
        elif not review_hash:
            warnings.append("the review on the Status line names no model-hash, so it cannot be tied to this version of the model")
        elif stale:
            err(f"strict depth: the review is of model-hash {review_hash}, the approved model is {actual}; {restamp}")
        return

    if open_questions:
        warnings.append("approved with open questions")
    if amendments:
        warnings.append(f"{len(amendments)} amendment(s) since approval: fold them into the model and approve again when convenient")
    for command, _, cells, names in scopes:
        if any("(assumed)" in cell for cell in cells):
            err(f"strict scope of {command} has entries marked (assumed): confirm them before approval")
        touching = [row for row in amendments
                    if any(re.search(rf"\b{re.escape(name)}\b", " ".join(row.values())) for name in names)]
        if touching:
            err(f"strict scope of {command}: {len(touching)} amendment row(s) touch it; a gap in a strict scope changes the model through ddd-modelling")
    if strict_commands:
        if not review:
            err("approved with strict commands, but their strict scope was not reviewed: run ddd-model-review, then tools/stamp-model.sh review <file>")
        elif not review_hash:
            warnings.append("the review on the Status line names no model-hash, so it cannot be tied to this version of the model")
        elif stale:
            warnings.append(f"the review is of model-hash {review_hash}, the approved model is {actual}. If the change touched a strict scope, "
                            f"{restamp}; if it touched none, re-stamp the review and say so")


def check(path, glossary_override, approving=False):
    problems, warnings, notes = [], [], []
    err = problems.append
    raw = path.read_text()
    text = re.sub(r"<!--.*?-->", "", raw, flags=re.S)

    title = re.search(r"^# Context:\s*(.+)$", text, re.M)
    context = title.group(1).strip() if title else path.stem
    top = split(text, "## ")

    hasher = pathlib.Path(__file__).with_name("model-hash.sh")
    hashed = subprocess.run([str(hasher), str(path)], capture_output=True, text=True)
    if hashed.returncode:
        err("model hash failed: " + (hashed.stderr.strip() or "no diagnostic"))

    state = read_status(raw)
    status = re.match(r"(.+)", state) if state else None
    if not status:
        err("no Status line")
    # A rule added to the core after approval is settled at the next change, not by breaking the approval.
    earlier_approval = bool(status and status.group(1).lower().startswith("approved") and not approving)

    depth = re.search(r"^Depth:\s*(.+)$", text, re.M)
    if depth and depth.group(1).strip() not in ("standard", "strict"):
        err(f"Depth is '{depth.group(1).strip()}'; it is 'standard' or 'strict'")
    overrides = re.findall(r"^Strict commands:[ \t]*(.*)$", text, re.M)
    strict_commands = []
    if len(overrides) > 1:
        err("more than one Strict commands line; use one comma-separated list")
    if overrides:
        strict_commands = [name.strip() for name in overrides[0].split(",")]
        if any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name) for name in strict_commands):
            err("Strict commands must be a comma-separated list of command names; omit the line when none are strict")
    assumed = len(re.findall(r"\(assumed\)", text))
    if assumed:
        warnings.append(f"{assumed} assumption(s) nobody has confirmed, marked (assumed)")

    primitives = {}
    for row in table(find(top, "Domain primitives")):
        name = row.get("Name", "")
        if not name:
            continue
        primitives[name] = row
        for column in row:
            if column != "Name" and not row[column]:
                err(f"primitive {name}: the '{column}' cell is empty")

    flow = find(top, "The flow")
    if flow is None:
        err("no 'The flow' section")
    elif not re.search(r"^\s*\d+\.", flow, re.M):
        err("'The flow' has no numbered steps")
    for section in ("Domain primitives", "Rules across aggregates", "Policies", "Decisions", "Open questions"):
        body = find(top, section)
        if body is None:
            err(f"no '{section}' section")
        elif section != "Open questions" and not table(body) and not NONE.search(body):
            err(f"'{section}' has no rows; write 'None.' if the question was asked and the answer is none")

    aggregates = [(t, b) for t, b in top if t.lower().startswith("aggregate:")]
    if not aggregates:
        err("no '## Aggregate: <name>' section")

    # Types are collected from every aggregate first, because one aggregate may refer to another's value types.
    parsed = []
    defined = dict.fromkeys(primitives, "primitive")
    for title_, body in aggregates:
        subs = split(body, "### ")
        block = code(find(subs, "States"))
        agg = {"name": title_.split(":", 1)[1].strip(), "subs": subs, "states": [], "terminal": set(), "defs": {}, "fields": set(), "sum": None}
        for line in block.splitlines():
            line = line.strip()
            sum_type = re.match(r"type\s+(\w+)\s*=\s*(.+)", line)
            definition = re.match(r"(\w+)\s*=\s*(.+)", line)
            if sum_type:
                agg["sum"] = sum_type.group(1)
                agg["states"] = [s.strip() for s in sum_type.group(2).split("|")]
            elif line.startswith("terminal"):
                agg["terminal"] = set(names_in(line))
            elif definition:
                body_ = re.sub(r"\(.*?\)", "", definition.group(2))
                agg["defs"][definition.group(1)] = names_in(re.sub(r"\b\w+\s*:", "", body_))
                agg["fields"].update(re.findall(r"\b(\w+)\s*:", body_))
        for row in table(find(subs, "Facts from outside")):
            fact = names_in(row.get("Fact", ""))
            if fact:
                agg["defs"].setdefault(fact[0], [])
        for name in [agg["sum"], *agg["defs"]]:
            if name and name in defined:
                err(f"{name} is defined twice")
            if name:
                defined[name] = "type"
        parsed.append(agg)

    all_names, glossary_needed, all_commands = set(defined), set(), set()
    all_defs = {name: refs for agg in parsed for name, refs in agg["defs"].items()}
    signatures, scopes = {}, []
    for agg in parsed:
        subs, states, where = agg["subs"], agg["states"], f"aggregate {agg['name']}"
        if not agg["sum"]:
            err(f"{where}: the States block has no 'type X = A | B' line")
            continue
        glossary_needed.update([agg["sum"], *[d for d in agg["defs"]]])
        all_names.update(agg["fields"])
        for state in states:
            if state not in agg["defs"]:
                err(f"{where}: state {state} is in the sum type but is never defined")
        for name, refs in agg["defs"].items():
            for ref in refs:
                if ref not in defined and ref not in BUILTIN:
                    err(f"{where}: {name} uses {ref}, which is neither a primitive nor a defined type")
        for state in agg["terminal"] - set(states):
            err(f"{where}: 'terminal {state}' names something that is not a state")

        failures = {r.get("Failure", ""): r for r in table(find(subs, "Failures")) if r.get("Failure")}
        events = {r.get("Event", ""): r for r in table(find(subs, "Events")) if r.get("Event")}
        commands, returned, emitted, produced = {}, set(), set(), set()
        for line in code(find(subs, "Commands")).splitlines():
            sig = re.match(r"\s*(\w+)\s*:\s*(.+?)\s*->\s*(.+)", line)
            if not sig:
                continue
            name, sources = sig.group(1), [s.strip() for s in sig.group(2).split("|")]
            creating = sources == ["()"]
            if not creating:
                for source in sources:
                    if source not in states:
                        err(f"{where}: command {name} starts from {source}, which is not a state")
            targets, own_events, own_failures = [], set(), set()
            for part in sig.group(3).split("|"):
                result = part.split("+")[0].strip()
                if result in states:
                    targets.append(result)
                    for event in names_in(part.split("+", 1)[1]) if "+" in part else []:
                        emitted.add(event)
                        own_events.add(event)
                        if event not in events:
                            err(f"{where}: command {name} emits {event}, which is not in the Events table")
                else:
                    returned.add(result)
                    own_failures.add(result)
                    if result not in failures:
                        err(f"{where}: command {name} returns {result}, which is neither a state nor in the Failures table")
            if not targets:
                err(f"{where}: command {name} has no resulting state")
            produced.update(targets)
            commands[name] = set() if creating else set(sources)
            signatures[name] = {"sources": commands[name], "targets": set(targets), "events": own_events, "failures": own_failures, "inputs": set()}
        if not commands:
            err(f"{where}: the Commands block has no 'Name : State -> State' lines")
        all_names.update([*commands, *events, *failures])
        all_commands.update(commands)

        listed = {r.get("Command", ""): r for r in table(find(subs, "Commands")) if r.get("Command")}
        for name in commands:
            issuer = listed.get(name, {}).get("Issued by")
            if not issuer:
                err(f"{where}: command {name} has no 'Issued by'")
            elif unconfirmed(issuer):
                err(f"{where}: command {name}: 'Issued by' is not confirmed ({issuer}); who may issue a command is part of the core, so ask the user and write their answer")
            # The optional Input column names the values a command takes that are not in the state it starts from.
            for ref in names_in(listed.get(name, {}).get("Input", "")):
                if ref not in defined and ref not in BUILTIN:
                    err(f"{where}: command {name} takes {ref}, which is neither a primitive nor a defined type")
                signatures[name]["inputs"].add(ref)
        for name in set(listed) - set(commands):
            err(f"{where}: the Commands table lists {name}, which has no signature")
        for name in set(events) - emitted:
            err(f"{where}: event {name} is listed, but no command emits it")
        for name, row in events.items():
            if not row.get("Consumed by"):
                err(f"{where}: event {name} has no consumer; write who needs it, or remove it")
        for name in set(failures) - returned:
            err(f"{where}: failure {name} is listed, but no command returns it")

        for state in states:
            if state not in produced:
                err(f"{where}: no command lists {state} as a result")
            leaves = any(state in sources for sources in commands.values())
            if state in agg["terminal"] and leaves:
                err(f"{where}: {state} is marked terminal, but a command starts from it")
            if state not in agg["terminal"] and not leaves:
                err(f"{where}: no command starts from {state}; mark it terminal or say how it ends")

        for row in table(find(subs, "Invariants")):
            number = row.get("#", "?")
            if unconfirmed(row.get("Invariant")):
                err(f"{where}: invariant {number} is not confirmed ({row.get('Invariant')}); invariants are part of the core, so ask the user and write their answer")
            if not row.get("Enforced by"):
                err(f"{where}: invariant {number} does not say where it is enforced")
            named = re.search(r"decision function (\w+)", row.get("Enforced by", ""))
            if named and named.group(1) not in commands:
                err(f"{where}: invariant {number} is enforced by {named.group(1)}, which is not a command")
            breakers = row.get("Commands that could break it", "")
            if not breakers:
                err(f"{where}: invariant {number} does not say which commands could break it")
            for name in names_in(breakers):
                if name not in commands:
                    err(f"{where}: invariant {number} names {name}, which is not a command")

        for row in table(find(subs, "Facts from outside")):
            fact = row.get("Fact", "?")
            believed = row.get("Believed when")
            if (not believed or unconfirmed(believed)) and earlier_approval:
                warnings.append(f"{where}: fact {fact}: 'Believed when' is {'missing' if not believed else f'not confirmed ({believed})'}. "
                                "The model was approved before trust rules were part of the core; confirm it with the user at the next change to this model")
            elif not believed:
                err(f"{where}: fact {fact} does not say when it is believed")
            elif unconfirmed(believed):
                err(f"{where}: fact {fact}: 'Believed when' is not confirmed ({believed}); what makes a caller or an outside fact trusted is part of the core, so ask the user and write their answer")

        columns = {c: s for c, s in commands.items() if s}
        matrix = table(next((b for t, b in subs if t.lower().startswith("command") and "matrix" in t.lower()), None))
        if not matrix:
            err(f"{where}: no command x state matrix")
        else:
            rows = {r.get("State", ""): r for r in matrix}
            for state in set(states) - set(rows):
                err(f"{where}: the matrix has no row for {state}")
            for command in set(columns) - set(matrix[0]):
                err(f"{where}: the matrix has no column for {command}")
            for state, row in rows.items():
                for command, legal in columns.items():
                    cell = row.get(command)
                    if cell is None or state not in states:
                        continue
                    if state in legal and cell.lower() != "yes":
                        err(f"{where}: matrix {state} x {command} should be 'yes'; the command's signature starts from {state}")
                    elif state not in legal and not re.match(r"no:\s*\S", cell, re.I):
                        err(f"{where}: matrix {state} x {command} needs 'no: <the business's reason>'")
            use_case = " ".join(" ".join(r.values()) for r in table(find(subs, "Use-case failures")))
            for command, legal in columns.items():
                refused = [s for s in states if s not in legal and s in rows]
                if refused and not re.search(rf"\b{command}\b", use_case):
                    warnings.append(f"{where}: the matrix refuses {command} in {', '.join(refused)}, but no Use-case failures row names {command}; name the failure the workflow returns")

        for section in ("Events", "Invariants", "Failures", "Use-case failures", "Facts from outside"):
            body = find(subs, section)
            if body is None:
                err(f"{where}: no '{section}' section")
            elif not table(body) and not NONE.search(body):
                err(f"{where}: '{section}' has no rows; write 'None.' if there are none")

        examples = table(find(subs, "Examples"))
        if not examples:
            err(f"{where}: no examples")
        numbers = [row.get("#", "") for row in examples if row.get("#")]
        for number in sorted({n for n in numbers if numbers.count(n) > 1}):
            err(f"{where}: example number {number} is used twice; numbers are permanent, so give a new row the next unused number")
        for row in examples:
            for column in ("Given", "When", "Then"):
                if not row.get(column):
                    err(f"{where}: example {row.get('#', '?')} has no '{column}'")
        mentions = lambda name, cols: any(re.search(rf"\b{name}\b", row.get(c, "")) for row in examples for c in cols)
        for name in commands:
            if examples and not mentions(name, ("Covers", "When")):
                err(f"{where}: command {name} has no example")
        for name in failures:
            if examples and not mentions(name, ("Covers", "Then")):
                err(f"{where}: failure {name} has no example")

        races = find(subs, "Races")
        if races is None or (not table(races) and not NONE.search(races)):
            err(f"{where}: 'Races' is empty; write 'None.' if no two commands can clash")

        for command in [c for c in strict_commands if c in signatures and c in commands]:
            scopes.append(strict_scope(command, signatures[command], subs, examples, primitives, all_defs,
                                       table(find(top, "Policies"))))

    for command, parts, _, _ in scopes:
        notes.append(f"strict scope for {command}: " + ("; ".join(parts) or "the command alone"))

    for name in sorted(set(strict_commands) - all_commands):
        err(f"Strict commands names {name!r}, which has no command signature")

    if status:
        check_approval(status.group(1), hashed, depth, strict_commands, scopes, top, assumed, err, warnings)

    glossary, found = load_glossary(path, context, glossary_override)
    if found and found.startswith("GLOSSARY"):
        warnings.append(f"{found} is the glossary's earlier name; rename it to {found.replace('GLOSSARY', 'CONTEXT')} "
                        "so other skills read it (ddd-setup's UPGRADING.md)")
    if glossary is None or not glossary.exists():
        err("no glossary found: expected CONTEXT.md at the repository root, or an entry for this context in CONTEXT-MAP.md")
    else:
        terms, avoid, own = parse_glossary(glossary, context)
        for name in sorted(glossary_needed):
            if re.sub(r"[^a-z0-9]", "", name.lower()) not in terms:
                err(f"{name} is not in {glossary.name}")
        for term, why in crossing_terms(path, context):
            if re.sub(r"[^a-z0-9]", "", term.lower()) in own:
                continue
            message = (f"{term} {why} (docs/domain/context-map.md), but it is not in {context}'s {glossary.name}. "
                       "Define it there, or, if the map cell is prose, rewrite it as glossary terms, comma-separated")
            if earlier_approval:
                warnings.append(message + "; add it at the next change to this model")
            else:
                err(message)
        for phrase, preferred in avoid:
            needle = words(phrase.replace(" ", "_").title().replace("_", ""))
            for name in sorted(all_names):
                if contains(words(name), needle):
                    err(f"{name} uses '{phrase}', which {glossary.name} lists under Avoid for {preferred}")

    return problems, warnings, notes


def main(argv):
    glossary = None
    approving = "--approving" in argv
    argv = [a for a in argv if a != "--approving"]
    if argv[:1] == ["--glossary"]:
        glossary, argv = argv[1], argv[2:]
    if not argv:
        print(__doc__)
        return 2
    failed = False
    for name in argv:
        problems, warnings, notes = check(pathlib.Path(name), glossary, approving)
        for message in notes:
            print(f"{name}: {message}")
        for message in warnings:
            print(f"{name}: warning: {message}")
        for message in problems:
            print(f"{name}: {message}")
        failed = failed or bool(problems)
        if not problems:
            print(f"{name}: model check passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
