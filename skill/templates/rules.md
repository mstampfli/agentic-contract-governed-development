## Rules (canonical source)
Every agent is told its role in its task. Follow **All roles** + your role's section + the sections it names; the
other sections describe other roles — read, never follow. (Counter-specifiers and researchers follow only their
brief.) `<your id>` = the id in your role line; leave the rule text unfilled.
No role line (e.g. a session working directly for the user):
- Role per part of the work: code → Writer / fixer (`<your id>` = module-table id of the module owning each file you
  change); review → Reviewer; breaking the system → Red teamer; running this process → Orchestrator.
- Nobody orchestrates for you: any code change, or a change to a registered entry (format, state, call, failure
  contract, helper / constant / convention, user requirement) makes you also the Orchestrator → SKILL.md, "Pick a mode"
  (writing the code yourself = Mode 2: snapshot first, acceptance test before code for new user-visible behaviour,
  fresh reviews).
- Writer limits (stay inside the root, don't read `prompts/`) bind only your writing part; your orchestrator part
  uses the work directory and `prompts/`.
- Undecidable from spec or code → Orchestrator, "Decisions and the user". (With a role line: No-invention.)

### All roles
- Read-then-rely: open and cite whatever you rely on (module, spec entry, ledger entry):
  `Cite: <path>:<line> "<exact snippet>"` (path relative to the project root), never from memory. Citations in code,
  tests and the spec are checked and kept current; ledgers, `prompts/`, `PROCESS.md`, `STATUS.md` are history.
- Only the merged INTERFACES.md is binding; INTERFACES.proposed.md is a draft under review.
- No "agreed with / matches / as X expects" without a citation.
- Only the orchestrator edits INTERFACES.md, the coverage matrix and decision tags. Write only what your role allows.
- Sandbox: act only on the project, temp directories, the work directory and fakes — never on real devices,
  accounts, services or user data, unless the spec says so.

### Writer / fixer (task says: "Your role: writer <id>")
- Owner rule: only the owner of FMT-n encodes/decodes it; only the writer of EFF-n mutates it. Call the owner's
  functions; say "FMT-n" instead of re-describing a layout. Helpers, constants, conventions: registered, one home.
  Can't import the owner's code (e.g. another language — a separate process is no reason)? Implement FMT-n exactly as
  written, in one place, with a contract test `tests_own/test_<your id>_contract_*` against the owner's golden bytes;
  owners of such formats publish them as `tests_own/data_<your id>_golden_*`.
- No-invention: a fact in neither spec nor code → QUESTIONS.md (blocking — another module or a user
  requirement depends on the answer: stop that item, say so in your reply) or ASSUMPTIONS.md (non-blocking: `## ASSUMPTION-<your id>-<n> — <text>`, code marked with the same id).
- User requirements and the quality bar are requirements: meet the items your module affects. Add no code path the
  spec doesn't need (no failure-model item → ask, don't build).
- ACK every amendment whose "Affected:" names you: append `ACK V<k> <your id>` to ASSUMPTIONS.md.
- Stay inside the project root (read and write; temp directories allowed); never read `prompts/`.
- You may write: your module files; `tests_own/test_<your id>_*`, `tests_own/data_<your id>_*`; ledger appends
  (entries headed with your id, ACK lines naming it). Never `tests_review/`, `tests/acceptance/` (run them, don't edit), other writers' files, the spec.
- Registered entry or `PROJ` file (build/test config, package init) must change → CHANGE REQUEST in your reply
  (blocking → also QUESTIONS.md): the change + every consumer found. Code changes only after the amendment merges,
  owner first, then consumers (`PROJ`: the orchestrator changes it).
- QUESTIONS.md entries: `## Q-<your id>-<n> — <question>` (tagged `[ANSWERED V<k>]`, `V0` if merged into the first
  spec, `[ANSWERED PROJ]` if a `PROJ` file changed; the orchestrator's own: `Q-PROJ-<n>`).
- Fix the class, not the instance: every instance in your files + a class test `tests_own/test_<your id>_class_*`
  (class spanning modules: the orchestrator names who writes it). Then sweep: search your files for similar problems
  (same root cause in another shape, the same mistake elsewhere) and make one general pass over what you changed;
  each problem found is a class (fix + class test); a similar problem outside your files → list it in your reply; a
  spec gap → QUESTIONS.md / CHANGE REQUEST. Quality tasks (bar item below target, simplification): sweep findings
  are listed in your reply, not applied; no class test — the orchestrator measures; all existing tests still pass
  (strict-xfail probes of findings just fixed fail by design).
- Reply: files, questions/assumptions, change requests, classes found by the sweep, the exact test command, line
  moves that stale others' citations.

### Reviewer (task says: "Your role: reviewer, kind <spec-change | module | seam | quality>, id <id>")
- Never modify code, spec or ledgers; write only new probes `tests_review/test_<kind>_<id>_*` (seam ids `A-B`) and
  the rewrites "Probes" allows. Also follow "Probes".
- Kinds spec-change, module, seam — by CLASS: concern id from concerns.md (or "NEW CONCERN: <name>"), every other
  instance (search the code), a class-level fix (spec rule, shared helper, class test). Severity break (wrong behaviour) / gap (a case no entry or code handles) / smell
  (neither)
  (spec-change: blocking findings only + a separate "owner's call" list). First line: the class that most blocks
  green. Verdict on every assumption headed with a reviewed module's id (spec-change: every one the draft touches): accept / reject (why, correct rule) / supersede; seam: do the two sides'
  assumptions contradict? Report behaviour no spec entry or assumption explains. Propose coverage changes.
- Kind quality — per "User requirements" target and "Quality bar" item: met / below (measured vs target, within or
  beyond the hard limit, why, the change that closes it or "no change expected to help") / not built yet (what, which
  planned component). Judged items by their stance: beat / match → run ours and the reference through the same
  scenario, say which is better or "tie" and the single biggest gap; differ → is ours distinct on each identity axis, and not
  worse on each floor axis; criterion → against the criterion. Then simplifications (code traced to no spec entry, fixed class or acceptance test;
  duplication; handling of failures outside the failure model), each with the tests showing it is safe. No concern
  ids, severities or assumption verdicts. First line: the gap that most blocks the bar.

### Probes (reviewers and red teamers)
- Run with the project's test runner, terminate (<60 s per file), assert the SPECIFIED behaviour.
- Known bug → strict xfail naming the finding (fixed later → the probe fails → next reviewer rewrites it).
  Behaviour the spec doesn't decide yet → assert the proposed fix as strict xfail; rewrite once decided.
- Realistic fault injection: a stubbed syscall succeeds (possibly short) or raises, never both; real signatures;
  patch os-level functions, not private helpers.
- Failing old probe, by its actual output: spec changed → rewrite; injection point moved → re-target; real regression
  → keep failing, report. You may rewrite any probe you classified, whoever wrote it (say so).

### Red teamer (task says: "Your role: red teamer, target <target id>")
- Never modify code, spec or ledgers; write only new probes `tests_review/test_redteam_<target id>_*` and the rewrites
  "Probes" allows. Also follow "Probes".
- BREAK the running system with unplanned scenarios: operations (restart while running, upgrade, disk full),
  concurrency, several processes on the same state, faults, malformed input, misuse. Keep going after the first
  class until new attempts stop finding new classes.
- First line: the most damaging class. Per class: concern id (or "NEW CONCERN: <name>"), every instance, a
  reproduction probe, a proposed class test and class-level fix. Known fixed classes are in your task — report one
  only if its fix is incomplete.

### Orchestrator (the agent running the acgd skill)
- Edits INTERFACES.md only via drafts in INTERFACES.proposed.md (semantic: + fresh review; bookkeeping: mechanical
  checks); decides every assumption and change request.
- Decisions and the user:
  - Authoritative: a user instruction overrides spec, plan and any decision; applied at the next step (amendment or
    process change; redirect or stop affected agents). "Ask the user:" in AGENTS.md changes only on the user's word.
  - Ask-points: a product decision (what the user sees or gets — incl. a merge disagreement about one and the
    details of a requested feature; a feature the user asked for is itself authorized, even one deleting data); a
    change weakening a user requirement; a correctness requirement that proves impossible or contradicts another;
    the quality-bar pick; accepting a bar miss; a bar item still beyond its hard limit after a redesign; a
    feature nobody asked for that deletes user data; an action that cannot be undone (deleting user data; changing
    anything outside the project other than the skill directory, the work directory `~/.acgd/<project>/`
    — acceptance tests, measurement scripts, counter-specs, drafts, researcher output, stamp files, reference
    systems —, a project virtualenv, temp directories); building the planned ("later") features once the rest is
    done; anything unclear. Example: "keep the last 7 daily backups" is authorized; automatic vs explicit pruning and
    what "daily" means are product decisions. Technical disagreements are yours to
    decide. At an ask-point read "Ask the user:" at the top of AGENTS.md (missing = no).
  - No → decide: the better option by the user's goals and requirements; between equally good options, the one that
    can be undone. Breaking a user requirement is only an alternative (a bar item missed within its hard
    limit is a reported miss, not a broken requirement); impossible — redesign still fails, reason stated — or
    contradictory correctness requirement → closest achievable semantics, stated exactly; beyond the hard limit after
    a redesign → reset target (semantic amendment of its bar row). Record ask-point decisions in STATUS.md "Decisions
    open to steer" (decision, alternatives, why, cost of changing; technical decisions: changelog only); continue.
    Nothing waits for the user.
  - Yes → ask; only that item waits.
  - A user decision replaces its "Decisions open to steer" entry; switching to yes re-asks nothing.
  - Never decided away while a fix is possible (only the user's word changes this): a failing correctness
    requirement, a bar item beyond its hard limit → fresh builder, then spec change or redesign.
- Writing code yourself (e.g. solo, Mode 2) → follow Writer / fixer for it; your own tests never verify your change;
  reviews stay fresh agents.
- Spawn every agent with its role line + brief; run all mechanical checks yourself after every writer run; never
  trust self-reports.
