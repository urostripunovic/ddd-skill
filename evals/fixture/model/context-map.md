# Context map

## Bounded contexts

| Context | Kind | Responsible for | Owns these aggregates | Not responsible for |
|---|---|---|---|---|
| Ordering | core | Taking, placing and cancelling orders | Order | Payment, delivery, prices |

## Relationships

| Upstream | Downstream | Pattern | What crosses the boundary | Translation |
|---|---|---|---|---|
| Pricing service | Ordering | anticorruption layer | Unit price for a product | in Ordering; arrives in the domain as a PriceQuote |
