# Context: <name>

Status: light
<!-- A light context has no approval. Moving it to standard sets "Status: draft" and is approved like a new core. -->

Depth: light
<!-- Light while being wrong is cheap. Move to standard (or strict for the part that needs it) when a request touches money,
     credentials, authorisation, personal data or anything hard to undo, another context reacts to its facts, it gains a
     second lifecycle, it outgrows about a dozen rows, or the user asks. -->

## Requests

<!-- Every request the rules answer, and who or what may make it. "Issued by" is never assumed: ask. -->

| Request | Issued by | Notes |
|---|---|---|
| <!-- TunnelEntered --> | <!-- the simulation, in the same process --> | |

## Examples

<!-- One row per rule: the state, the request, the facts the rules decide, and the test that pins it, named
     "example <n>". Row numbers are permanent: a new row takes the next unused number, a removed row leaves a gap.
     Write "none" in Request for a starting state, and "none" in Facts for a request that is already answered. -->

| # | State | Request | Facts | Test |
|---|---|---|---|---|
| <!-- 1 --> | <!-- Fighting, not the last arena --> | <!-- BossCleared --> | <!-- ArenaCleared --> | <!-- run.test.ts: example 1 --> |
| <!-- 2 --> | <!-- Fighting --> | <!-- TunnelEntered --> | <!-- TunnelRefused(NotCleared) --> | <!-- run.test.ts: example 2 --> |

## Open questions

<!-- Questions a change raised and the user has not answered yet. "None." when there are none. -->
