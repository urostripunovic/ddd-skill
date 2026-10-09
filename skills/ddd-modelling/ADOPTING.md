# Adopting existing code

Use this when a repository already has domain code and no model, and the user has chosen to start from the code. The goal is a confirmed model for one aggregate at a time, and a plan to move the code towards it. Do not try to model the whole repository in one pass.

The notation is in [NOTATION.md](NOTATION.md), the glossary format in [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md) and the way of asking in [INTERVIEW.md](INTERVIEW.md); depth, approval and the notes tail are in the lifecycle files SKILL.md names.

## 1. Pick one slice

Ask which aggregate or area matters most, or propose the one the user is about to change. Name the files that belong to it.

## 2. Derive a draft from the code

Read that slice and write what the code does today, with a `file:line` reference for every item so the user can check it.

- **Terms**: the names the code uses. Flag technical ones (manager, record, DTO, status) and synonyms.
- **States**: from status fields, enums, nullable fields and flags. Note which field combinations the code treats as each state.
- **Transitions**: every place the status or its fields change, and what is checked first. Fill in the matrix from these: `yes` where the code allows the command in that state, and `no: the code rejects it at <file:line>` or `no: nothing in the code does this` elsewhere.
- **Invariants**: from validation code and conditionals. Note where the same rule is checked in several places, or in only some of them.
- **Primitives**: raw strings and numbers that are validated somewhere, and the bounds found there.
- **Examples**: from the existing tests. A test that pins a rule with real values is an example already; cite it.
- **Races**: whether the code does anything when two requests change the same thing: a version column, a lock, a transaction. "Nothing" is a finding, not a gap in your reading.

Set the status line to `Status: derived from code, not confirmed, read at <short commit>`, where the commit is `HEAD` when you read the slice. Code shows what the system does, not what the business intends.

## 3. Cross-check with the user

Go through the draft with the user and compare it with what they say the business does.

- Where the code and the user agree, mark the item confirmed.
- Where they differ, do not pick a side. List it as a discrepancy: it is either a bug in the code or a rule the user forgot. The user decides which.
- Every `no` cell that the code gave a technical reason for needs the business's reason. Ask.
- Ask about what the code cannot show using the chosen depth: who may issue each command, which values are sensitive, and the questions under "Ask what the timeline hides". At standard depth, propose non-core details together as assumptions rather than asking about every one.

Then write the target model in the normal notation: states and legal commands. This notation describes behaviour; it does not require matching state types in the code. Run `tools/check-model.sh` and get approval as lifecycle/approval.md describes.

If the slice is a prototype scope, its row stays while the model is a draft ([lifecycle/adoption.md](lifecycle/adoption.md)). Before asking for approval, check what changed in the slice since you read it: `git log --oneline <commit>..HEAD -- <files>` with the commit from the Status line, and `git status -- <files>`. Update the draft for each change, or list it as a discrepancy.

## 4. Write a migration plan

Add a `## Migration` section, the first section of the notes tail (lifecycle/notes-tail.md). Number the steps; `ddd-implementation` does one step at a time and marks it `(done <date>)`, so a later session starts at the first step not marked done. Order the steps so that the code works after each one:

1. Tests that pin down current behaviour, before changing anything.
2. The behaviour changes the model requires, one command at a time, with any data migration they need.
3. Removal of what nothing reads any more.

If the code already matches the approved model, say that no migration is needed. Whether the plan also moves the code to another code style is `ddd-implementation`'s to say: read **Planning a migration** in its [MIGRATION.md](../ddd-implementation/MIGRATION.md) and add the steps it names.

When the code uses names the glossary lists under `_Avoid_`, add a rename step of its own, so renames never share a change with behaviour. Until it is done, those names stay in the existing code, and new code uses the glossary's names.

List the discrepancies from step 3 that were judged to be bugs, as separate items. Fixing behaviour and restructuring code are different changes and should not share a commit.

Stop here. Each migration step is implemented with `ddd-implementation`.
