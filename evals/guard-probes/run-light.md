# Context: Run

Status: light
Depth: light

## Requests

| Request | Issued by | Notes |
|---|---|---|
| BossCleared | the simulation, in the same process | |
| TunnelEntered | the simulation, in the same process | |

## Examples

| # | State | Request | Facts | Test |
|---|---|---|---|---|
| 1 | Fighting, not the last arena | BossCleared | ArenaCleared | |
| 2 | Fighting | TunnelEntered | TunnelRefused(NotCleared) | |
| 3 | Cleared, not the last arena | TunnelEntered | ArenaEntered(next arena) | |

## Open questions

None.
