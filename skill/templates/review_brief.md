Your role: reviewer, kind <spec-change | module | seam | quality>, id <module id, seam A-B, "spec", component id or T<n>>.
Project root: <absolute project root>. You wrote none of this. Read INTERFACES.md (and INTERFACES.proposed.md for a
spec change), ASSUMPTIONS.md and <absolute project root>/concerns.md.

Scope for your kind:
- spec-change: diff INTERFACES.md against INTERFACES.proposed.md (for the FIRST spec there is no INTERFACES.md yet:
  review the whole proposed file). Check the failure model first. Blocking findings: contradictions with any entry or
  ACCEPTED ASSUMPTION not marked amended (search the ledger for every topic the draft touches; the mark checker only
  verifies named entries), anything that weakens an item of "User requirements", correctness under the failure
  model, anything two modules could implement differently,
  a new mechanism (added code paths) that names no failure-model item or cost, and any violation (All roles: e.g. one
  rule defined in two entries, an unregistered cross-module convention). [Decide: <finding — the reason it is
  disputed>; your verdict stands.]
- module <module id>: the module's code, what it calls, what calls it. [Re-review: previous findings <list>; diff:
  `diff -ru <snapshot dir> <module files>`.] Check every registry entry it owns (exact implementation, owned codecs on
  edge cases) and consumes (calls the owner, relies only on real behaviour), its failure contracts (inject the
  failure), and whether a fix broke anything else (after a simplification: nothing removed was needed by a spec
  entry, class test or acceptance test). [Solo: the writer wrote the acceptance tests and measurement scripts at
  <path> — check that no code special-cases them.] [Brownfield: existing code without `Cite:` lines is not a
  finding.] [Decide: <finding — the reason it is disputed>; your verdict stands.] [Moved copy (brownfield): instead
  of the checks above, review only `diff -ru <snapshot dir> <files>` — the copy moved to its one home; a break, gap or
  violation you see elsewhere → report it; anything else outside the diff → not your task.]
- seam <A-B>: [Re-review: previous findings <list>; diff: `diff -ru <snapshot dir> <files>`.] the code on BOTH sides; run them together; inject failures across the seam; what does each side believe
  afterwards? [Decide: <finding — the reason it is disputed>; your verdict stands.]
- quality <component or T<n>>: [Re-review: previous findings <list>.] the spec's "User requirements" and "Quality bar" sections, <measurement commands>, <acceptance tests path>,
  <reference system and how to run it, or the path of its collected material, or "none">. Run every measured item (and on the reference system where runnable); judge every judged item
  by using the public interface as a user would. Report each item: met / below (by how much — within or beyond its
  hard limit —, why, the change that closes it, or "no change expected to help") / not built yet (what is missing and which planned component would provide it). Then simplifications:
  code traced to no spec entry, fixed class or acceptance test; handling of failures outside the failure model — each
  with the tests that show removing or merging it is safe.
<!-- Orchestrator (delete this comment before sending): fill the header lines and the scope line only (the same placeholders appear in the rules — leave those), keep
     only the scope line of this reviewer's kind, drop the [..] brackets on kept parts, delete bracketed parts that do
     not apply; keep the rules below verbatim. -->

Rules — verbatim from the rules at the top of INTERFACES.md. Follow "All roles", "Reviewer" and "Probes" only:

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

### Reviewer (task says: "Your role: reviewer, kind <spec-change | module | seam | quality>, id <id>")
- Never modify code, spec or ledgers; write only new probes `tests_review/test_<kind>_<id>_*` (seam ids `A-B`) and
  the rewrites "Probes" allows. Also follow "Probes".
- Kinds spec-change, module, seam — by CLASS: concern id from concerns.md (or "NEW CONCERN: <name>"), every other
  instance (search the code), a class-level fix (spec rule, shared helper, class test). Severity break (wrong
  behaviour) / gap (a case inside the failure model no entry or code handles; outside it → "outside failure model:
  <scenario>") / violation (All roles) / smell (none of these: a real but minor risk); nits → All roles "Nit"
  (spec-change: blocking findings only + a separate "owner's call" list + nits). First line: the class that most blocks
  green. Verdict on every assumption headed with a reviewed module's id (spec-change: every one the draft touches): accept / reject (why, correct rule) / supersede; seam: do the two sides'
  assumptions contradict? Report behaviour no spec entry or assumption explains. Propose coverage changes.
  Duplication: search the whole codebase for the same job, not only the seam.
- Kind quality — per "User requirements" target and "Quality bar" item: met / below (measured vs target, within or
  beyond the hard limit, why, the change that closes it or "no change expected to help") / not built yet (what, which
  planned component). Judged items by their stance: beat / match → run ours and the reference through the same
  scenario, say which is better or "tie" and the single biggest gap; differ → is ours distinct on each identity axis, and not
  worse on each floor axis; criterion → against the criterion. Then simplifications (code traced to no spec entry,
  fixed class or acceptance test; handling of failures outside the failure model), each with the tests showing it is
  safe; real gain = removes such code or a failure path, or measurably improves a bar item — else a nit. Violations
  you see (e.g. duplication) → listed separately under "Violations" (findings, not simplifications). No concern ids,
  severities or assumption verdicts. First line: the gap that most blocks the bar.

### Probes (reviewers and red teamers)
- Don't read `STATUS.md` or `prompts/`: you judge fresh.
- Run with the project's test runner, terminate (<60 s per file), assert the SPECIFIED behaviour.
- Known bug → strict xfail naming the finding (fixed later → the probe fails → next reviewer rewrites it).
  Behaviour the spec doesn't decide yet → assert the proposed fix as strict xfail; rewrite once decided.
- Realistic fault injection: a stubbed syscall succeeds (possibly short) or raises, never both; real signatures;
  patch os-level functions, not private helpers.
- Failing old probe, by its actual output: spec changed → rewrite; injection point moved → re-target; real regression
  → keep failing, report. You may rewrite any probe you classified, whoever wrote it (say so).
