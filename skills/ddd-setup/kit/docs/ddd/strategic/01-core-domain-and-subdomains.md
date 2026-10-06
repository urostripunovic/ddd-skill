# Core domain and subdomains

## Core domain

From Evans' Reference, "Core Domain":

> In a large system, there are so many contributing components, all complicated and all absolutely necessary to success, that the essence of the domain model, the real business asset, can be obscured and neglected.
>
> It is harsh reality that not all parts of the design are going to be equally refined. Priorities must be set. To make the domain model an asset, the critical core of that model has to be sleek and fully leveraged to create application functionality. But scarce, highly skilled developers tend to gravitate to technical infrastructure or neatly definable domain problems that can be understood without specialized domain knowledge.
>
> Therefore:
>
> **Boil the model down. Define a core domain and provide a means of easily distinguishing it from the mass of supporting model and code. Bring the most valuable and specialized concepts into sharp relief. Make the core small.**
>
> **Apply top talent to the core domain, and recruit accordingly. Spend the effort in the core to find a deep model and develop a supple design—sufficient to fulfill the vision of the system.**
>
> Justify investment in any other part by how it supports the distilled core.

## Generic subdomains

From Evans' Reference, "Generic Subdomains":

> Some parts of the model add complexity without capturing or communicating specialized knowledge. Anything extraneous makes the core domain harder to discern and understand. The model clogs up with general principles everyone knows or details that belong to specialties which are not your primary focus but play a supporting role. Yet, however generic, these other elements are essential to the functioning of the system and the full expression of the model.
>
> Therefore:
>
> **Identify cohesive subdomains that are not the motivation for your project. Factor out generic models of these subdomains and place them in separate modules. Leave no trace of your specialties in them.**
>
> **Once they have been separated, give their continuing development lower priority than the core domain, and avoid assigning your core developers to the tasks (because they will gain little domain knowledge from them). Also consider off-the-shelf solutions or published models for these generic subdomains.**

## Strategic classification

From the DDD Crew's Bounded Context Canvas, which asks of each context: "How important is this context to the success of your organisation?"

> - core domain: a key strategic initiative
> - supporting domain: necessary but not a differentiator
> - generic: a common capability found in many domains

## In this kit

This section is the kit's convention, not part of DDD.

The **Kind** column of the Bounded contexts table in `docs/domain/context-map.md` holds `core`, `supporting` or `generic`, as the user answers the canvas's question.

## Corrections

<!-- Add a dated line each time a recorded kind turned out to be wrong, and what it became. -->
