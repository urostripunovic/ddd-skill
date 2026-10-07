# Strict review

Read this from [SKILL.md](SKILL.md) at strict effective depth, or when the context file has no `Depth:` line. Everything in SKILL.md still holds.

## Lenses in sub-agents

At strict depth, if you can start sub-agents, give each lens its own. Its prompt holds only: the path of SKILL.md with the instruction to apply that one lens, the paths of the model files, the part under review, and a file path outside the repository to write its findings to. It returns one line: how many blockers, and the path. Pass nothing from this conversation. Read the three files when all are done. A sub-agent that returns its whole report fills this conversation with three reports before you have written one.

## 3. What the lenses do not cover

- **Language**: each term has one meaning per context, and no two terms mean the same thing.
- **Contexts**: each boundary is justified by a change in meaning, rules or ownership, not by a technical layer or a table. Each context says what it is not responsible for. Every dependency between contexts and to external systems is in the map, with what crosses and how it is translated. Each context has a Kind and each relationship a Pattern, and the row agrees with the card's definition in `docs/ddd/strategic/`: for example, a conformist row with a translation, or an anticorruption layer with none, contradicts its card. Do not judge whether the chosen pattern is wise; the cards quote their sources and give no rule for that.
- **States**: no field is "only set in some cases". No command lists "wrong state" as a failure; if one does, its source states are too wide.
- **Events**: past tense, and carrying what their consumers need and no more.
- **Invariants**: each is concrete enough to write a test for, and "enforced by the type" is actually visible in the state definition.
- **Aggregates**: a list inside an aggregate has an upper bound. An aggregate that every command in the context touches is probably too large; say which rule forces that.
- **Status**: a model derived from code is not marked approved.
