# Customer/supplier development

From Evans' Reference, "Customer/Supplier Development":

> *When two teams are in an upstream-downstream relationship, where the upstream team may succeed independently of the fate of the downstream team, the needs of the downstream come to be addressed in a variety of ways with a wide range of consequences.*
>
> A downstream team can be helpless, at the mercy of upstream priorities. Meanwhile, the upstream team may be inhibited, worried about breaking downstream systems. The problems of the downstream team are not improved by cumbersome change request procedures with complex approval processes. And the freewheeling development of the upstream team will stop if the downstream team has veto power over changes.
>
> Therefore:
>
> **Establish a clear customer/supplier relationship between the two teams, meaning downstream priorities factor into upstream planning. Negotiate and budget tasks for downstream requirements so that everyone understands the commitment and schedule.**
>
> Agile teams can make the downstream team play the customer role to the upstream team, in planning sessions. Jointly developed automated acceptance tests can validate the expected interface from the upstream. Adding these tests to the upstream team's test suite, to be run as part of its continuous integration, will free the upstream team to make changes without fear of side effects downstream.

## In this kit

This section is the kit's convention, not part of DDD.

One row in the Relationships table of `docs/domain/context-map.md`, with the upstream and downstream and `customer/supplier` as the Pattern.

## Corrections

<!-- Add a dated line each time this pattern turned out not to describe the relationship, and what it became. -->
