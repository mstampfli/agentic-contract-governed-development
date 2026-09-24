---
name: acgd
description: Keep a multi-module codebase consistent across modules and across writers — several writer agents in parallel (Mode 1) or one agent writing alone (Mode 2, solo), on a new project or an existing codebase. Use when modules exchange data, share persisted state, or depend on each other's failure behavior — greenfield builds, extending a built system, and ongoing work in an existing codebase.
---

# ACGD — Agentic Contract-Governed Development

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
findings 6→3 / 5→2; unregistered conventions still drifted. Cost: much larger token usage than a plain build
(bookkeeping slips, an out-of-scope edge case → tiers, batching, "question scope").

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

## Pick a mode
Two choices: where you start (new project / existing codebase) and who writes the code. Reviewers, red teamers,
counter-specifiers and researchers are fresh agents in every mode.

| | New project | Existing codebase |
|---|---|---|
| **Mode 1** — several writers: you orchestrate, writer agents build components in parallel | Phases 1 → 2 → 3 (done); phase 4 per add-on | "Start: existing codebase"; per add-on: baseline round → phase 4 |
| **Mode 2** — solo: this session orchestrates and writes the code, one change at a time | Phase 1 → "Each change" per component | "Start: existing codebase" → "Each change" |

* **Mode 1** only when ≥2 components can be built at the same time (their dependencies green) and each is large or
  complex enough that parallel writing saves real time. Otherwise **Mode 2**: work that comes one change at a time
  (bug fixes, a feature along one dependency chain), a small or simple system (few components, few seams, little
  shared state), or unsure. The evidence above comes from Mode 1 builds; Mode 2 is not yet measured. Switch any time
  on the same spec.
* **Already set up** (`STATUS.md` exists; it records mode and start): continue where it says — unfinished work in its
  phase / step; new work → Mode 1 phase 4 (existing codebase: baseline round first), Mode 2 "Each change". No mode
  recorded (set up before modes existed): start = new project if the work directory holds counter-specs, else
  existing codebase; mode by the routing above (this session writing the code = Mode 2); record both in `STATUS.md`.
  A mode switch updates `STATUS.md`. Skill rules changed since setup (`spec_check.py rules` reports differing
  sections) → re-copy `rules.md` into INTERFACES.md (bookkeeping amendment), AGENTS.md and saved `prompts/*.md`
  (headers stay). Agents of an earlier session are gone: an unfinished writer
  item goes to a fresh builder (Mode 2: this session) on the current code, counted as the same writer (Standing
  rules); the snapshot from before the item stays the review diff base, the new run gets its own stamp; reviews
  re-spawn fresh.
* "Phases" is written for Mode 1. Mode 2 uses phase 1, phase 3's checkpoint loops and phase 4's first three bullets
  (specify, reopen, re-decide); there, "via the build loop" means "Each change" steps 2–6.

## Terms
* **Module**: unit with its own writer (Mode 2: one writer for all; ids stay per module — they name ownership in
  ledgers, ACKs and assumptions); module table row = id, files, Depends-on.
  * Id: letter, then letters/digits/`_` (no hyphens — ids sit in `ASSUMPTION-<id>-<n>`).
  * Every root file belongs to one row (user config/data included), except process files (`INTERFACES*.md`, ledgers,
    `STATUS.md`, `PROCESS.md`, `concerns.md`, `AGENTS.md`/`CLAUDE.md`, `prompts/`, `snapshots/`, `tests_review/`, `tests/acceptance/`) and
    `tests_own/` (belongs to the writer whose id the file carries).
  * `PROJ` row (always present): build config, package `__init__`, test-runner config (collects `tests_own/`,
    `tests_review/`, `tests/acceptance/`; `test_` = pytest default, set the pattern for other runners). Written by the orchestrator; writers
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
  * no break, no cross-module gap inside the failure model (smells and nits never block);
  * no failing acceptance test that exercises it;
  * every owner's call decided; every coverage cell of its existing seams decided (planned seams may stay `open`);
  * no missing ACK; no unanswered question of its writers.
* **Nit**: rules.md → All roles. **Trivial change**: changes no behaviour, touches no registered entry, seam or
  cross-module convention, and deletes or merges no code (comments, log wording, formatting, a module-private
  rename, project docs — not the spec) — e.g. most nit fixes. Judged by the orchestrator from the diff, never from the
  writer's reply; in doubt → not trivial.
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
  * Performance/quality targets ("under 200 ms") → quality-bar items (measured or judged).
  * Impossible (its redesign still fails, reason stated) or contradictory correctness requirement → closest
    achievable semantics, stated exactly (in V0: a rule + changelog line) — an ask-point.
* **Acceptance tests**: end-to-end, public interface, written by the orchestrator, kept with the measurement scripts
  in the **work directory** `~/.acgd/<project>/acceptance/` (path in `STATUS.md`, so a later session finds
  it). Hidden from writers only while the components they exercise are being built (writers game visible tests —
  observed; Mode 2: the solo writer writes them and the measurement scripts, so its module reviewers check that no
  code special-cases them instead); once those components are green, the orchestrator moves the tests into the
  project's `tests/acceptance/` as regular regression tests (writers may run them, never edit them). Tests for new features or
  add-ons start hidden again.
  Run once every component they exercise is green, and at every later checkpoint. External services: tested against
  fakes; a feature on one is done when it passes against fakes; a real-service check is a decision. The
  orchestrator's fakes live in the work directory; writers build their own as `tests_own/test_<id>_*` /
  `tests_own/data_<id>_*`; the protocol a fake
  imitates is registered (FMT).
* **Quality bar** (spec section): the user's performance/quality targets + orchestrator-set targets for areas where
  the user named none (ask-point).
  * Measured: workload, target (preferably vs a reference system), **hard limit** (default 3× worse; for a "≥ X"
    target: X/3; user may set per item).
  * Judged: scenario + criterion + **stance** toward the named reference:
    * beat: judge sees ours and the reference in the same scenario; ours must be picked;
    * match: ours must not be picked worse (a tie passes);
    * differ: named identity axes where ours must be recognisably different (a judge describing both gives
      different answers) + floor axes where it must not be worse;
    * criterion: no reference, judged against the criterion alone.
    Reference not runnable → compare against collected material (footage, screenshots, published numbers) in the
    work directory, never from memory.
    Project default in the section; stance per item is part of the bar's ask-point. Hard limit: fallback stance
    (default: beat → match; others none = any shortfall is a reported miss); a user's "must": the stance itself.
  * "None beyond green" is a valid recorded decision. Writers see the bar in words; scripts stay hidden; results →
    `STATUS.md`.
* **Decisions vs status**: spec = decisions (entries, requirements, scope, targets, bar, coverage), changed only by
  amendment. `STATUS.md` = progress, rewritten in place: "Decisions open to steer" first; mode and start (new /
  existing codebase); per-component progress / green; red-team rounds; bar measurements + history; quality gaps and
  reported misses; open questions; open coverage count; not-yet-conforming components (existing codebase); what is
  running; work directory path.
* **Done** (current scope): all components green; red-team loops converged; acceptance tests pass; every bar item met
  or a reported miss (within its hard limit).

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
  targets `T<n>` (listed at V0; a new one = bookkeeping amendment).
* **Coverage** (orchestrator edits; reviewers propose): concern (`concerns.md`) × seam; cell = entry ref / `out:
  <reason>` / `n/a` / `open`. Columns from Depends-on pairs + external boundaries, refined as entries appear.
  `spec_check.py coverage` = what is open / needed next. It records only known concern kinds; discovery finds new
  ones → project copy AND skill copy of `concerns.md`, so the next project checks it from day one (skill updates).
* **Register before crossing a boundary**; registries complete at every point, not before coding. Pin early only
  between parallel writers who can't read each other's code — the registry is their only shared truth (pin R1
  byte-level + limits, R2, R3, R4), and always in Mode 2 (Mode 2 → "Pinning"); otherwise the producer's code is the
  truth (register owner + pointer).

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
* **Tiers**: bookkeeping (verbatim acceptance, marks, new requirement quote, changelog, rules-copy refresh, nit fixes
  in prose outside entries, REQ quotes and V items; existing
  codebase: scope-map additions, the user's scope override) → mechanical checks; semantic
  → fresh spec-change reviewer. Merge criterion: no contradiction, correct under the failure model, nothing two modules
  could implement differently, no user requirement weakened.
* **Batch** a round's findings: one amendment, one fix round per module.
* **Re-read before re-review**: after fixing a review round's findings, re-read the whole spec (not only the edited
  lines), check each edit in context and grep for restatements of every touched rule; then the fresh re-review
  (observed: fast targeted patches re-broke other entries, and review rounds stopped converging).
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
skill directory (`<skill dir>`, e.g. `~/.claude/skills/acgd`).
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
* **Writers** never get review / red-team prompts (`prompts/` off limits), hidden acceptance tests or measurement scripts; user
  requirements and the bar are requirements for them, not hidden grading (Mode 2: Terms → "Acceptance tests").

## Phases (Mode 1: several agents; per component, no global phase)
1. **Discover** (initial system and every add-on), in order:
   * create the work directory `~/.acgd/<project>/` (`<project>` = the project root's directory name). Two fresh agents write **blind counter-specs** there (`counterspec_brief.md`) from the
     user's request verbatim incl. future plans (add-on: its request — for a planned feature the original words
     about it — + a summary of the existing external interface). No failure model, draft or research from you, so they cannot inherit your blind spots
     (research is the later gap check, not their input); every fact they state from memory is unverified until a
     researcher or the primary source confirms it. Prompts: before
     setup in `<work dir>/prompts/`, copied into `prompts/` at setup; add-on: straight into `prompts/`, next `r<N>`.
     Your own draft in parallel, in the work directory;
   * **setup** after both: copy `concerns.md`; create `QUESTIONS.md`, `ASSUMPTIONS.md`, `PROCESS.md` (orchestrator
     mistakes → process changes), `STATUS.md` (with work-dir path), `prompts/`, `tests_own/`, `tests_review/`,
     `snapshots/`, PROJ test config, `AGENTS.md` (`<project>`, `<skill dir>` filled, absolute) + `CLAUDE.md`
     symlink (now, so counter-specifiers can't read it);
   * **merge** into `INTERFACES.proposed.md`; the all / some / one list goes in the changelog. All → keep.
     Disagreement → decide, reason in the changelog (product decision → ask-point; technical → yours). Some or only one →
     adopt, or `out: <reason>` in coverage ("not adopted: <reason>" in the changelog if not a cell). Open questions
     → QUESTIONS.md or decide;
   * quote the **user requirements** (`REQ-n`);
   * **operational traces**: install, first start, restart while running, upgrade, overload, disk full, misuse;
   * **1–2 reference systems** (yourself or researchers, `researcher_brief.md`): what they handle and the draft doesn't
     = gap candidate (e.g. a data-dir lock);
   * **acceptance tests** for correctness requirements and stated features in scope now (planned ones: at their add-on);
   * **quality bar**: the user's targets + for each stated feature / component without a user target 2–3 candidates, each named, obtainable
     and comparable (e.g. a reference system's benchmark) — an ask-point; script measured items;
   * **run the reference system** where it runs locally (install in the work directory or a virtualenv): same
     workload → baseline; same public interface → also the acceptance tests (a test the mature system fails is
     probably wrong — observed: an over-reaching acceptance test);
   * fill coverage (incl. merge `out:`s) and scope map → spec-change review of the whole file → fix → fresh re-review until
     no blocking finding → merge as V0
     (add-on: next `## V<k>`, reviewed as a spec change).
2. **Build loop** (a component starts once its dependencies are green; independent ones in parallel): writer →
   mechanical checks → fresh module review → seam reviews of changed seams → fixes by class → repeat until a full
   round finds it green (trivial changes: Reviews → "When").
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
   * ends by convergence, no round count: no accepted simplification pending, and a fresh reviewer finds every
     item met, or below with "no change expected to help".
     Still below then = **miss**, reported with the best value — only if within its hard limit.
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
* Always a **fresh** agent (authors and earlier reviewers are anchored). Re-review: previous findings (not nits) as
  checklist +
  real diff (git, or the pre-run snapshot, `diff -ru`); reviews from scratch incl. regressions.
* **Sweep before re-review** (every review kind and red-team round, both modes): after a round's findings the fixer
  fixes each class, searches its own work for similar problems (same root cause in another shape, the same mistake
  elsewhere) and makes one general pass over what it changed — then a fresh reviewer. Writer: its own files (rules.md
  → Writer / fixer); what it lists elsewhere → the orchestrator routes each to its owner as a finding (nits: Standing
  rules); listed quality
  items → judged by the next quality round. Orchestrator: the spec ("Re-read before re-review").
* Output: spec-change / module / seam by class (concern id, all instances, class fix, assumption verdicts); quality per
  bar item + simplifications. First line: what most blocks green / the bar. Formats and probe rules: rules.md.
* When: module review after every semantic module change — a simplification (deleted or merged code) always counts,
  and its reviewer checks that nothing removed was needed by a spec entry, class test or acceptance test; seam review when a side changes meaning; spec-change review
  per semantic amendment; red team + quality per green checkpoint; trivial changes (Terms) → mechanical checks, no
  fresh review (green stays).

## Orchestrator duties (never trust self-reports)
**Before spawning**: save the prompt (`prompts/`; before setup `<work dir>/prompts/`), run `spec_check.py rules` on it
(unfilled header placeholders, wrong rule sections fail).

**Before every writer run** (and resume), N = r<N> of the starting prompt/message: `cp -r` its modules →
`snapshots/<component>-<id>-r<N>/` (skip if no code yet); `touch <work dir>/stamp_<id>_r<N>`.

**After every writer run**, in order:
1. Its tests with its reported command ("0 tests ran" = red flag), every class test, `tests/acceptance/`, every saved probe (each file,
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
* A round that finds no break / gap (spec-change: no blocking finding) ends that loop (observed: ~15 spec-review
  rounds spent on non-issues in a real run). Smells and nits never start a round: fix them with the next real fix round, list or drop them; a nit-only fix is at most a trivial change
  (mechanical checks only, green stays) — never a known issue, never "same finding again".
* "Outside failure model" reports (red team) → extend the failure model (semantic amendment; then a class like any
  other) or record `out: <reason>` in coverage (no cell → changelog line "not adopted: <reason>").
* Every orchestrator mistake → root cause + process change in `PROCESS.md`; general ones (process fixes, new concern
  kinds) also into this skill — **skill updates** (not writable → `PROCESS.md` "skill updates" + tell the user). Most
  tools here came from one.
* Isolate parallel writers only while the other side doesn't exist; every forced stand-in / duplicate gets a
  follow-up.

## Start: existing codebase (brownfield)
**Setup** (once, either mode): short INTERFACES.md registering what the code does today — rules, failure model, user
requirements, module table (id, files, Depends-on, incl. `PROJ`), formats, state, calls, failure contracts, helpers
(owner + pointer to code), scope map, coverage, quality bar for in-scope components (ask-point; "none beyond green"
is valid; each scope addition adds its items, in that component's baseline amendment); both ledgers,
`PROCESS.md`, `STATUS.md`, `concerns.md` copy, work directory, `prompts/`, `tests_own/`, `tests_review/`,
`snapshots/`, PROJ test config; `AGENTS.md` + `CLAUDE.md` symlink with `<project>`, `<skill dir>` (absolute) filled
(`all` flags unfilled ones). Later phase 1 runs skip phase 1's setup step.
* Draft in `INTERFACES.proposed.md` → spec-change review → fixes → fresh re-review until no blocking finding → merge
  as V0 (no counter-specs: the code is the source).
* Behaviour wrong under the failure model → register the correct rule, not the bug; its owner stays listed in
  `STATUS.md` as "not yet conforming" until a baseline round fixes it.
* `REQ-n`: the user's stated requirements for the system and the work at hand (none → none); acceptance tests per
  change, like any new requirement.
* Existing code has no `Cite:` lines — not a finding (new and changed code cites as usual).

**Scope** (scope map, Scope column): in scope = the components the work touches or calls directly, plus every
not-yet-conforming component they depend on; each later change adds its own. The rest is "existing, unreviewed":
* it counts as green wherever a rule needs a component green (dependencies, acceptance-test runs, targets, phase
  4's start);
* red team and quality stop at the smallest composite containing all in-scope components;
* seam reviews toward it are part of a full round; a finding in it (review, red team, acceptance test, sweep
  listing) brings it into scope: scope-map addition merged at once, then its baseline round, then the fix;
* Done (Terms) covers in-scope components only; the Done report lists out-of-scope "not yet conforming" ones.
* User override "check everything": every component in scope, recorded in the scope map with the user's words (not a
  `REQ-n`); then a baseline round for every component, dependencies first, and phase 3's loops on the whole system;
  Done over all components.

**Baseline round** — a component's first full round, making existing code green before anything builds on it:
* When: before the change is drafted, for each in-scope component not green yet, dependencies first (scope from the
  request). Mode 1: before phase 4; Mode 2: after step 1's classification. A component the draft brings into scope →
  its baseline round before the draft merges: the draft moves to `<work dir>/draft_<title>.md`, the baseline's
  amendment goes through `INTERFACES.proposed.md` and merges, then the draft is re-applied and re-reviewed.
* Against the merged spec, like any review. One semantic amendment (if needed): the orchestrator decides the open
  coverage cells of the component's seams and its quality-bar items; Mode 2 also pins the entries the component owns, before its reviews
  ("Pinning"). Open owner's calls the existing code answers → the orchestrator records them as
  `ASSUMPTION-<id>-<n>` pointing at the code; the rest go to the first fix run (a run of their own if nothing else
  needs fixing). The change's own new acceptance
  tests don't count for baseline green.
* How: snapshot `snapshots/<component>-<id>-r0/` (diff base); mechanical checks = "After every writer run" 1–5 with
  the project's own test command; fresh module + seam reviews → fixes by class + sweep → repeat until green. Fixes
  are normal writer runs (next free r<N>, prompt, snapshot, stamp, duties): Mode 1 → a fresh builder first, then
  Standing rules; Mode 2 → this session (prompt as in "Each change" step 2).

## Mode 2 — Solo: new project or existing codebase
* **New project**: phase 1 (incl. its setup) → V0; then each component, dependencies first, as one change (a module
  already in V0 is "code only", unless an entry is missing or wrong).
* **Existing codebase**: "Start: existing codebase", then per change.
* **Pinning** (all registries as for parallel writers — R1 byte-level + limits, R2, R3, R4; after a context
  compaction or in a later session the writer is effectively a new agent that no longer remembers why the code is
  shaped as it is): new project at V0; existing codebase in each component's baseline round; after a switch from
  Mode 1, in the amendment of the first change that crosses an unpinned entry.

**Each change** (this session: orchestrator for decisions, spec and verification; the only writer — except a fresh
builder when a fix stalls, Standing rules):
1. Classify: adds a module or seam → phase 4's first three bullets (the draft merges in step 4), then steps 2–7;
   new/changed entry on existing seams (incl. pinning an entry after a switch from Mode 1) → steps 2–7 with the
   amendment in step 4; code only → steps 2–7, no semantic amendment; trivial (Terms) → steps 2, 5 and the
   mechanical checks only. Existing codebase: baseline round first ("Start: existing codebase").
2. Per module id the change writes: save a one-line `prompts/writer_<id>_r<N>.txt` describing the change (N = next
   free number for that id); snapshot / commit the modules (reviewers need a diff; skip if no code yet); `touch <work
   dir>/stamp_<id>_r<N>` (scope-breach check: the change's modules together).
3. New user-visible behaviour or a new/changed requirement not yet covered by an acceptance test → quote as `REQ-n`;
   write / rewrite its acceptance test first (never edit one to pass).
4. Amendment (if any): change protocol steps 2–4. `Affected:` = modules you change (not PROJ or new ones); ACK as each
   module's id.
5. Code, owner first; tests: contract test per consumer that can't import the owner's codec, failure-injection test
   per new R4 row, class test per fixed class.
6. Orchestrator duties checklist; fresh module review per semantically changed module (a simplification counts;
   trivial → mechanical; plus the special-casing check, Terms → "Acceptance tests"), seam review per changed
   seam. Findings → fixes by class + sweep, then steps 2, 4 (if a fix
   needs an amendment), 5, 6 again (a new snapshot, so each re-review diff shows the fixes) with fresh reviewers
   until a full round finds each touched component green; same finding again → fresh builder, then spec change /
   redesign (Standing rules). Only then the next change or component.
7. Checkpoints — phase 3's red-team and quality loops (existing codebase: up to the in-scope composite, "Scope"):
   during a new project's initial build at each green checkpoint, afterwards once a feature is whole. A bug fix
   alone → the red-team loop only if the bug crossed a seam or hit a failure-model item; a local bug → reviews +
   class test only; Done after bug fixes alone: bar items as last measured / judged (never judged → one quality
   round first). The loops run alongside the next change unless it writes a component in the target (then after
   them); their fixes are steps 2–6, each finished before the next change resumes. `STATUS.md` as in Mode 1. Done =
   Terms → Done (existing codebase: "Scope").

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
