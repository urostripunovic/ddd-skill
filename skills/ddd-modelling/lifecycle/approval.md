# Status and approval

Depth, the core and strict scope are defined in [depth.md](depth.md).

The `Status:` line says where a model stands. You write it, by editing the line:

| Status | Means |
|---|---|
| `draft` | being modelled, or its core changed since approval |
| `derived from code, not confirmed, read at <commit>` | adopted from code; the user has not confirmed it |
| `approved <date>` | the user approved the model |

`draft` and `approved <date>` may end with `, reviewed <date>`, once a model review has no blockers left.

- **Only the user approves.** Run `tools/check-model.sh` first, and do not ask while it fails. Then show the model's flow and ask whether they approve it. Any clear yes about the model is approval: "I approve", "approved", "yes, that is right". Permission to act ("go ahead", "allow everything") says nothing about the model: ask once. On a yes, write `Status: approved <today>`, keeping a `, reviewed <date>` that is there, say so in one line, and carry on with what the user asked for. Never write it without that yes. At standard depth, approval means the user confirmed the core and saw the list of assumptions; say so when asking.
- **Review before approval.** Strict, or a context with strict commands: a review in a fresh session (`ddd-model-review`) of the strict context, or of the strict scopes, recorded as `, reviewed <date>` before you ask. Standard: optional; one round is enough unless it finds a blocker in the core.
- **An edit to the approved core**, or to anything at strict effective depth, sets the status back to `draft`: show the change as a diff and ask again. At strict effective depth it also removes `, reviewed <date>`, until the changed rows are reviewed.
- **A change to the rest at standard effective depth** is not an edit: it is an `## Amendments` row ([notes-tail.md](notes-tail.md)), and the approval stands. Amendments are folded into the model, and approved again, together and when the user chooses.
- **The glossary and the context map** have no status of their own. When a change there alters what an approved rule means, show the affected contexts, set them to draft and ask for approval again. No tool can detect a change of meaning.
- **What changed since approval, and who approved,** is in git (`git log -p <file>`), not in the file. `tools/check-model.sh` cannot tell that a model changed after it was approved.
- **A line the earlier stamping tool wrote** (`approved by <name> on <date>`, with hashes in a comment) still reads as approved. Leave it until the next approval, which writes the short form.
