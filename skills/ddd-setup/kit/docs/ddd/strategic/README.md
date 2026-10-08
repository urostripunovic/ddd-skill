# Strategic cards

How the parts of a domain relate: which part is the core, and how two bounded contexts, or a context and an outside system, work together. These cards are about teams and models, not code, so they are the same in every language and code style.

## Sources

Every statement about DDD in these cards is quoted from one of three sources. The cards add no rules of their own. Each card ends with an **In this kit** section, which is the kit's convention for where the answer is written down, and nothing more.

- Eric Evans, *Domain-Driven Design Reference: Definitions and Pattern Summaries* (Domain Language, 2015), <https://www.domainlanguage.com/ddd/reference/>, licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
- DDD Crew, *Context Mapping*, <https://github.com/ddd-crew/context-mapping>, licensed under [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- DDD Crew, *Bounded Context Canvas*, <https://github.com/ddd-crew/bounded-context-canvas>, licensed under [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

The quotations are excerpts; line breaks from the PDF were removed and nothing else was changed. Read the sources for the full text. Each quotation stays under its source's licence, as given above, and is not covered by the kit's MIT licence; the rest of each card is. The licences cover the quoted text only: code and models written with the kit are not affected. Keep this file with the cards when you copy them.

Never edit quoted text, not even to shorten or clarify it: a changed quotation no longer says what its source says. Only the **In this kit** and **Corrections** sections are edited.

## Team relationships

From Evans' Reference:

> **upstream-downstream**: A relationship between two groups in which the "upstream" group's actions affect project success of the "downstream" group, but the actions of the downstream do not significantly affect projects upstream. (e.g. If two cities are along the same river, the upstream city's pollution primarily affects the downstream city.) The upstream team may succeed independently of the fate of the downstream team.
>
> **mutually dependent**: A situation in which two software development projects in separate contexts must both be delivered in order for either to be considered a success.
>
> **free**: A software development context in which the direction, success or failure of development work in other contexts has little effect on delivery.

## Context map

From Evans' Reference:

> Identify each model in play on the project and define its bounded context. This includes the implicit models of non-object-oriented subsystems. Name each bounded context, and make the names part of the ubiquitous language.
>
> Describe the points of contact between the models, outlining explicit translation for any communication, highlighting any sharing, isolation mechanisms, and levels of influence.
>
> Map the existing terrain. Take up transformations later.

From the DDD Crew: "Prefer small context maps for explicit questions", "Document and explain the patterns you are going to use", and "Work with different perspectives and multiple context maps for those perspectives."

## The cards

The second column is the line that connects each pattern to the context map in the pattern-language overview of Evans' Reference, or, where the overview has none, the pattern's own opening line.

| Card | In Evans' words |
|---|---|
| [01 Core domain and subdomains](01-core-domain-and-subdomains.md) | "Boil the model down." |
| [02 Partnership](02-partnership.md) | "When teams in two contexts will succeed or fail together, a cooperative relationship often emerges." |
| [03 Shared kernel](03-shared-kernel.md) | overlap allied contexts through a shared kernel |
| [04 Customer/supplier](04-customer-supplier.md) | relate allied contexts as customer/supplier teams |
| [05 Conformist](05-conformist.md) | overlap unilaterally as conformist |
| [06 Anticorruption layer](06-anticorruption-layer.md) | translate and insulate unilaterally with an anticorruption layer |
| [07 Open-host service](07-open-host-service.md) | support multiple clients through an open host service |
| [08 Published language](08-published-language.md) | formalize as published language (from open host service) |
| [09 Separate ways](09-separate-ways.md) | free teams to go separate ways |
| [10 Big ball of mud](10-big-ball-of-mud.md) | segregate the conceptual messes |

## In this kit

This section is the kit's convention, not part of DDD.

- `docs/domain/context-map.md` has a **Kind** column for each context (card 01) and a **Pattern** column for each relationship (cards 02 to 09). A big ball of mud (card 10) is marked on the context itself.
- Each fact that crosses a boundary is also a row of **Facts from outside** in the context file, and each reaction across contexts a row of **Policies**.
- When the team learns that a recorded pattern does not describe the relationship, add a dated line under **Corrections** in the card.
