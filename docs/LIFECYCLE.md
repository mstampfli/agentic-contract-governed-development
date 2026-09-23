# ACGD Delivery Lifecycle

A summary of the operating model. The normative text is [`skill/SKILL.md`](../skill/SKILL.md); agent rules live in
[`skill/templates/rules.md`](../skill/templates/rules.md).

```
                 ┌────────────────────────── Plan / Extend (add-ons, reopened coverage) ◄───────────┐
                 ▼                                                                                   │
  1. DISCOVER ──► 2. BUILD LOOP (per component) ──► 3. CHECKPOINT LOOPS ──► Done (current scope) ────┘
  counter-specs     writer → gates → fresh module     red team (classes)
  merge + review    review → seam reviews →           quality (bar, simplify)
  requirements      class fixes → until GREEN         both end by convergence
  acceptance tests
  quality bar
```

## Phase 1 — Discover
| Step | Output |
|---|---|
| Two blind counter-specifications (no orchestrator draft) + orchestrator draft | three independent specs |
| Project setup | ledgers, `STATUS.md`, `PROCESS.md`, `AGENTS.md` + `CLAUDE.md` symlink, test folders |
| Merge (all / some / one) | `INTERFACES.proposed.md`, reasons in the changelog |
| User requirements `REQ-n` | verbatim, visible to builders |
| Operational traces, reference systems | gap candidates |
| Acceptance tests, quality bar (with hard limits) | hidden tests, measurement scripts |
| Coverage matrix, scope map, spec-change review | `INTERFACES.md` V0 |

## Phase 2 — Build loop (per component, dependency-ordered, parallel where independent)
Writer → mechanical gates (tests, citations, `spec_check all`, scope) → fresh module review → fresh seam reviews →
class-level fixes → repeat until a **full round** finds the component **green**.

## Phase 3 — Checkpoint loops
- **Red team** on the smallest runnable composite, then every larger one; fresh red teamer per round; ends when no new
  defect class appears.
- **Quality** — every bar item met / below / not built yet, plus simplifications; ends by convergence; a miss is
  reported only within its hard limit, beyond it the loop escalates.

## Phase 4 — Plan / Extend
Add-ons re-enter Discover; decided coverage cells at touched seams are reopened and re-decided before merge.

## Controls that run continuously
| Control | Mechanism |
|---|---|
| Change governance | amendments with marks, derived impact, ACKs, tiered review |
| Decision governance | ledgers; every assumption dispositioned |
| Human in command | `Ask the user: yes\|no`; *Decisions open to steer*; overrides at the next step |
| Independent verification | fresh agents, orchestrator-run gates, never self-reports |
| Continuous improvement | every orchestrator mistake → root cause → process change |
