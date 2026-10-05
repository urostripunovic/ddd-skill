# Context map

## Bounded contexts

| Context | Responsible for | Owns these aggregates | Not responsible for |
|---|---|---|---|
| Ordering | Taking, placing and cancelling orders | Order | Payment, delivery, prices |

## Relationships

| Upstream | Downstream | What crosses the boundary | Translation |
|---|---|---|---|
| Pricing service | Ordering | Unit price for a product | Anti-corruption layer in Ordering; arrives in the domain as a PriceQuote |
