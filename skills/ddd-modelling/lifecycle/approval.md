# Status and approval

Depth, the core and strict scope are defined in [depth.md](depth.md).

The `Status:` line is written by `tools/stamp-model.sh`, never by hand:

| Status | Means |
|---|---|
| `draft` | being modelled, or edited since approval |
| `derived from code, not confirmed, read at <commit>` | adopted from code; the user has not confirmed it |
| `approved by <name> on <date>` | the user approved this exact text |

Any of them may end with `, reviewed <date>`, once a model review has no blockers left (`tools/stamp-model.sh review <file>`). The hashes that tie the approval and the review to this exact text go in a comment at the end of the line, `<!-- model-hash <hash>, reviewed at <hash> -->`; a review of another hash is out of date. A line in the older form, with the hashes in the text, means the same.

- **Only the user approves.** Ask for the word "approve"; "go ahead" or "allow everything" is not approval. The approver's name comes from the user: from the `Approvers:` line under `## Domain code` in the agent instructions when it holds one name; otherwise ask which listed name is approving, or, with no list, for the name, unless the message gives it. Never take it from git config, an account, an email or any other source. The `Approvers:` line is the user's: change it only when the user asks for that change in their own words, never to make an approval go through. `tools/stamp-model.sh` refuses a name that is not on it. Then run `tools/stamp-model.sh approve <file> "<name>"`, which refuses while the model fails its check. At standard depth, approval means the user confirmed the core and saw the list of assumptions; say so when asking. When asking, show the reply to type: `I approve <file>.`, adding `Approver: <name>` when there is no list or it holds several names.
- **Review before approval.** Strict, or a context with strict commands: a review in a fresh session (`ddd-model-review`) of the strict context, or of the strict scopes. Standard: optional; one round is enough unless it finds a blocker in the core. After a reviewed model changes inside a strict scope, only the changed rows are reviewed again.
- **An edit to the approved core**, or to anything at strict effective depth, sets the status back with `tools/stamp-model.sh draft <file>`, and the user approves again.
- **A change to the rest at standard effective depth** is not an edit: it is an `## Amendments` row ([notes-tail.md](notes-tail.md)), and the approval stands. Amendments are folded into the model, and approved again, together and when the user chooses.
- **The hash** covers the context file except its Status line and its notes tail ([notes-tail.md](notes-tail.md)). It does not cover the glossary or the context map: when a change there alters what an approved rule means, show the affected contexts, set them to draft and ask for approval again. No tool can detect a change of meaning.
