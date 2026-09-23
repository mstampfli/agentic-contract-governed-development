---
name: consistent-build
description: Keep a multi-module codebase consistent across modules and across writers (several agents, or one agent over a long task). Use when modules exchange data, share persisted state, or depend on each other's failure behavior — greenfield parallel builds, extending a built system, and ongoing work in an existing codebase.
---

# consistent-build

"Be consistent" as an instruction fails; cross-module bugs have structural causes, fixed by structure:

| Cause (observed) | Fix |
|---|---|
| Contracts pin signatures, not data / state / failure behaviour | Spec registries (formats, state, calls, failure contracts), one owner per entry |
| Consumer written before its producer invents it | Dependency order; consumers read and cite real code |
| Gaps filled with guesses | Ledgers (QUESTIONS / ASSUMPTIONS), every assumption decided |
| Spec covers only what its author thought of | Discovery: blind counter-specs, operational traces, reference systems, red team |
| Writers game the grader; orchestrator trusts self-reports | Fresh reviewers; orchestrator runs everything itself |
| Bugs fixed one instance at a time | Fixes by class + a class test kept forever |
| Reviews only add code; "correct" treated as "good" | Quality bar, measured continuously, judged per checkpoint, simplify pass |

Evidence (A/B runs, blind audits, acceptance tests hidden from writers): tinykv formats/ownership disagreements ~7 → ~2;
tinyq 15/17 vs 17/17 acceptance, every cross-module break of the plain build absent, high-severity consistency
findings 6→3 / 5→2; unregistered conventions still drifted. Cost ≈ 20× tokens (bookkeeping slips, an out-of-scope edge
case → tiers, batching, "question scope").

## The user: authoritative, never needed
* **Overrides** spec, plan, any decision; applied at the next step (amendment or process change):
  * running writer: SendMessage "stop <item> until V<k> merges" (partial code stays) → after merge "V<k> merged:
    re-read <entries>, ACK V<k>, continue <item>" (or a fresh builder);
  * affected reviewers: stopped, re-spawned fresh after the merge; red teamers: re-spawned once the target is green;
  * new or changed requirement: write / rewrite its acceptance tests before the amendment merges.
  The user may also change the bar, accept a miss, stop any loop.
* **Switch** `Ask the user: yes|no` at the top of `AGENTS.md` (missing = `no`). `no`: the loop decides everything
  (the better option by the user's goals; between equally good ones, the one that can be undone) and lists each
  ask-point decision in `STATUS.md` → "Decisions open to steer" (technical decisions: changelog only). `yes`:
  asks at the ask-points, waiting only for that item. Ask-points and exact rule — one place only: `rules.md` →
  Orchestrator → "Decisions and the user".

## Terms
* **Module**: unit with its own writer; module table row = id, files, Depends-on.
  * Id: letter, then letters/digits/`_` (no hyphens — ids sit in `ASSUMPTION-<id>-<n>`).
  * Every root file belongs to one row (user config/data included), except process files (`INTERFACES*.md`, ledgers,
    `STATUS.md`, `PROCESS.md`, `concerns.md`, `AGENTS.md`/`CLAUDE.md`, `prompts/`, `snapshots/`, `tests_review/`) and
    `tests_own/` (belongs to the writer whose id the file carries).
  * `PROJ` row (always present): build config, package `__init__`, test-runner config (collects `tests_own/`,
    `tests_review/`; `test_` = pytest default, set the pattern for other runners). Written by the orchestrator; writers
    send CHANGE REQUESTs; no amendment needed; not a component (no reviews, no green state). Orchestrator's questions: `Q-PROJ-<n>`.
* **Component**: module(s) that become green together (default one; group tiny or co-changing modules — scope map).
* **Roles**: orchestrator (you); writer / fixer (**fresh builder** = new writer agent: finding + spec + code, no
  transcript); reviewer (spec-change, module, seam, quality); red teamer; counter-specifier; researcher. Each spawned
  with its role line + brief. No role line → role by kind of work (rules intro).
* **Seam**: producer↔consumer of an FMT, writer↔reader of an EFF, caller↔callee of a CALL / R4 row, and every external
  boundary (`ext↔A`: users, third-party/untrusted callers, external services). Own clients (CLI, UI) are modules:
  client↔server is a module seam; their human users → `ext↔CLI`; a server others can reach → `ext↔<server>`. Written
  `A↔B` (`A-B` in file names); one coverage column each.
* **Ids**: `FMT-n` formats, `EFF-n` state, `CALL-n` calls, `HLP-n` helpers/constants/conventions, `REQ-n` user
  requirements, R4 rows by call; amendment `## V<k> <title>`, items `V<k>-<n>`; `ASSUMPTION-<id>-<n>`. Marks ("amended
  by V4-2") go on the defining line (heading, bold bullet, table row).
* **Versions**: first merged spec = V0 (no amendment sections); `## V<k>` → version k. `INTERFACES.proposed.md` = full
  spec with the draft applied; deleted after merge.
* **Full round** (per component): fresh module review of each module + fresh seam review of each touching seam whose
  other side exists (`ext↔A`: covered by A's module review + red team).
* **Green** — after a full round:
  * no break, no cross-module gap inside the failure model (smells never block);
  * no failing acceptance test that exercises it;
  * every owner's call decided; every coverage cell of its existing seams decided (planned seams may stay `open`);
  * no missing ACK; no unanswered question of its writers.
* **Owner's call**: single-module detail a spec-change review marks non-blocking → writer prompt's "Owner's calls:"
  line → writer decides, records `ASSUMPTION-<id>-<n>`; decided when that is.
* **Target** `T<n>`: runnable composite of green components red-teamed; scope map lists components + start commands.
* **Class**: pattern behind a finding. **Class test**: covers every instance, `tests_own/test_<id>_class_*`; red-team
  reproduction probes stay in `tests_review/`; both re-run after every writer run.
* **User requirements** `REQ-n`: every feature, requirement and target the user stated, verbatim in the spec (writers
  and reviewers see it). New quote → bookkeeping amendment; changed → semantic amendment `Touches:` it. Quotes keep
  their text; only the mark is added. Moving a planned feature to "now" `Touches:` its REQ-n.
  * Correctness (never lose data, exactly once, bit-for-bit) and stated features → acceptance tests. Hard: never
    accepted failing, never built upon failing.
  * Performance/quality targets ("under 200 ms") → measured quality-bar items.
  * Impossible (its redesign still fails, reason stated) or contradictory correctness requirement → closest
    achievable semantics, stated exactly (in V0: a rule + changelog line) — an ask-point.
* **Acceptance tests**: end-to-end, public interface, written by the orchestrator, kept with the measurement scripts
  in the **work directory** `~/.consistent-build/<project>/acceptance/` (path in `STATUS.md`, so a later session finds
  it). Never given to writers (they stay inside the root; the tests live outside it).
  Run once every component they exercise is green, and at every later checkpoint. External services: tested against
  fakes; a feature on one is done when it passes against fakes; a real-service check is a decision. The
  orchestrator's fakes live in the work directory; writers build their own in `tests_own/`; the protocol a fake
  imitates is registered (FMT).
* **Quality bar** (spec section): the user's performance/quality targets + orchestrator-set targets for areas where
  the user named none (ask-point).
  * Measured: workload, target (preferably vs a reference system), **hard limit** (default 3× worse; for a "≥ X"
    target: X/3; user may set per item).
  * Judged: scenario + criterion.
  * "None beyond green" is a valid recorded decision. Writers see the bar in words; scripts stay hidden; results →
    `STATUS.md`.
* **Decisions vs status**: spec = decisions (entries, requirements, scope, targets, bar, coverage), changed only by
  amendment. `STATUS.md` = progress, rewritten in place: "Decisions open to steer" first; per-component progress /
  green; red-team rounds; bar measurements + history; quality gaps and reported misses; open questions; open coverage
  count; what is running; work directory path.
* **Done** (current scope): all components green; red-team loops converged; acceptance tests pass; every bar item met
  or a reported miss (measured: within its hard limit).

## The spec: INTERFACES.md (template in `templates/`)
Sections: rules (verbatim), **failure model**, **user requirements**, **scope map**, quality bar, module table,
helpers, R1 formats, R2 state, R3 calls, R4 failure contracts, coverage, traces, changelog.
* **Failure model first**: crash, power loss/corruption, interrupts, **several processes on the same state**, others.
  Every rule depends on it; deciding it late = most expensive mistake observed.
* **R1** every shape crossing a boundary or persisted, byte-level where bytes matter, incl. limits; one owner + codec.
  **R2** one writer (in-process AND cross-process, e.g. lock file), lifecycle, crash ordering. **R3** semantics incl.
  None vs empty, errors, ownership, concurrency, who validates. **R4** per state-changing call × failure: state
  guaranteed afterwards, who restores it, what the caller is told (incl. "unknown outcome"). **Helpers, constants, conventions**
  (integer bounds, which error a bad argument raises): one home each (observed: unregistered convention → two
  exception types).
* **Scope map**: components, modules, dependencies, scope now / planned / undecided (planned boundaries provisional),
  targets `T<n>`.
* **Coverage** (orchestrator edits; reviewers propose): concern (`concerns.md`) × seam; cell = entry ref / `out:
  <reason>` / `n/a` / `open`. Columns from Depends-on pairs + external boundaries, refined as entries appear.
  `spec_check.py coverage` = what is open / needed next. It records only known concern kinds; discovery finds new
  ones → project copy AND skill copy of `concerns.md`, so the next project checks it from day one (skill updates).
* **Register before crossing a boundary**; registries complete at every point, not before coding. Pin early only
  between parallel writers who can't read each other's code — the registry is their only shared truth (pin R1
  byte-level + limits, R2, R3, R4); otherwise
  the producer's code is the truth (register owner + pointer).

### Changing the spec
* Drafts only in `INTERFACES.proposed.md`; writers read only the merged spec (observed: a draft in the real spec got
  implemented before review).
* **Marks**:
  * new entries / module rows / coverage columns: in place, "(added by V<k>)", listed under `Adds:`;
  * changed entries: named in `Touches:`, rewritten in place to the current rule + mark (the registries always read
    as the current truth); earlier marks stay ("amended
    by V2-1, V3-1"); the V section says what changed and why;
  * `R4[<call>]` in `Touches:` → every existing row of that call marked; an unchanged row gets "(reviewed in V<k>)"; a
    new row alone → `Adds:`;
  * items `V<k>-<n>` are never rewritten; a later one supersedes them; only edit: append "(superseded by V<k>-<n>)";
  * `spec_check.py marks` checks named entries; the reviewer finds unnamed ones, incl. accepted assumptions.
* **Tiers**: bookkeeping (verbatim acceptance, marks, new requirement quote, changelog) → mechanical checks; semantic
  → fresh spec-change reviewer. Merge criterion: no contradiction, correct under the failure model, nothing two modules
  could implement differently, no user requirement weakened.
* **Batch** a round's findings: one amendment, one fix round per module.
* **Consolidate, don't layer** (interacting amendments in one area → one entry):
  * replaced amendment heading tagged "(superseded by V<k>)" = its mark (`all` skips its marks and ACKs); partly
    replaced → restate its live items in the new amendment (not in `Touches:`), then tag the heading only (the
    item-level tag is for a single item superseded without consolidation); semantic if any
    rule changes, else bookkeeping;
  * `Touches:` = live entries only; `Affected:` = writers of replaced amendments who still must act;
  * answers/decisions tagged with a superseded version stay valid.
* **Question scope**: a draft rule adding code paths (interrupt safety, retries…) names its failure-model item and
  cost, else out of scope; drafts that keep failing review → is it in the failure model at all? (observed: an
  out-of-scope interrupt mechanism cost hundreds of lines).
* **Change protocol** (only the orchestrator edits the spec):
  1. CHANGE REQUEST from a writer (change + every consumer found). Product decision or weakened requirement →
     ask-point (observed in simulation: "add resend" vs "never send twice").
  2. **Impact derived, never remembered**: owners from registries + every file citing the entries or the owner's
     code (`grep -rln 'FMT-3\|<owner functions>' <root> --exclude-dir=snapshots`).
  3. Draft; cells of changed entries → `open`, re-decided in the draft. Pre-merge: `spec_check.py marks` + `ledger`
     on the proposed file + the tier's review. Merge; decision tags (`[ANSWERED V<k>]`, `[ACCEPTED V<k>]`, …) go on ledger headings at merge.
  4. Owner's code first, then consumers. Each `Affected:` writer ACKs `ACK V<k> <id>` (module not done without it;
     `all` checks after merge). `Affected:` = spawned writers that must act (ids comma-separated, or `none`), incl. the requester if it
     changes code; finished ones are resumed. Never `PROJ` or a module the amendment creates.

### Ledgers
* `QUESTIONS.md` — blocking. Writer stops the item. Answer = amendment, never a message only (`[ANSWERED V0]` if
  merged into V0; PROJ-only → orchestrator changes the file, `[ANSWERED PROJ]`). Resume the same agent by SendMessage:
  "Question <Q-id> answered by amendment V<k>: re-read <entries>, ACK V<k>, continue".
* `ASSUMPTIONS.md` — non-blocking; writers append entries headed with their id, and ACK lines; only the orchestrator
  tags headings.
* Each assumption gets one decision, recorded in an amendment and tagged `[ACCEPTED V<k>]` (the amendment quotes
  the assumption verbatim, never paraphrased) / `[REJECTED V<k>: <correct rule>]` (owner fixes code) / `[SUPERSEDED by <entry>]`. Reviewers give
  verdicts; the orchestrator decides; `spec_check.py ledger` lists undecided ones.

## Rules and roles
`templates/rules.md` = single source, sections **All roles**, **Writer / fixer**, **Reviewer**, **Probes**, **Red
teamer**, **Orchestrator**; each agent follows All roles + its role's sections only. Scripts/templates live in the
skill directory (`<skill dir>`, e.g. `~/.claude/skills/consistent-build`).
* **Copies**: spec and `AGENTS.md` carry all sections; `CLAUDE.md` → symlink to `AGENTS.md` (`ln -s AGENTS.md
  CLAUDE.md`; verified: the lazy CLAUDE.md load follows it; no symlinks → copy after every change). Prompts carry role
  line + All roles + own sections (briefs in `templates/`; counter-specifier / researcher briefs carry none). Fill
  header lines only: delete unused bracketed lines, drop brackets on kept ones ("[Fix task:]" → "Fix task:").
* **Rule change** → every copy AND every enforcing script in the same step (observed: "ledgers are history" while the
  citation check still read them).
* **Prompt files**: `prompts/<writer|review_<kind>|redteam|counterspec|research>_<id>_r<N>.md`; SendMessage texts (tasks,
  stop, resume) same name `.txt`; N counts that role+id's prompts and messages. Counter-spec ids `A`/`B`; researcher
  `REF1`…; spec-change reviewer: `review_spec-change_spec_r<N>.md`. `spec_check.py rules <file>` checks a `.md`
  prompt.
* **Subagents** get CLAUDE.md only lazily (after reading a file there) → the prompt copy is mandatory; put the absolute
  project root in every prompt (cwd may be reset).
* **Writers** never get review / red-team prompts (`prompts/` off limits), acceptance tests or measurement scripts; user
  requirements and the bar are requirements for them, not hidden grading.

## Phases (Mode 1: several agents; per component, no global phase)
1. **Discover** (initial system and every add-on), in order:
   * create the work directory. Two fresh agents write **blind counter-specs** there (`counterspec_brief.md`) from the
     user's request verbatim incl. future plans (add-on: its request — for a planned feature the original words
     about it — + a summary of the existing external interface). No failure model or draft from you, so they cannot inherit your blind spots. Prompts: before
     setup in `<work dir>/prompts/`, copied into `prompts/` at setup; add-on: straight into `prompts/`, next `r<N>`.
     Your own draft in parallel, in the work directory;
   * **setup** after both: copy `concerns.md`; create `QUESTIONS.md`, `ASSUMPTIONS.md`, `PROCESS.md` (orchestrator
     mistakes → process changes), `STATUS.md` (with work-dir path), `prompts/`, `tests_own/`, `tests_review/`,
     `snapshots/`, PROJ test config, `AGENTS.md` + `CLAUDE.md` symlink (now, so counter-specifiers can't read it);
   * **merge** into `INTERFACES.proposed.md`; the all / some / one list goes in the changelog. All → keep.
     Disagreement → decide, reason in the changelog (product decision → ask-point; technical → yours). Only one →
     adopt, or `out: <reason>` in coverage ("not adopted: <reason>" in the changelog if not a cell). Open questions
     → QUESTIONS.md or decide;
   * quote the **user requirements** (`REQ-n`);
   * **operational traces**: install, first start, restart while running, upgrade, overload, disk full, misuse;
   * **1–2 reference systems** (yourself or researchers, `researcher_brief.md`): what they handle and the draft doesn't
     = gap candidate (e.g. a data-dir lock);
   * **acceptance tests** for correctness requirements and stated features;
   * **quality bar**: the user's targets + for each area the user left open 2–3 candidates, each named, obtainable
     and comparable (e.g. a reference system's benchmark) — an ask-point; script measured items;
   * **run the reference system** where it runs locally (install in the work directory or a virtualenv): same
     workload → baseline; same public interface → also the acceptance tests (a test the mature system fails is
     probably wrong — observed: an over-reaching acceptance test);
   * fill coverage (incl. merge `out:`s) and scope map → spec-change review of the whole file → fix → merge as V0
     (add-on: next `## V<k>`, reviewed as a spec change).
2. **Build loop** (a component starts once its dependencies are green; independent ones in parallel): writer →
   mechanical checks → fresh module review → seam reviews of changed seams → fixes by class → repeat until a full
   round finds it green.
3. **Checkpoint loops** (both start at the same checkpoints, in parallel):
   **Red team**:
   * where: component + its dependencies green → smallest runnable composite containing it (not runnable alone →
     first composite that runs it); again on each larger green composite up to the whole system (some classes live
     only in the union, e.g. two processes on one data dir); separate composites in parallel;
   * round: fresh red teamer (`redteam_brief.md`) starts the target, keeps going after the first class, reports every
     class with instances + class test → fixes by class via the build loop → fresh red teamer given known classes as
     "<concern id> — <class> — class test <path>";
   * ends: a round finds no new class inside the failure model. Known class again = incomplete fix → fresh builder
     or spec change;
   * not after every fix: reviews and class tests cover local changes; unknowns appear when a part becomes whole.

   **Quality**:
   * round: fresh quality reviewer (`review_brief.md`, kind quality): each bar item met / below / not built yet +
     simplifications;
   * below + accepted simplifications → quality task to owners via the build loop (all tests and probes still pass,
     except strict-xfail probes of findings just fixed); needs a new/changed registry entry (e.g. a search index =
     new state) → change protocol first;
   * not built yet: specified → waits for its build; unspecified → scope map → next plan / extend;
   * ends by convergence, no round count: no accepted simplification pending, and a fresh reviewer finds nothing
     below the bar or no change expected to help.
     Still below then = **miss**, reported with the best value — measured items only if within the hard limit.
     Beyond it = failure: escalate like correctness (fresh builder → spec change / redesign); still beyond after the
     redesign → ask-point (reset target = semantic amendment of its bar row);
   * **done** → report with `STATUS.md` (met, misses, decisions open to steer). Planned ("later") features = ask-point;
     under `no` the loop continues into them.
4. **Plan / extend** (from any green part; start from the latest quality gaps and open coverage cells):
   * specify the add-on with phase 1 (scope map; new seams → entries + coverage columns);
   * **reopen** cells in columns of seams whose producer / writer / callee the add-on uses directly (deeper only where
     a trace carries new inputs or load), unless the add-on's amendment states why a concern can't be affected — new
     consumers bring needs the old spec never considered;
   * re-decide them in the draft before merge (existing components stay green; ones whose entries change → phase 2);
   * then phases 2–3 (Mode 2: its steps 2–7 instead).

## Reviews (`review_brief.md`: spec-change / module / seam / quality; `redteam_brief.md`)
* Always a **fresh** agent (authors and earlier reviewers are anchored). Re-review: previous findings as checklist +
  real diff (git, or the pre-run snapshot, `diff -ru`); reviews from scratch incl. regressions.
* Output: spec-change / module / seam by class (concern id, all instances, class fix, assumption verdicts); quality per
  bar item + simplifications. First line: what most blocks green / the bar. Formats and probe rules: rules.md.
* When: module review after every semantic module change — a simplification (deleted or merged code) always counts,
  and its reviewer checks that nothing removed was needed by a spec entry, class test or acceptance test; seam review when a side changes meaning; spec-change review
  per semantic amendment; red team + quality per green checkpoint; comment-only changes → mechanical checks.

## Orchestrator duties (never trust self-reports)
**Before spawning**: save the prompt (`prompts/`; before setup `<work dir>/prompts/`), run `spec_check.py rules` on it
(unfilled header placeholders, wrong rule sections fail).

**Before every writer run** (and resume), N = r<N> of the starting prompt/message: `cp -r` its modules →
`snapshots/<component>-<id>-r<N>/` (skip if no code yet); `touch <work dir>/stamp_<id>_r<N>`.

**After every writer run**, in order:
1. Its tests with its reported command ("0 tests ran" = red flag), every class test, every saved probe (each file,
   `timeout 120`; a strict-xfail probe of a just-fixed finding fails by design → next reviewer rewrites it).
2. `verify_citations.py <root>`; stale citation after an owner's change: code / `tests_own/` → its writer;
   `tests_review/` → you.
3. `spec_check.py all INTERFACES.md ASSUMPTIONS.md` (before V0: on the proposed file): marks, ledger, ACKs, questions,
   rules copies (spec, AGENTS.md, `prompts/*.md`), AGENTS.md / symlink. Coverage is informational → run
   `spec_check.py coverage` before declaring green.
4. Measured bar items whose components exist.
5. Read the ledgers.
6. Scope: `find <root> -type f -newer <work dir>/stamp_<id>_r<N>` (+ `git status` for deletions) → only its files,
   its `tests_own/`, ledger appends (entries headed with its id, ACK lines). Ignore tool caches, virtualenvs, process
   and PROJ files changed by you / reviewers / red teamers, files of writers running concurrently.
7. Rewrite `STATUS.md`.

**Standing rules**:
* A fixer's own tests never verify its fix.
* Findings to owners by class; first fix → same writer (SendMessage, saved `.txt`); same finding again → fresh builder.
* No round cap; steer by convergence. Correctness failures are never accepted: stalls escalate (fresh builder → spec
  change / redesign).
* Nothing others depend on stays a "known issue"; only local non-correctness items, approved by the orchestrator and
  listed in "Decisions open to steer".
* Every orchestrator mistake → root cause + process change in `PROCESS.md`; general ones (process fixes, new concern
  kinds) also into this skill — **skill updates** (not writable → `PROCESS.md` "skill updates" + tell the user). Most
  tools here came from one.
* Isolate parallel writers only while the other side doesn't exist; every forced stand-in / duplicate gets a
  follow-up.

## Mode 2 — Ongoing work in an existing codebase
**Setup** (once): short INTERFACES.md — rules, failure model, user requirements, module table (id, files, Depends-on,
incl. `PROJ`), formats, state, calls, failure contracts, helpers (owner + pointer to code), scope map, coverage; both
ledgers, `PROCESS.md`, `STATUS.md`, `concerns.md` copy, work directory, `prompts/`, `tests_own/`, `tests_review/`,
`snapshots/`, PROJ test config; `AGENTS.md` + `CLAUDE.md` symlink with `<project>`, `<skill dir>` (absolute) filled
(`all` flags unfilled ones).

**Each change** (the session is orchestrator for decisions, spec and verification, writer for its code):
1. Classify: adds a module or seam → phase 4's discovery, then steps 2–7 (this session writes the code); new/changed
   entry on existing seams → steps 2–7 with the amendment in step 4; code only → steps 2–7, no semantic amendment.
2. Save a one-line `prompts/writer_<id>_r<N>.txt` describing the change (N = next number for that id); snapshot /
   commit the modules (reviewers need a diff); `touch <work dir>/stamp_<id>_r<N>` (scope-breach check).
3. New user-visible behaviour or a new/changed requirement → quote as `REQ-n`; write / rewrite its acceptance test
   first (never edit one to pass).
4. Amendment (if any): change protocol steps 2–4. `Affected:` = modules you change (not PROJ or new ones); ACK as each
   module's id.
5. Code, owner first; tests: contract test per consumer that can't import the owner's codec, failure-injection test
   per new R4 row, class test per fixed class.
6. Orchestrator duties checklist; fresh module review per changed module with new behaviour (comment-only →
   mechanical), seam review per changed seam.
7. Feature whole → red-team round + quality review (if the project has a bar). `STATUS.md` as in Mode 1.

## Files
* `templates/rules.md` — all rules (single source). `templates/INTERFACES.template.md` — spec skeleton.
* `templates/AGENTS.md.template` — switch, pointers, all rules (`CLAUDE.md` = symlink).
* Briefs: `writer_brief.md`, `review_brief.md` (kinds), `redteam_brief.md`, `counterspec_brief.md`,
  `researcher_brief.md`.
* `concerns.md` — concern kinds (coverage rows); add every new kind.
* `spec_check.py` (`python3 <skill dir>/spec_check.py …`): `marks SPEC [V<k>]`, `ledger SPEC LEDGER`, `acks SPEC
  LEDGER`, `coverage SPEC [CATALOG]`, `questions DIR|QUESTIONS.md`, `rules FILE`, `all SPEC LEDGER` (+ questions,
  AGENTS.md, symlink, `prompts/*.md`).
* `tests/test_scripts.py` — one regression test per real finding, correct and broken input each. Run `python3 -m
  pytest -q <skill dir>/tests` after every script change; add a test per new case (observed: three straight rounds
  shipped a script regression).
* `verify_citations.py` — every `Cite:` points at a real file:line containing the snippet (proves the writer looked,
  not that the code is right); skips `snapshots/`, `prompts/`, virtualenvs, root ledgers, `PROCESS.md`, `STATUS.md`.
