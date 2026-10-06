# Is the kit in use?

The kit is adopted in a repository when `docs/domain/` exists. Without it, no ddd skill blocks or redirects work; each says in one line what it would have done.

A scope listed under `## Prototypes` in `docs/domain/context-map.md` (or in the agent instructions, when there is no map) is exempt: the user chose depth none for it, and unmodelled code in it is written without a model. The exemption holds while a draft model for that scope is being adopted, and ends at approval: the approval removes the row, or narrows it to the part still unmodelled. It never overrides an approved model.
