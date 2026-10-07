# Prototypes and migration steps

Read this from [SKILL.md](SKILL.md) when the scope is listed under `## Prototypes` ([adoption.md](../ddd-modelling/lifecycle/adoption.md)), or the task is a step under the context file's `## Migration`. The rest of SKILL.md still holds.

**A recorded prototype.** Inside a prototype scope (adoption.md), implement without requiring a model, in the project's chosen style and checks. While a draft model for the scope is being adopted, say in your summary that the draft must be checked against this change before approval.

**A step from the migration plan.** The task is a step under the context file's `## Migration` (the user names it, or a ticket points at it), and the model is approved. Do that step and nothing else, in the order the plan gives, instead of the per-command order below: a step that adds characterisation tests adds only tests, and a rename step only renames. When it is done, add `(done <date>)` to the end of the step, so the next session starts at the first step not marked done.
