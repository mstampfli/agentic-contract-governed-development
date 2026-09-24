Your role: writer <ID>. Project root: <absolute project root> (use absolute paths; stay inside it).
Read INTERFACES.md fully, then the existing code of every module you depend on.
Task: <files / what to build or fix>. Project specifics: <language, allowed libraries, style, test runner — or "none">.
[Owner's calls:] Details left to you, decide each and record it as your ASSUMPTION: <list>.
[Fix task:] Findings to fix, each with its class: <list>.
[Quality task:] Quality-bar items below target (measured vs target; judged: stance and the single biggest gap) and accepted simplifications: <list>.
<!-- Orchestrator (delete this comment before sending): fill the header lines only; delete bracketed lines that do not
     apply and drop the brackets on the ones you keep ("[Fix task:]" → "Fix task:"); keep the rules below verbatim. To resume a writer after its question is answered, don't send this brief again: send
     "Question <Q-id> answered by amendment V<k>: re-read <entries>, ACK V<k>, continue" to the same agent with
     SendMessage; after a stop for a user
     change: "V<k> merged: re-read <entries>, ACK V<k>, continue <item>"; a first fix: "Fix task: <findings, each with its
     class>". -->

Rules — verbatim from the rules at the top of INTERFACES.md. Follow "All roles" and "Writer / fixer" only:

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
- Nit: a finding with no effect, however small, on behaviour, on any registered entry or seam, or on any cross-module
  convention (registered or not) — e.g. formatting, a module-private name, a style preference, a comment that
  misstates nothing, a simplification with no real gain, a wording fix in spec prose outside entries, REQ quotes and
  V items. (A comment misstating a contract is a smell.) Report nits last, one line each, under "Nits
  (non-blocking)"; they never block green and need no class test.

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
  each problem found is a class (fix + class test), a nit → fix or list it; a similar problem outside your files →
  list it in your reply; a spec gap → QUESTIONS.md / CHANGE REQUEST. Quality tasks (bar item below target,
  simplification): sweep findings are listed in your reply, not applied; no class test — the orchestrator measures;
  all existing tests still pass (strict-xfail probes of findings just fixed fail by design).
- Reply: files, questions/assumptions, change requests, classes and nits found by the sweep, the exact test command,
  line moves that stale others' citations.
