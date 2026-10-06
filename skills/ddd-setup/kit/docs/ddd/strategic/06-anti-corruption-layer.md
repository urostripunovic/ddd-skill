# Anticorruption layer

From Evans' Reference, "Anticorruption Layer":

> *Translation layers can be simple, even elegant, when bridging well-designed bounded contexts with cooperative teams. But when control or communication is not adequate to pull off a shared kernel, partner or customer/supplier relationship, translation becomes more complex. The translation layer takes on a more defensive tone.*
>
> A large interface with an upstream system can eventually overwhelm the intent of the downstream model altogether, causing it to be modified to resemble the other system's model in an ad hoc fashion. The models of legacy systems are usually weak (if not big balls of mud), and even the exception that is clearly designed may not fit the needs of the current project, making it impractical to conform to the upstream model. Yet the integration may be very valuable or even required for the downstream project.
>
> Therefore:
>
> **As a downstream client, create an isolating layer to provide your system with functionality of the upstream system in terms of your own domain model. This layer talks to the other system through its existing interface, requiring little or no modification to the other system. Internally, the layer translates in one or both directions as necessary between the two models.**

## In this kit

This section is the kit's convention, not part of DDD.

- One row in the Relationships table of `docs/domain/context-map.md`, with `anti-corruption layer` as the Pattern. Translation names where the layer lives and what comes out of it, such as "in Ordering; arrives in the domain as a PriceQuote".
- With the functional cards installed, the code for the layer follows [09 Anti-corruption layer](../cards/functional/09-anti-corruption-layer.md) and [07 Parse at the boundary](../cards/functional/07-parse-at-the-boundary.md). Those are the kit's code style, not part of this pattern.

## Corrections

<!-- Add a dated line each time this pattern turned out not to describe the relationship, and what it became. -->
