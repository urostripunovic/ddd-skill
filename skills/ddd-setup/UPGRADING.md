# Upgrading from an earlier version of the kit

Read this when `install.sh` reports the earlier card layout, or the repository has cards or a glossary in a form listed here.

- A card that still has `## Go` and `## TypeScript` sections is from an earlier version of the kit: recommend the new layout. Its **Corrections** are kept in every case.
- Cards directly under `docs/ddd/cards/` (`01-domain-primitive.md`, `go/`, `ts/`) are from before the style directories; the script says so. With the user's agreement, move them into `docs/ddd/cards/functional/` with `git mv`, so their history and Corrections come along, and keep the kit's new top-level `docs/ddd/cards/README.md` beside them, copying the repository's **Wanted** rows into it. Then run the script again and handle what it lists as above.
- `docs/domain/glossary.md` is from an earlier version that wrote the glossary as a table: offer to move its terms into `CONTEXT.md` in the format `ddd-modelling` describes.
- `GLOSSARY.md` and `GLOSSARY-MAP.md` are the glossary's earlier names. With the user's agreement, rename them with `git mv` to `CONTEXT.md` and `CONTEXT-MAP.md`, and the per-context glossaries a map links to, updating its links. If a `CONTEXT.md` already exists, written by another skill, merge the terms into it and ask about each term the two define differently. The model's approval stands: its hash does not cover the glossary.
