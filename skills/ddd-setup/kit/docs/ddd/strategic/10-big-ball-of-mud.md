# Big ball of mud

From Evans' Reference, "Big Ball of Mud" (a term introduced after the 2004 book):

> As we survey existing software systems, trying to understand how distinct models are being applied within defined boundaries, we find parts of systems, often large ones, where models are mixed and boundaries are inconsistent.
>
> It is easy to get bogged down in an attempt to describe the context boundaries of models in systems where there simply are no boundaries.
>
> Well-defined context boundaries only emerge as a result of intellectual choices and social forces (even though the people creating the systems may not always have been consciously aware of these causes at the time). When these factors are absent, or disappear, multiple conceptual systems and mix together, making definitions and rules ambiguous or contradictory. The systems are made to work by contingent logic as features are added. Dependencies crisscross the software. Cause and effect become more and more difficult to trace. Eventually the software congeals into a big ball of mud.
>
> The big ball of mud is actually quite practical for some situations (as described in the original article by Foote and Yoder), but it almost completely prevents the subtlety and precision needed for useful models.
>
> Therefore:
>
> **Draw a boundary around the entire mess and designate it a big ball of mud. Do not try to apply sophisticated modeling within this context. Be alert to the tendency for such systems to sprawl into other contexts.**
>
> (see http://www.laputan.org/mud/mud.html. Brian Foote and Joseph Yoder)

From the DDD Crew: "Big Ball Of Mud is a demarcation of a bad model or system quality. You want to make sure, that this mess does not propagate into other bounded contexts." Evans, under [anticorruption layer](06-anti-corruption-layer.md): "The models of legacy systems are usually weak (if not big balls of mud)".

## In this kit

This section is the kit's convention, not part of DDD.

One row in the Bounded contexts table of `docs/domain/context-map.md` for the whole system, with `(big ball of mud)` after its name.

## Corrections

<!-- Add a dated line each time this designation turned out to be wrong, and what it became. -->
