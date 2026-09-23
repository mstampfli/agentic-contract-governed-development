import re
import os
B=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'skill', 'templates') + '/'
R=open(B+'rules.md').read()
def sec(name):
    m=re.search(r'^### '+re.escape(name)+r'.*?(?=^### |\Z)', R, re.M|re.S); return m.group(0).rstrip()
intro=R[R.index('Every agent is told'):R.index('### All roles')].rstrip()
body_all=R[R.index('Every agent is told'):].rstrip()
ALL,WR,RV,PR,RT=sec('All roles'),sec('Writer / fixer'),sec('Reviewer'),sec('Probes'),sec('Red teamer')
def swap(path, start_marker, new_block):
    u=open(path).read(); i=u.index(start_marker); j=u.index('\n\n', u.index('### ', i)) if False else None
    return u
# spec template: replace rules block (from '## Rules' heading to '## Failure model')
t=B+'INTERFACES.template.md'; u=open(t).read(); i=u.index('## Rules'); j=u.index('## Failure model')
u=u[:i]+'## Rules (verbatim copy of templates/rules.md — all roles; check with `spec_check.py rules INTERFACES.md`)\n'+body_all+'\n\n'+u[j:]
open(t,'w').write(u)
open(B+'AGENTS.md.template','w').write('''<!-- Copy to AGENTS.md in the project root (remove this comment), then: ln -s AGENTS.md CLAUDE.md
     (CLAUDE.md must be a symlink to AGENTS.md so the two can never drift; verified: the lazy CLAUDE.md load follows it).
     Without symlink support, copy AGENTS.md to CLAUDE.md after every change; spec_check.py all verifies they match. -->
# <project> — instructions for every agent

Ask the user: no
<!-- yes | no — changed only on the user's instruction. no: nothing waits for the user; decisions are listed in
     STATUS.md "Decisions open to steer". yes: the ask-points are asked. The rule: Orchestrator → "Decisions and the
     user" below. Either way the user's instructions override everything. -->

The spec is `INTERFACES.md` (binding; drafts under review are in `INTERFACES.proposed.md` — never implement them).
Ledgers: `QUESTIONS.md`, `ASSUMPTIONS.md`. Review and red-team probes: `tests_review/`. Concern catalog: `concerns.md`.
Live status (decisions open to steer, green state, quality-bar measurements, open questions, what is running, the
acceptance-test path): `STATUS.md`.
Process: the acgd skill at `<skill dir>` (SKILL.md; prompts from templates/*_brief.md; checks
`python3 <skill dir>/spec_check.py all INTERFACES.md ASSUMPTIONS.md` and `python3 <skill dir>/verify_citations.py .`).

'''+R.rstrip().replace('## Rules (canonical source)', '## Rules (verbatim copy of templates/rules.md — all roles)')+'\n')
def brief(path, head, sections, role_names):
    open(path,'w').write(head+'\nRules — verbatim from the rules at the top of INTERFACES.md. Follow '+role_names+' only:\n\n'+intro+'\n\n'+'\n\n'.join(sections)+'\n')
brief(B+'writer_brief.md','''Your role: writer <ID>. Project root: <absolute project root> (use absolute paths; stay inside it).
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
''',[ALL,WR],'"All roles" and "Writer / fixer"')
brief(B+'review_brief.md','''Your role: reviewer, kind <spec-change | module | seam | quality>, id <module id, seam A-B, "spec", component id or T<n>>.
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
  failure), and whether a fix broke anything else (after a simplification: nothing removed was needed by a spec
  entry, class test or acceptance test).
- seam <A-B>: [Re-review: previous findings <list>; diff: `diff -ru <snapshot dir> <files>`.] the code on BOTH sides; run them together; inject failures across the seam; what does each side believe
  afterwards?
- quality <component or T<n>>: [Re-review: previous findings <list>.] the spec's "User requirements" and "Quality bar" sections, <measurement commands>, <acceptance tests path>,
  <reference system and how to run it, or the path of its collected material, or "none">. Run every measured item (and on the reference system where runnable); judge every judged item
  by using the public interface as a user would. Report each item: met / below (by how much — within or beyond its
  hard limit —, why, the change that closes it, or "no change expected to help") / not built yet (what is missing and which planned component would provide it). Then simplifications:
  code traced to no spec entry, fixed class or acceptance test; duplication; handling of failures outside the failure
  model — each with the tests that show removing or merging it is safe.
<!-- Orchestrator (delete this comment before sending): fill the header lines and the scope line only (the same placeholders appear in the rules — leave those), keep
     only the scope line of this reviewer's kind, drop the [..] brackets on kept parts, delete bracketed parts that do
     not apply; keep the rules below verbatim. -->
''',[ALL,RV,PR],'"All roles", "Reviewer" and "Probes"')
brief(B+'redteam_brief.md','''Your role: red teamer, target <T<n> from the scope map> (= <components in the target>). Project root: <absolute project root>.
You wrote none of this. Read INTERFACES.md, ASSUMPTIONS.md and <absolute project root>/concerns.md, then the code.
How to run the target (you start, stop and kill it yourself, in a temp dir): <concrete commands, no placeholders>.
Known, already-fixed classes: <one line each: "<concern id> — <class name> — class test <path>", or "none">.
<!-- Orchestrator (delete this comment before sending): fill the header; keep the rules below verbatim. -->
''',[ALL,RT,PR],'"All roles", "Red teamer" and "Probes"')
