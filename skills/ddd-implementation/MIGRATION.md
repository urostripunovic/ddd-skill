# Prototypes and migration steps

Read this from [SKILL.md](SKILL.md) when the scope is listed under `## Prototypes` ([adoption.md](../ddd-modelling/lifecycle/adoption.md)), or the task is a step under the context file's `## Migration`. The rest of SKILL.md still holds.

**Planning a migration.** `ddd-modelling` reads this while it writes the plan. In the repository's own code style (see **Code style** in SKILL.md), the plan keeps the existing representations: add no step that introduces domain primitives, state types or pure decision functions merely to match the kit's examples. With the cards, the plan moves the code to them, and its middle steps are, in this order: domain primitives, introduced at the boundary first so the existing code keeps receiving what it expects; state types, with a translation to and from the existing representation at the repository; decision functions, one command at a time, replacing the old logic; removal of the old representation once nothing reads it.

**A recorded prototype.** Inside a prototype scope (adoption.md), implement without requiring a model, in the project's chosen style and checks. While a draft model for the scope is being adopted, say in your summary that the draft must be checked against this change before approval.

**A step from the migration plan.** The task is a step under the context file's `## Migration` (the user names it, or a ticket points at it), and the model is approved. Do that step and nothing else, in the order the plan gives, instead of the per-command order below: a step that adds characterisation tests adds only tests, and a rename step only renames. When it is done, add `(done <date>)` to the end of the step, so the next session starts at the first step not marked done.
