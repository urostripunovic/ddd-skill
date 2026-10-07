# Context map

## Bounded contexts

Kind answers "How important is this context to the success of your organisation?" with `core`, `supporting` or `generic`, as the DDD Crew's Bounded Context Canvas defines them. See `docs/ddd/strategic/01-core-domain-and-subdomains.md`.

| Context | Kind | Responsible for | Owns these aggregates | Not responsible for |
|---|---|---|---|---|
| <!-- Ordering --> | <!-- core --> | <!-- Taking and changing orders --> | <!-- Order --> | <!-- Payment, delivery --> |

## Relationships

One row per dependency between contexts or to an external system. Upstream is the side whose actions affect the other's success, but not the other way round (Evans). Pattern is one or more of the strategic cards in `docs/ddd/strategic/`: partnership, shared kernel, customer/supplier, conformist, anticorruption layer, open host service, published language, separate ways. Mark a big ball of mud in the table above, after the context's name.

| Upstream | Downstream | Pattern | What crosses the boundary | Translation |
|---|---|---|---|---|
| <!-- Payment provider --> | <!-- Billing --> | <!-- anticorruption layer --> | <!-- Charge status --> | <!-- in Billing; arrives in the domain as a ChargeOutcome --> |

## Open questions

<!-- Boundaries we are unsure about, and what would settle them. -->

## Prototypes

<!-- Only scopes where the user chose depth none. Modelling is postponed for unmodelled code
     in these scopes, not for the whole repository. A row stays while a draft model for its scope is
     being adopted; when that model is approved, remove the row, or narrow it to the part that is
     still unmodelled. -->

| Scope | Code paths (if known) | What the prototype is testing |
|---|---|---|
