# Conformist

From Evans' Reference, "Conformist":

> When two development teams have an upstream/down-stream relationship in which the upstream has no motivation to provide for the downstream team's needs, the downstream team is helpless. Altruism may motivate upstream developers to make promises, but they are unlikely to be fulfilled. Belief in those good intentions leads the downstream team to make plans based on features that will never be available. The downstream project will be delayed until the team ultimately learns to live with what it is given. An interface tailored to the needs of the downstream team is not in the cards.
>
> Therefore:
>
> **Eliminate the complexity of translation between bounded contexts by slavishly adhering to the model of the upstream team. Although this cramps the style of the downstream designers and probably does not yield the ideal model for the application, choosing conformity enormously simplifies integration. Also, you will share a ubiquitous language with your upstream team. The upstream is in the driver's seat, so it is good to make communication easy for them. Altruism may be sufficient to get them to share information with you.**

The alternative Evans names, when conforming is impractical, is the [anticorruption layer](06-anti-corruption-layer.md): "even the exception that is clearly designed may not fit the needs of the current project, making it impractical to conform to the upstream model."

## In this kit

This section is the kit's convention, not part of DDD.

One row in the Relationships table of `docs/domain/context-map.md`, with `conformist` as the Pattern and `none` as the Translation. The upstream's terms go into the downstream context's glossary as they are.

## Corrections

<!-- Add a dated line each time this pattern turned out not to describe the relationship, and what it became. -->
