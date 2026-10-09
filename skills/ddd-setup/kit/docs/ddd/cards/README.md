# Pattern cards

How domain code is written: one directory per style. A card has the rule, what enforces it, an anti-pattern, and the corrections this team has recorded. The examples are in one directory per language inside the style.

| Style | For |
|---|---|
| [functional/](functional/README.md) | Wlaschin-style typed DDD: a type per state, pure decision functions, errors as values. Examples in Go and TypeScript |

Read the style's README, then only the cards the task needs, and the examples only for the language being written. A style's `REVIEW.md` is its checklist for code reviews: `ddd-implementation` is the only skill that writes code from the cards, and the reviews are style-neutral apart from that file. The cards for how contexts relate to each other are not about code and do not depend on the style: they are in [`docs/ddd/strategic/`](../strategic/README.md).

## Maintaining the cards

- When an agent gets a pattern wrong, add a dated line under **Corrections** in that card. This is where the cards gain most of their value.
- Replace the generic examples with approved code from your own projects over time.
- After editing an example, run `tools/check-cards.sh` so the cards never teach code that does not compile.

## When no card fits

A card is added when a project has needed the pattern, not before. A card written ahead of a real case teaches a guess.

1. The agent says that no card covers the pattern, names it, and adds a row under **Wanted** below.
2. It implements the code from the rules in the `ddd-implementation` skill, and the reviews run as usual.
3. Once that code is reviewed and merged, it becomes the card: copy an existing card's headings, put the merged code in the language directory as the example, and run `tools/check-cards.sh`. The check fails while an installed language has no example for a card.
4. Remove the row from **Wanted**.

### Wanted

| Pattern | First needed in | Date |
|---|---|---|
| <!-- Saga with compensation --> | <!-- billing/refund.go --> | <!-- 2026-01-15 --> |
| Property test over command sequences (asked for by `ddd-implementation`) | the first aggregate implemented with the kit | 2026-10-03 |

## Adding a language

A language is a directory inside a style: a `README.md` with the same three headings as the existing ones (idioms, checks, never), and one example per card. Add its extraction and its compile and lint commands to `tools/extract_cards.py` and `tools/check-cards.sh`, and a reference lint config to `tools/lint/`. The cards do not change. `ddd-setup` needs a line for detecting the language and merging its lint config.

## Adding a style

A style is a directory here with its own `README.md`, its own cards and its own language directories, for example an object-oriented style in the manner of Evans and Vernon, with entity classes, for a language built for it. The model in `docs/domain/` stays the same: it describes behaviour, not code. Add the style to the table above, to `install.sh` and to the choice in `ddd-setup`.
