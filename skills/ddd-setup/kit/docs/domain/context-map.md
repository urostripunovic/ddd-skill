# Context map

## Bounded contexts

| Context | Responsible for | Owns these aggregates | Not responsible for |
|---|---|---|---|
| <!-- Ordering --> | <!-- Taking and changing orders --> | <!-- Order --> | <!-- Payment, delivery --> |

## Relationships

One row per dependency between contexts or to an external system.

| Upstream | Downstream | What crosses the boundary | Translation |
|---|---|---|---|
| <!-- Payment provider --> | <!-- Billing --> | <!-- Charge status --> | <!-- Anti-corruption layer in Billing --> |

## Open questions

<!-- Boundaries we are unsure about, and what would settle them. -->

## Prototypes

<!-- Only scopes where the user chose depth none. Modelling is postponed for unmodelled code
     in these scopes, not for the whole repository. When a draft model is created for part of a
     scope, remove the row, or narrow it to the part that is still unmodelled. -->

| Scope | Code paths (if known) | What the prototype is testing |
|---|---|---|
