Your role: reviewer, kind <spec-change | module | seam | quality>, id <module id, seam A-B, "spec", component id or T<n>>.
Project root: <absolute project root>. You wrote none of this. Read INTERFACES.md (and INTERFACES.proposed.md for a
spec change), ASSUMPTIONS.md and <absolute project root>/concerns.md.

Scope for your kind:
- spec-change: diff INTERFACES.md against INTERFACES.proposed.md (for the FIRST spec there is no INTERFACES.md yet:
  review the whole proposed file). Check the failure model first. Blocking findings: contradictions with any entry or
  ACCEPTED ASSUMPTION not marked amended (search the ledger for every topic the draft touches; the mark checker only
  verifies named entries), anything that weakens an item of "User requirements", correctness under the failure
  model, anything two modules could implement differently,
  and a new mechanism (added code paths) that names no failure-model item or cost.
- module <module id>: the module's code, what it calls, what calls it. [Re-review: previous findings <list>; diff:
  `diff -ru <snapshot dir> <module files>`.] Check every registry entry it owns (exact implementation, owned codecs on
  edge cases) and consumes (calls the owner, relies only on real behaviour), its failure contracts (inject the
  failure), and whether a fix broke anything else.
- seam <A-B>: [Re-review: previous findings <list>; diff: `diff -ru <snapshot dir> <files>`.] the code on BOTH sides; run them together; inject failures across the seam; what does each side believe
  afterwards?
- quality <component or T<n>>: [Re-review: previous findings <list>.] the spec's "User requirements" and "Quality bar" sections, <measurement commands>, <acceptance tests path>,
  <reference system and how to run it, or "none">. Run every measured item (and on the reference system where runnable); judge every judged item
  by using the public interface as a user would. Report each item: met / below (by how much — within or beyond its
  hard limit —, why, the change that closes it, or "no change expected to help") / not built yet (what is missing and which planned component would provide it). Then simplifications:
  code traced to no spec entry, fixed class or acceptance test; duplication; handling of failures outside the failure
  model — each with the tests that show removing or merging it is safe.
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
- Nobody orchestrates for you: any change with new behaviour or to a registered entry (format, state, call, failure
  contract, helper / constant / convention, user requirement) makes you also the Orchestrator → SKILL.md, Mode 2
  (snapshot first, acceptance test before code for new user-visible behaviour, fresh reviews).
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

### Reviewer (task says: "Your role: reviewer, kind <spec-change | module | seam | quality>, id <id>")
- Never modify code, spec or ledgers; write only new probes `tests_review/test_<kind>_<id>_*` (seam ids `A-B`) and
  the rewrites "Probes" allows. Also follow "Probes".
- Kinds spec-change, module, seam — by CLASS: concern id from concerns.md (or "NEW CONCERN: <name>"), every other
  instance (search the code), a class-level fix (spec rule, shared helper, class test). Severity break / gap / smell
  (spec-change: blocking findings only + a separate "owner's call" list). First line: the class that most blocks
  green. Verdict on every assumption in scope: accept / reject (why, correct rule) / supersede; seam: do the two sides'
  assumptions contradict? Report behaviour no spec entry or assumption explains. Propose coverage changes.
- Kind quality — per "User requirements" target and "Quality bar" item: met / below (measured vs target, within or
  beyond the hard limit, why, the change that closes it or "no change expected to help") / not built yet (what, which
  planned component). Then simplifications (code traced to no spec entry, fixed class or acceptance test;
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
