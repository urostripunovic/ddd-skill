---
name: ddd-system-design
description: "Check one flow of an approved domain model against the common system-design patterns (caching, read replicas, indexing, batching, sharding, async writes, real-time updates, queues, worker pools, workflow engines, retries, idempotency, circuit breakers, self-healing, CQRS), and record for each whether it applies, with the reason. Use after the model is approved, before cutting tickets."
disable-model-invocation: true
---

# System design check

Answer one question for one flow: which of the usual system-design patterns does it need, and why? Record every pattern as **applies**, **not needed** or **deferred**, with a reason, so the limits are written down and nobody has to guess later whether a pattern was forgotten or ruled out.

This is a technical pass. The model says what the business needs; this skill says how the system keeps up with it. It never changes the model.

## Before you start

1. If `docs/domain/` does not exist, this repository has not adopted the kit. Say so and stop.
2. Run `tools/check-model.sh` on the context file. If it fails, or the status is not approved, stop and say which. Patterns chosen for a model that may still change are chosen for guesses.
3. Note the commit the context file last changed in: `git log -1 --format=%h -- <file>`. The record carries it.
4. Ask which flow, or which steps of `## The flow`, to check, if the user did not say. One flow per run.

## Read what the model already answers

The model answers several of these questions in domain terms. Read them as input and do not ask them again:

| Model section | Already answers |
|---|---|
| `## Policies`, "safe to deliver twice" | idempotency of the commands a policy causes |
| `### Races` | who wins when two commands meet; what optimistic concurrency must deliver |
| `## Rules across aggregates`, "Immediate or eventual" | where async writes and queues are allowed, and what users see meanwhile |
| `### Facts from outside`, "If not, or no answer" and "May it be stale?" | what retries and circuit breakers must end in, and how long a cache may hold a fact |
| `## Amendments` | the rows above as amended |

Also read the project as it is: what storage, broker and runtime it already has. Ask the user for what the code cannot tell you. Do not propose new infrastructure where the existing one does the job.

## The patterns

Go through the flow step by step. For each step, take only the patterns whose signal is there. A pattern without a signal is **not needed**, with "no signal" as the reason, and is not asked about.

| Need | Pattern | Signal in the model or the project |
|---|---|---|
| Scale reads | caching | a fact or read that is asked for far more often than it changes; "May it be stale?" says yes |
| | read replicas | read load that the primary store cannot carry, and reads that may lag writes |
| | indexing | a lookup by something other than the aggregate's id |
| Scale writes | batching | many small writes of the same kind close together, where none needs its own answer at once |
| | sharding | one store cannot hold the data or the write rate; a key that splits it without a rule across the parts |
| | async writes | a write whose result the caller does not wait for; the rule it touches is "eventual" |
| Real-time | WebSockets | both sides send while a session is open |
| | server-sent events | the server pushes progress or changes to a caller who only watches |
| | long-polling | pushes are rare, or the caller's network cannot hold a stream open |
| Long-running work | message queue | a policy across processes; a step that outlives the request that started it |
| | worker pool | slow or uneven jobs that must not starve each other; an outside source with a rate limit |
| | workflow engine | several steps with waits, timeouts or compensation that must survive restarts |
| Reliability | retries with backoff | a fact from outside or a delivery that can fail for a moment |
| | idempotency | anything retried, redelivered or double-clicked |
| | circuit breaker | an outside source that can be down for longer than a request can wait |
| | self-healing | a desired state the system should return to on its own: stuck jobs, orphaned resources, drift |
| Separate reads and writes | CQRS | a read side with a different shape or load from the aggregate; a read model card or "Read model" in the glossary |

Some patterns only work together. When one applies, check its partner:

- retries, queues and redelivery need **idempotency**, and the model must say what makes a command the same one
- async writes and queues need the rule they touch to be **eventual** in the model
- caching and read replicas need **"May it be stale?"** or the read model to allow the lag
- a worker pool needs a bound, and an answer to **what happens when it is full**: wait, reject or shed
- self-healing needs a **desired state** and something that notices drift: a lease, a heartbeat, a reconcile loop
- a circuit breaker needs the fact's **"If not, or no answer"** to say what the caller gets while it is open

## Ask

Ask in rounds, one step of the flow per round, at most three questions per round, each with a proposed answer. With Matt Pocock's `grilling` installed, use its format.

Ask for the numbers a verdict depends on: requests per second, data size, how long a job runs, how stale is acceptable in seconds. Do not invent them. If nobody knows, the verdict is **deferred**, and the reason names the number that would decide it.

An answer that changes what the business sees is a model question, not a technical one: how stale a price a customer may see, what happens to an order while a retry is pending, who compensates when step three fails. Mark the row **blocked by the model**, keep going with the rest, and at the end offer `ddd-modelling` with the questions. Do not answer them yourself and do not write to the context file.

## Record

Write `docs/system-design/<context>.md`. If it exists, update the rows of this flow and leave the others.

```
# System design: <context>

Model: docs/domain/contexts/<context>.md, at commit <commit>

## <Flow or steps checked>

| Step | Pattern | Verdict | Why | How |
|---|---|---|---|---|
| 2. AddItem | caching | applies | prices are read on every add and change hourly; the model allows 5 minutes stale | in-process cache keyed by SKU, 5 minute expiry |
| 2. AddItem | circuit breaker | applies | Pricing can be down for minutes; model: PricingUnavailable | open after 5 failures in 30 s, half-open after 30 s |
| 3. PlaceOrder | async writes | not needed | the customer waits for the placed order; the rule is immediate | |
| 3. PlaceOrder | sharding | deferred | needs the expected orders per day | |
| 4. ReserveStock | message queue | blocked by the model | what does the customer see while stock is unconfirmed? | |

## Not checked

<patterns or steps left out, and why>
```

**Why** points at the model's row or the number that decided it. **How** names the mechanism in one line: a library, a setting, an existing component. Leave it empty for anything but **applies**.

If the project keeps ADRs in `docs/adr/`, write one for each **applies** row whose mechanism was a real choice between options, and link it from **How**.

## Hand off

Rows that **apply** are work around the domain, not domain behaviour. `ddd-to-tickets` lists them as out of scope; they become tickets with Matt Pocock's `to-tickets`, or by hand, each blocked by the command ticket of its step. Show the user the record and the list of **blocked by the model** questions. Do not cut tickets here.

When the model is approved again, run this again on the change (`git diff <commit> -- <context file>`), update only the rows whose steps changed, and give the record the new commit. Amendments rows alone do not call for a new run; `ddd-next` and `tools/ddd-status.sh` only flag a record once the model has been approved again since its commit.

## Do not

- Change the model, its notes tail or the glossary.
- Add a pattern without a signal, or because it is common. "Not needed" is a good answer.
- Invent load, size or latency numbers.
- Put infrastructure into domain code or domain tickets.
- Check more than one flow per run.
