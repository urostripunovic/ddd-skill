# Open-host service

From Evans' Reference, "Open-host Service":

> *Typically for each bounded context, you will define a translation layer for each component with which you have to integrate that is outside the context. Where integration is one-off, this approach of inserting a translation layer for each external system avoids corruption of the models with a minimum of cost. But when you find your subsystem in high demand, you may need a more flexible approach.*
>
> When a subsystem has to be integrated with many others, customizing a translator for each can bog down the team. There is more and more to maintain, and more and more to worry about when changes are made.
>
> Therefore:
>
> **Define a protocol that gives access to your subsystem as a set of services. Open the protocol so that all who need to integrate with you can use it. Enhance and expand the protocol to handle new integration requirements, except when a single team has idiosyncratic needs. Then, use a one-off translator to augment the protocol for that special case so that the shared protocol can stay simple and coherent.**
>
> This places the provider of the service in the upstream position. Each client is downstream, and typically some of them will be conformist and some will build anticorruption layers. A context with an open host service might have any sort of relationship to contexts other than its clients.

From the DDD Crew: "The teams on the downstream are free to be conformists or to build anticorruption layers." Evans adds, under [published language](08-published-language.md): "Published language is often combined with open-host service."

## In this kit

This section is the kit's convention, not part of DDD.

One row per client in the Relationships table of `docs/domain/context-map.md`, with `open host service` in the Pattern, followed by the client's own pattern when it has one: `open host service, conformist` or `open host service, anti-corruption layer`.

## Corrections

<!-- Add a dated line each time this pattern turned out not to describe the relationship, and what it became. -->
