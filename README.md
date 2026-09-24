# Agentic Contract-Governed Development (ACGD)

**Contract-governed delivery for teams of AI coding agents**

> **Status:** the latest additions (the user switch, quality loop, work directory, prompt checks, brownfield start and solo (Mode 2) steps, judged-item stances) are
> validated in simulations only, not yet in a real multi-agent build.

> *Align every contributor — human or AI agent — to a single source of truth, verify every boundary independently,
> and converge on a defect-free, cross-module-consistent system without human bottlenecks.*

ACGD is an operating model and toolchain for building multi-module software with parallel AI coding agents, or with a
single agent working alone — on a new project or an existing codebase. It ships as a [Claude Code](https://claude.com/claude-code) skill: a governance
playbook, role-scoped agent briefs, specification templates, and mechanical compliance gates.

---

## The problem statement

Telling an agent "be consistent" does not work. The instruction is understood — and still not followed.
Cross-module defects are **structural**, so ACGD remediates them structurally:

| Root cause (observed in controlled trials) | ACGD control |
|---|---|
| Contracts pin signatures, not data, state or failure behaviour | **Interface Registry** — formats, state, calls, failure contracts; one accountable owner per entry |
| Consumers are built before producers and invent them | **Dependency-ordered delivery**; consumers read and cite the real implementation |
| Gaps are filled with plausible guesses | **Decision Ledgers** (questions / assumptions), every assumption formally dispositioned |
| The specification covers only what its author anticipated | **Discovery Pipeline** — blind counter-specifications, operational traces, reference-system benchmarking, adversarial red-teaming |
| Builders optimise for the grader; orchestrators trust self-reports | **Independent Verification** — fresh reviewers every round; the orchestrator executes every check itself |
| Defects are fixed one instance at a time | **Class-Level Remediation** with permanent regression class tests |
| Reviews only add code; "correct" is mistaken for "good" | **Quality Bar** — measured continuously, judged at every checkpoint, with a simplification pass |

## Capability overview

- **Living Interface Specification** (`INTERFACES.md`) — failure model first; registries `FMT` / `EFF` / `CALL` / `HLP`
  / `REQ`; failure contracts (`R4`); a concern × seam **coverage matrix** that answers *"what is not covered yet?"*
- **Amendment Governance** — versioned amendments with in-place marks, impact derivation, acknowledgement tracking,
  tiered review (bookkeeping vs. semantic), consolidation instead of layering.
- **Role-Based Agent Operating Model** — orchestrator, writer / fixer, fresh builder, reviewer (spec-change, module,
  seam, quality), red teamer, counter-specifier, researcher. Each agent receives exactly its role's rules; one
  canonical rules source, verbatim copies, machine-verified.
- **Checkpoint Loops per Component** — no global phase gate: a component is *green* when a full round of fresh reviews
  passes; red-team and quality loops run at every green checkpoint and end by convergence, never by a round cap.
- **Human-in-Command, Never Required** — a single `Ask the user: yes|no` switch. `no`: the loop decides, logs every
  ask-point decision under *Decisions open to steer*, and never waits. The user's instruction always overrides, effective at the
  next step.
- **Compliance Gates** — `spec_check.py` (marks, ledger dispositions, acknowledgements, open questions, rule-copy
  integrity, prompt completeness, coverage) and `verify_citations.py` (every `Cite:` points at real code), backed by
  a regression suite.
- **Two modes, two starts** — several writers in parallel (Mode 1) or one solo writer (Mode 2), each on a new
  project or an existing codebase (brownfield start: register what the code does today, review only what the work
  touches or calls directly, plus not-yet-conforming code they depend on, unless told otherwise). Every gate runs in both; reviewers stay fresh agents. Includes sessions that start
  with no role assignment.

See [`docs/LIFECYCLE.md`](docs/LIFECYCLE.md) for the delivery lifecycle and [`skill/SKILL.md`](skill/SKILL.md) for the
normative playbook.

## Evidence

Measured in A/B trials (same task, same model; arm A = plain multi-agent build, arm B = ACGD), with acceptance tests
written before any code and hidden from builders, and blind audits of anonymised copies:

| Metric | Plain build | ACGD |
|---|---|---|
| Hidden acceptance tests (message-queue trial, 6 writers) | 15 / 17 | **17 / 17** |
| Cross-module breaks found by blind audit | several (nested size limits, unknown outcomes reported as failures, stuck reopen) | **none of those** |
| High-severity duplication / inconsistency findings (two independent blind audits) | 6 and 5 | **3 and 2** |
| Format / ownership disagreements (key-value trial) | ~7 | **~2** |
| Throughput vs. plain build | baseline | comparable |
| Token cost | baseline | **much higher** |

**Limitations, stated plainly:** two trials, one run per arm — indicative, not proven. ACGD only prevents drift in
what it registers (an unregistered convention still drifted). Defects inside a single module need the red team and
tests. The cost is substantial; tiers, batching and "question scope" exist to contain it.

## Repository layout

```
skill/
  SKILL.md                    normative playbook (the Claude Code skill)
  concerns.md                 cross-module concern catalogue (coverage matrix rows)
  spec_check.py               compliance gates
  verify_citations.py         citation integrity gate
  templates/
    rules.md                  single canonical rules source (role sections)
    INTERFACES.template.md    living specification skeleton
    AGENTS.md.template        project agent instructions (CLAUDE.md → symlink)
    writer_brief.md  review_brief.md  redteam_brief.md  counterspec_brief.md  researcher_brief.md
  tests/test_scripts.py       regression suite for the gates
tools/gen_templates.py        regenerates every rules copy from templates/rules.md
docs/LIFECYCLE.md             delivery lifecycle overview
```

## Installation

```bash
git clone https://github.com/mstampfli/agentic-contract-governed-development acgd
mkdir -p ~/.claude/skills
cp -r acgd/skill ~/.claude/skills/acgd
```

Then ask Claude Code for a multi-module build (or invoke `/acgd`). Requirements: Python 3.10+ for the
gates, `pytest` for the regression suite.

## Governance of the framework itself

- `templates/rules.md` is the only place rules are edited; run `python3 tools/gen_templates.py` to propagate them, and
  `python3 skill/spec_check.py rules <file>` to verify any copy.
- Every script change ships with a regression test (`python3 -m pytest -q skill/tests`). CI enforces both.
- Every process failure observed in use becomes a root cause and a process change — most controls in this
  repository originated that way.

## License

MIT — see [LICENSE](LICENSE).
