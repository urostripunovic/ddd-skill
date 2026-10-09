# The glossary is shared

Read this from [SKILL.md](SKILL.md) before the first write to `GLOSSARY.md`.

Other skills read and write the same `GLOSSARY.md`, among them Matt Pocock's `domain-modeling` and `tdd` (from his 1.3; before it the file was `CONTEXT.md`), so its name and format are fixed. It holds the glossary and nothing else:

```md
# Ordering

Takes, places and cancels customer orders.

## Language

**Placed order**:
An order the customer has committed to. It has at least one item and a time of placing.
_Avoid_: Submitted order
```

- One or two sentences per term, written so a newcomer can tell it from its neighbours. Business words only: no record, entity, DTO, manager, handler or status.
- When several words exist for one concept, pick one and list the others under `_Avoid_`. The checks search for those words, so a rejected synonym that is not written down will come back.
- With one context, or several that share their words, there is one `GLOSSARY.md` at the root, with a `# <Context>` heading per context once there are two; an `_Avoid_` under one context's heading applies to that context only, so Billing can avoid a word that Payments uses. Split it into a `GLOSSARY.md` per context and a `GLOSSARY-MAP.md` at the root only when a word means different things in two contexts, or the user asks: `- [Ordering](./src/ordering/GLOSSARY.md): one line on what it is`. How the contexts relate is written only in `docs/domain/context-map.md`: the map's `## Relationships` section is the one line `See docs/domain/context-map.md.` If it holds relationships written by another skill, move each into `docs/domain/context-map.md`, ask about any the two files describe differently, and leave that line in their place.
- Create the file when the first term is settled, not before.
- A term is written the moment it is settled, with no separate approval step. Approval is recorded on context files, not on the glossary or context map. When a shared definition or relationship changes, identify the affected contexts and show the impact to the user. If it changes an approved rule's meaning, record that change in the context, set it to draft and get approval again. The checker catches some missing names, rejected synonyms, and terms that cross a boundary in the context map but are missing from a side's glossary; it cannot detect a change of meaning.
