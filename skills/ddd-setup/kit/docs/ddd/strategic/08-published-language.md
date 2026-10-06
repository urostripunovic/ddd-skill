# Published language

From Evans' Reference, "Published Language":

> *The translation between the models of two bounded contexts requires a common language.*
>
> Direct translation to and from the existing domain models may not be a good solution. Those models may be overly complex or poorly factored. They are probably undocumented. If one is used as a data interchange language, it essentially becomes frozen and cannot respond to new development needs.
>
> Therefore:
>
> **Use a well-documented shared language that can express the necessary domain information as a common medium of communication, translating as necessary into and out of that language.**
>
> Many industries establish published languages in the form of data interchange standards. Project teams also develop their own for use within their organization.
>
> Published language is often combined with open-host service.

From the DDD Crew: "Widely known examples of a Published Language are iCalendar or vCard."

## In this kit

This section is the kit's convention, not part of DDD.

`published language` in the Pattern of the relationship in `docs/domain/context-map.md`, with the language's name in What crosses the boundary. With an [open-host service](07-open-host-service.md), both names go in the Pattern: `open host service, published language`.

## Corrections

<!-- Add a dated line each time this pattern turned out not to describe the relationship, and what it became. -->
