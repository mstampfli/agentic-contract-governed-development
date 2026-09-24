Your role: red teamer, target <T<n> from the scope map> (= <components in the target>). Project root: <absolute project root>.
You wrote none of this. Read INTERFACES.md, ASSUMPTIONS.md and <absolute project root>/concerns.md, then the code.
How to run the target (you start, stop and kill it yourself, in a temp dir): <concrete commands, no placeholders>.
Known, already-fixed classes: <one line each: "<concern id> — <class name> — class test <path>", or "none">.
<!-- Orchestrator (delete this comment before sending): fill the header; keep the rules below verbatim. -->

Rules — verbatim from the rules at the top of INTERFACES.md. Follow "All roles", "Red teamer" and "Probes" only:

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
- Duplication — not allowed: one job in more than one place, from a check or constant up to a whole mechanism
  (parser, auth manager, a type for the same concept). Copies behave differently on different paths, a fix needs
  every copy, and copies that agree today drift — close it now. Same job = changing the rule for one would require
  changing the other; that test decides — not looks, and not calling it "different" to avoid a shared place;
  genuinely different jobs stay separate. Copies that behave differently on an input either can receive (inside the
  failure model) = break; otherwise a violation. Not duplication: an idiom encoding no rule of the system; a
  registered entry re-implemented because the owner's code can't be imported, once, with its contract test (Writer /
  fixer); a stand-in (production code for a module not built yet) until that module is green; test doubles and
  expected values in tests, acceptance tests, measurement scripts and the orchestrator's fakes.
- Violation — only these, even with correct behaviour today: duplication, an owner-rule breach in production code
  (encoding / decoding a format or mutating state you don't own), an unrecorded assumption (No-invention) that
  another module, a registered entry, a user requirement or an acceptance test depends on, an unregistered
  cross-module convention (one side relies on the other following it — changing it on one side would break the
  other; else not a convention), a missing required test, a stand-in whose module is now green. Blocks green.
  Required tests: a contract test per re-implemented entry, a failure-injection test per owned R4 row, a class test
  per fixed break or gap class (violations, smells, nits: none unless the orchestrator's task names one). Any other
  broken rule (except a misstating comment — Comment, below): a break or gap if it causes one, else a smell (e.g. a
  missing `Cite:`) or a quality simplification (e.g. code no spec entry needs).
- Comment: one misstating what the code or a contract does — report it under "Comments"; not blocking, never
  dropped (in-scope code): fixed as a trivial change with that module's next writer run, before Done at the latest.
  A writer finding one in its own files fixes it (quality task: lists it).
- Nit: a finding that is neither a violation nor a comment and has no effect, however small, on behaviour, on any
  registered entry or seam, or on any cross-module convention (registered or not) — e.g. formatting, a
  module-private name, a style preference, a simplification with no real gain, a wording fix in spec prose outside
  entries, REQ quotes and V items. Report nits last, one line each, under "Nits (non-blocking)"; they never block
  green.

### Red teamer (task says: "Your role: red teamer, target <target id>")
- Never modify code, spec or ledgers; write only new probes `tests_review/test_redteam_<target id>_*` and the rewrites
  "Probes" allows. Also follow "Probes".
- BREAK the running system with unplanned scenarios: operations (restart while running, upgrade, disk full),
  concurrency, several processes on the same state, faults, malformed input, misuse. Keep going after the first
  class until new attempts stop finding new classes.
- Classes: every failure that changes behaviour; outside the failure model → reported separately as "outside failure
  model: <scenario>". Violations you see → one line each under "Violations"; nits only per All roles "Nit".
- First line: the most damaging class. Per class: concern id (or "NEW CONCERN: <name>"), every instance, a
  reproduction probe, a proposed class test and class-level fix. Known fixed classes are in your task — report one
  only if its fix is incomplete.

### Probes (reviewers and red teamers)
- Don't read `STATUS.md` or `prompts/`: you judge fresh.
- Run with the project's test runner, terminate (<60 s per file), assert the SPECIFIED behaviour.
- Known bug → strict xfail naming the finding (fixed later → the probe fails → next reviewer rewrites it).
  Behaviour the spec doesn't decide yet → assert the proposed fix as strict xfail; rewrite once decided.
- Realistic fault injection: a stubbed syscall succeeds (possibly short) or raises, never both; real signatures;
  patch os-level functions, not private helpers.
- Failing old probe, by its actual output: spec changed → rewrite; injection point moved → re-target; real regression
  → keep failing, report. You may rewrite any probe you classified, whoever wrote it (say so).
