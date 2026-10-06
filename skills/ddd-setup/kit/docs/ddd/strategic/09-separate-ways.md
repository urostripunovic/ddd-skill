# Separate ways

From Evans' Reference, "Separate Ways":

> We must be ruthless when it comes to defining requirements. If two sets of functionality have no significant relationship, they can be completely cut loose from each other.
>
> Integration is always expensive, and sometimes the benefit is small.
>
> Therefore:
>
> **Declare a bounded context to have no connection to the others at all, allowing developers to find simple, specialized solutions within this small scope.**

The DDD Crew describe the team relationship behind it as **free**: "A Bounded Context or a team that works in it is free if changes in other Bounded Contexts do not influence its success or failure."

## In this kit

This section is the kit's convention, not part of DDD.

One row in the Relationships table of `docs/domain/context-map.md` with both contexts, `separate ways` as the Pattern and `nothing` as What crosses the boundary, so the absence of a connection is recorded as a decision.

## Corrections

<!-- Add a dated line each time this pattern turned out not to describe the relationship, and what it became. -->
