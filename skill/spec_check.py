#!/usr/bin/env python3
"""Mechanical spec checks: six checks plus "all" (runs them together).

  spec_check.py marks    SPEC [SECTION]       every entry an amendment section names carries an in-place mark
                                              (SECTION defaults to the latest "## V<k>" section; skipped if none)
  spec_check.py ledger   SPEC LEDGER          every ledger assumption has a decision (accepted/rejected/superseded)
  spec_check.py acks     SPEC LEDGER          every writer listed in an amendment's "Affected:" line has ACKed it
  spec_check.py questions DIR|QUESTIONS.md   every "## Q-<id>-<n>" heading in QUESTIONS.md carries [ANSWERED V<k>] or [ANSWERED PROJ]
  spec_check.py coverage SPEC [CATALOG]       undecided concern x seam cells = what is not covered / needed next
                                              (CATALOG defaults to concerns.md next to SPEC, else the skill's copy)
  spec_check.py rules    FILE [RULES]         a prompt carries exactly its role's sections and no unfilled header
                                              placeholder (<...>, [optional line]); any other copy carries all;
                                              everything verbatim from templates/rules.md (placeholders unfilled);
                                              counter-specifier and researcher prompts: only their header is checked
  spec_check.py all      SPEC LEDGER          marks (every amendment section not headed "(superseded by V<k>)"), ledger, acks, questions (QUESTIONS.md next to SPEC),
                                              rules on SPEC, AGENTS.md and every prompts/*.md next to it, CLAUDE.md is a symlink to
                                              AGENTS.md; coverage printed, never fails

Ids: FMT-n (formats), EFF-n (state), CALL-n (calls), HLP-n (shared helpers, constants, conventions), REQ-n (user
     requirements, verbatim), R4[<call>] (failure-contract row whose first cell is the call,
     with or without backticks), V<k>-<n> (item n of amendment section "## V<k> <title>"),
     ASSUMPTION-<writer id>-<n> (writer id = module-table id: a letter, then letters, digits, _ — no hyphens,
     e.g. W3 or STORE).
marks:    "Adds: X" → X is defined outside the section with "(added by V<k>)". An amendment section names what it changes via "Touches: X, Y" / "amends X" / "supersedes X" / "replaces X". The line that
          DEFINES X elsewhere (its heading, bold bullet or table row) must mention the section (e.g. "amended by V4-2").
          Only NAMED entries can be checked — finding unnamed ones is the spec reviewer's job.
ledger:   ASSUMPTION-<id>-<n> is decided if a spec paragraph (a heading, bullet or table row with its wrapped
          continuation lines) mentions it in full (or a range "ASSUMPTION-W4-1 … W4-6"
          / "ASSUMPTION-W4-1 to ASSUMPTION-W4-6") together with
          accepted / rejected / superseded. The ledger heading must also carry the decision tag
          "[ACCEPTED V<k>]", "[REJECTED V<k>: ...]" or "[SUPERSEDED by ...]".
acks:     an amendment section's line "Affected: W1, STORE, ..." (comma-separated ids) requires "ACK V<k> <id>" in the ledger for each id
          ("Affected: none" = nobody).
coverage: section "## Coverage" = markdown table, first column concern id (C1…), other columns seams. A cell is an
          entry reference (covered), "out: <reason>", "n/a", or "open"/empty (reported). Catalog concerns without a
          row are reported too.
"""
import os, re, sys

def read(p):
    return open(p, encoding='utf-8').read() if os.path.isfile(p) else ''

def mentions(line, sec):
    # exact section id: V1 must not match V12-1
    return re.search(r'(?<![\w-])' + re.escape(sec) + r'(?!\d)', line) is not None

def latest_section(spec_path):
    secs = re.findall(r'^## (V\d+)\b(?!.*superseded by)', read(spec_path), re.M | re.I)
    return max(secs, key=lambda v: int(v[1:])) if secs else None

def in_superseded(lines, i):
    # is line i inside an amendment section headed "(superseded by V<k>)"? (its heading tag is its only mark)
    head = next((lines[j] for j in range(i, -1, -1) if lines[j].startswith('## ')), '')
    return re.match(r'## V\d+\b', head) is not None and re.search(r'superseded by', head, re.I) is not None

def marks(spec_path, sec=None):
    sec = sec or latest_section(spec_path)
    if sec is None:
        return []  # no amendment yet: nothing to check
    lines = read(spec_path).split('\n')
    start = next((i for i, l in enumerate(lines) if re.match(r'## ' + re.escape(sec) + r'\b', l)), None)
    if start is None:
        return [f'section "## {sec}" not found']
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith('## ')), len(lines))
    body = '\n'.join(lines[start:end])
    named, missing, calls = set(), [], set()
    for m in re.finditer(r'(?im)^\s*(?:[-*]\s*)?(?:\*\*V\d+-\d+\*\*\s*)?(?:amends|Touches|supersedes|replaces)\b:?([^\n]*)', body):
        named |= set(re.findall(r'\b(FMT-\d+|EFF-\d+|CALL-\d+|HLP-\d+|REQ-\d+|V\d+-\d+)\b', m.group(1)))
        calls |= set(re.findall(r'R4\[([^\]]+)\]', m.group(1)))  # Adds: lines are not changes to existing rows
        missing += [f'malformed id "{t}" in "{m.group(0).strip()[:60]}"' for t in
                    re.findall(r'(?i)\b(?:fmt|eff|call|hlp|req)[-_]?\d+\b', m.group(1))
                    if not re.fullmatch(r'(FMT|EFF|CALL|HLP|REQ)-\d+', t)]
    r4 = next((i for i, l in enumerate(lines) if re.match(r'## R4\b', l)), None)
    r4_end = next((i for i in range(r4 + 1, len(lines)) if lines[i].startswith('## ')), len(lines)) if r4 is not None else -1
    for call in calls:
        # only rows inside the "## R4" section: a component or target named like the call must not match
        rows = [i for i, l in enumerate(lines) if r4 is not None and r4 < i < r4_end
                and re.match(r'\|\s*`?' + re.escape(call) + r'`?[\s(|]', l)]
        if not rows:
            missing.append(f'R4[{call}]: row not found')
        else:  # every row of the call: an "(added by V<k>)" row must not hide an unmarked amended one
            missing += [f'R4[{call}]: row at line {i + 1} has no mark mentioning {sec}' for i in rows if not mentions(lines[i], sec)]
    for m in re.finditer(r'(?im)^\s*(?:[-*]\s*)?Adds:([^\n]*?)(?:Touches:.*)?$', body):  # new entries: defined + marked
        for ent in re.findall(r'\b((?:FMT|EFF|CALL|HLP|REQ)-\d+)\b', m.group(1)):
            pat = re.compile(r'(\*\*' + re.escape(ent) + r'\b|^#+ ' + re.escape(ent) + r'\b|^\| ' + re.escape(ent) + r'\b)')
            defs = [i for i, l in enumerate(lines) if pat.search(l) and not start <= i < end]
            if not defs:
                missing.append(f'{ent}: listed under Adds: but not defined')
            elif not any(mentions(lines[i], sec) for i in defs):
                missing.append(f'{ent}: added at line {defs[0] + 1} without "(added by {sec})"')
    for ent in sorted(e for e in named if not e.startswith(sec + '-')):
        pat = re.compile(r'(\*\*' + re.escape(ent) + r'\b|^#+ ' + re.escape(ent) + r'\b|^\| ' + re.escape(ent) + r'\b)')
        found = [i for i, l in enumerate(lines) if pat.search(l) and not start <= i < end]
        defs = [i for i in found if not in_superseded(lines, i)]
        if found and not defs:
            continue  # defined only in a superseded section: its heading tag is the mark
        if not defs:
            missing.append(f'{ent}: definition not found')
        elif not any(mentions(lines[i], sec) for i in defs):
            missing.append(f'{ent}: defined at line {defs[0] + 1} without a mark mentioning {sec}')
    return missing

def ledger(spec_path, ledger_path):
    led = read(ledger_path)
    ids = sorted(set(re.findall(r'ASSUMPTION-([A-Za-z][A-Za-z0-9_]*)-(\d+)(?![\w-])', led)), key=lambda t: (t[0], int(t[1])))
    paras, cur = [], []
    for raw in read(spec_path).split('\n'):
        if re.match(r'\s*([-*|]|#)', raw) and cur:
            paras.append(' '.join(cur)); cur = []
        cur.append(raw.strip())
    paras.append(' '.join(cur))
    decided = set()
    for p in paras:
        if not re.search(r'accepted|rejected|superseded', p, re.I):
            continue
        for w, a, b in re.findall(r'ASSUMPTION-([A-Za-z][A-Za-z0-9_]*)-(\d+)\s*(?:…|\.\.\.|to)\s*(?:ASSUMPTION-)?(?:[A-Za-z][A-Za-z0-9_]*-)?(\d+)', p):
            decided |= {(w, str(i)) for i in range(int(a), int(b) + 1)}
        decided |= set(re.findall(r'ASSUMPTION-([A-Za-z][A-Za-z0-9_]*)-(\d+)', p))
    out = [f'malformed ledger id "{b}" (writer id = a letter, then letters, digits, _; no hyphens)' for b in
           sorted({b.rstrip('-_') for b in re.findall(r'ASSUMPTION-[A-Za-z0-9_-]*', led)} - {f'ASSUMPTION-{w}-{n}' for w, n in ids})
           if not re.fullmatch(r'ASSUMPTION-[A-Za-z][A-Za-z0-9_]*-\d+', b)]
    out += [f'ASSUMPTION-{w}-{n}: no decision in the spec' for w, n in ids if (w, n) not in decided]
    for w, n in ids:
        head = re.search(r'^#+ .*ASSUMPTION-' + re.escape(w) + '-' + n + r'\b.*$', led, re.M)
        if head and not re.search(r'\[(ACCEPTED|REJECTED|SUPERSEDED)', head.group(0)) and not spec_path.endswith('.proposed.md'):
            out.append(f'ASSUMPTION-{w}-{n}: ledger heading has no [ACCEPTED|REJECTED|SUPERSEDED ...] tag')
    return out

def acks(spec_path, ledger_path):
    led, out = read(ledger_path), []
    for sec, head, body in re.findall(r'^## (V\d+)\b([^\n]*)(.*?)(?=^## |\Z)', read(spec_path), re.M | re.S):
        if re.search(r'superseded by', head, re.I):
            continue  # consolidated away: nobody ACKs a dead amendment
        m = re.search(r'Affected:\s*([^\n]+)', body)
        if not m or re.match(r'\s*(none|—|-)\s*\.?\s*$', m.group(1), re.I):
            continue
        ids = [t.strip().strip('.').strip() for t in re.sub(r'\([^)]*\)', '', m.group(1)).split(',')]
        out += [f'{sec}: malformed Affected entry "{i}" (use comma-separated writer ids)' for i in ids
                if i and not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', i)]
        for wid in [i for i in ids if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', i)]:
            if not re.search(r'ACK\s+' + sec + r'\s+' + re.escape(wid) + r'\b', led, re.I):
                out.append(f'{sec}: no "ACK {sec} {wid}" in the ledger')
    return out

def questions(qpath):
    heads = re.findall(r'^#+ .*\bQ-[^\s]*.*$', read(qpath), re.M)
    out = [f'malformed question id (writer ids start with a letter): {h.lstrip("# ").strip()}' for h in heads
           if not re.search(r'\bQ-[A-Za-z][A-Za-z0-9_]*-\d+\b', h)]
    return out + [f'unanswered: {h.lstrip("# ").strip()}' for h in heads
                  if re.search(r'\bQ-[A-Za-z][A-Za-z0-9_]*-\d+\b', h) and not re.search(r'\[ANSWERED (V\d+|PROJ)', h)]

def coverage(spec_path, catalog_path=None):
    project_cat = os.path.join(os.path.dirname(os.path.abspath(spec_path)), 'concerns.md')
    catalog_path = catalog_path or (project_cat if os.path.isfile(project_cat) else
                                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concerns.md'))
    catalog = re.findall(r'^\|\s*(C\d+)\s*\|\s*([^|]+)\|', read(catalog_path), re.M)
    m = re.search(r'^## Coverage[^\n]*\n(.*?)(?=^## |\Z)', read(spec_path), re.M | re.S)
    if not m:
        return ['no "## Coverage" section: every concern x seam is undecided']
    rows = [l for l in m.group(1).split('\n') if l.strip().startswith('|')]
    if len(rows) < 2:
        return ['"## Coverage" has no table: every concern x seam is undecided']
    seams = [c.strip() for c in rows[0].strip('|').split('|')][1:]
    ref = re.compile(r'(FMT-\d+|EFF-\d+|CALL-\d+|HLP-\d+|REQ-\d+|V\d+-\d+|R4\[[^\]]+\])')
    todo, seen = [], set()
    for r in rows[2:]:
        cells = [c.strip() for c in r.strip('|').split('|')]
        cid = cells[0].split()[0] if cells[0] else '?'
        seen.add(cid)
        for seam, cell in zip(seams, cells[1:] + [''] * len(seams)):
            low = cell.lower()
            if (low.startswith('out:') and len(cell) > 5) or low == 'n/a' or ref.search(cell):
                continue
            todo.append(f'{cid} x {seam}: {cell or "empty"}')
    return [f'{cid} ({name.strip()}): no row' for cid, name in catalog if cid not in seen] + todo

ROLE_SECTIONS = {'writer': ['All roles', 'Writer / fixer'],
                 'reviewer': ['All roles', 'Reviewer', 'Probes'],
                 'red teamer': ['All roles', 'Red teamer', 'Probes']}

def rules(path, rules_path=None):
    """A prompt/brief (has "Your role: <role>") must carry exactly its role's sections; any other file (spec,
    AGENTS.md) must carry the intro and every section. Each must match templates/rules.md verbatim."""
    rules_path = rules_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'rules.md')
    src, text, out = read(rules_path), read(path), []
    # <your id> stays unfilled; the work directory's <project> may be filled in (AGENTS.md is filled per project)
    norm = lambda x: re.sub(r'[^\s`(]*\.consistent-build/[^/\s`]+/', '~/.consistent-build/P/',
                            re.sub(r'<your id>|<ID>', '<id>', re.sub(r'\s+', ' ', x))).strip()
    secs = dict((h[4:].split(' (')[0], (h, b)) for h, b in re.findall(r'^(### [^\n]+)\n(.*?)(?=^### |\Z)', src, re.M | re.S))
    intro = src[src.index('Every agent is told'):src.index('### All roles')]
    role = re.search(r'^Your role:\s*(writer|reviewer|red teamer|counter-specifier|researcher)', text, re.M | re.I)
    tdir = os.path.dirname(os.path.abspath(rules_path))
    if role and os.path.dirname(os.path.abspath(path)) != tdir:
        # a filled prompt (not a template): none of its brief's own placeholders may be left above the rules.
        # Only the brief's own strings count, so quoted code or a verbatim request containing <...> passes.
        brief = {'writer': 'writer', 'reviewer': 'review', 'red teamer': 'redteam', 'counter-specifier': 'counterspec',
                 'researcher': 'researcher'}[role.group(1).lower()]
        tpl = re.sub(r'<!--.*?-->', '', read(os.path.join(tdir, brief + '_brief.md')).split('\nRules — verbatim')[0], flags=re.S)
        header = text.split('\nRules — verbatim')[0]
        # a placeholder counts only together with the template text right before it ("Project root: <absolute ...>"),
        # outermost <...> only, so nested ones and the same words in quoted content don't count
        left = set()
        for line in tpl.split('\n'):
            for m in re.finditer(r'<(?:[^<>\n]|<[^<>\n]*>)+>', line):
                ctx = line[max(0, m.start() - 15):m.end()]
                if ctx in header:
                    left.add(m.group(0))
            lab = re.match(r'\[[^\]\n]+\]', line)
            if lab and re.search(r'^' + re.escape(lab.group(0)), header, re.M):
                left.add(lab.group(0))
        out += [f'unfilled placeholder in the header: {p}' for p in sorted(left)]
        out += ['orchestrator comment ("<!-- Orchestrator ...") not deleted'] if '<!-- Orchestrator' in header else []
    if role and role.group(1).lower() in ('counter-specifier', 'researcher'):
        return out
    expected = ROLE_SECTIONS[role.group(1).lower()] if role else list(secs)
    if norm(intro) not in norm(text):
        out.append('intro ("Every agent is told its role…") missing or changed')
    for name, (head, body) in secs.items():
        m = re.search(r'^' + re.escape(head) + r'\n(.*?)(?=^### |^## |\Z)', text, re.M | re.S)
        if name in expected:
            if not m:
                out.append(f'section "{name}" missing')
            elif norm(m.group(1)) != norm(body):
                hint = ' (placeholders like <your id> must stay unfilled)' if '<your id>' in body and '<your id>' not in m.group(1) else ''
                out.append(f'section "{name}" differs from templates/rules.md{hint}')
        elif m:
            out.append(f'section "{name}" must not be in a {role.group(1)} prompt')
    return out

def report(name, problems):
    print(f'[{name}] {"OK" if not problems else str(len(problems)) + " open"}')
    for p in problems:
        print('  ' + p)
    return not problems

def main(a):
    need = {'questions': 2, 'marks': 2, 'ledger': 3, 'acks': 3, 'coverage': 2, 'rules': 2, 'all': 3}
    if not a or a[0] not in need or len(a) < need[a[0]]:
        print(__doc__); return 2
    if a[0] == 'marks':
        ok = report('marks', marks(a[1], a[2] if len(a) > 2 else None))
    elif a[0] == 'ledger':
        ok = report('ledger', ledger(a[1], a[2]))
    elif a[0] == 'acks':
        ok = report('acks', acks(a[1], a[2]))
    elif a[0] == 'questions':
        q = a[1] if a[1].endswith('.md') else os.path.join(a[1], 'QUESTIONS.md')
        ok = report('questions', questions(q))
    elif a[0] == 'rules':
        ok = report('rules', rules(a[1], a[2] if len(a) > 2 else None))
    elif a[0] == 'coverage':
        ok = report('coverage (= what is next)', coverage(a[1], a[2] if len(a) > 2 else None))
    else:
        if not os.path.isfile(a[1]):
            print(f'spec not found: {a[1]} (before the first merge, run on INTERFACES.proposed.md)'); return 1
        d = os.path.dirname(os.path.abspath(a[1]))
        # every amendment section, except ones whose heading says "(superseded by V<k>)" after a consolidation
        secs = sorted(set(re.findall(r'^## (V\d+)\b(?!.*superseded by)', read(a[1]), re.M | re.I)), key=lambda v: int(v[1:]))
        results = [report('marks (every amendment)', [f'{s}: {p}' for s in secs for p in marks(a[1], s)]), report('ledger', ledger(a[1], a[2])), report('acks', acks(a[1], a[2])),
                   report('questions', questions(os.path.join(d, 'QUESTIONS.md'))),
                   report('rules ' + os.path.basename(a[1]), rules(a[1]))]
        agents, claude = os.path.join(d, 'AGENTS.md'), os.path.join(d, 'CLAUDE.md')
        link = []
        if not os.path.isfile(agents):
            link.append('AGENTS.md missing next to the spec')
        else:
            results.append(report('rules AGENTS.md', rules(agents)))
            top = read(agents).split('\n## ')[0]  # the header above the rules; the rule text keeps its own <project>
            ask = re.search(r'^Ask the user:[ \t]*(\S*)', top, re.M)
            if ask and ask.group(1).lower() not in ('yes', 'no'):
                link.append(f'AGENTS.md: "Ask the user: {ask.group(1)}" must be yes or no (missing line = no)')
            link += [f'AGENTS.md: placeholder {p} not filled' for p in ('<project>', '<skill dir>') if p in top]
            if not os.path.lexists(claude):
                link.append('CLAUDE.md missing (ln -s AGENTS.md CLAUDE.md)')
            elif os.path.islink(claude):
                if os.path.realpath(claude) != os.path.realpath(agents):
                    link.append('CLAUDE.md is a symlink but not to AGENTS.md')
            elif read(claude) != read(agents):
                link.append('CLAUDE.md is a separate file and differs from AGENTS.md (make it a symlink: ln -sf AGENTS.md CLAUDE.md)')
        pdir = os.path.join(d, 'prompts')
        if os.path.isdir(pdir):  # saved prompts (*.md); SendMessage texts are saved as *.txt and not checked
            results.append(report('rules prompts/', [f'{f}: {p}' for f in sorted(os.listdir(pdir)) if f.endswith('.md')
                                                     for p in rules(os.path.join(pdir, f))]))
        results.append(report('AGENTS.md filled, CLAUDE.md -> AGENTS.md', link))
        report('coverage (= what is next; informational)', coverage(a[1]))
        ok = all(results)
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
