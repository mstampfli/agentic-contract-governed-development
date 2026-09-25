"""Regression tests for spec_check.py and verify_citations.py.
Every case comes from a real finding (review rounds 5-16). Run after EVERY script change:
    python3 -m pytest -q <skill dir>/tests/test_scripts.py
Each check is tested on a correct realistic input (must pass) AND a broken one (must fail)."""
import os, subprocess, sys, textwrap

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(SKILL, 'templates')


def run(tmp, *args, script='spec_check.py'):
    r = subprocess.run([sys.executable, os.path.join(SKILL, script), *args], cwd=tmp, capture_output=True, text=True)
    return r.returncode, r.stdout


def w(tmp, name, text):
    p = os.path.join(tmp, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(textwrap.dedent(text))
    return p


def project(tmp, fill=True):
    spec = open(os.path.join(T, 'INTERFACES.template.md')).read()
    w(tmp, 'INTERFACES.md', spec)
    a = open(os.path.join(T, 'AGENTS.md.template')).read().split('\n', 3)[3]
    if fill:
        a = a.replace('<project>', 'demo').replace('<skill dir>', '/skills/acgd')
    w(tmp, 'AGENTS.md', a)
    os.symlink('AGENTS.md', os.path.join(tmp, 'CLAUDE.md'))
    w(tmp, 'ASSUMPTIONS.md', '')


def filled(role_brief, header):
    t = open(os.path.join(T, role_brief)).read()
    return header + '\nRules — verbatim' + t.split('\nRules — verbatim', 1)[1]


# ---------------- marks ----------------
def test_marks_touches_line_is_read(tmp_path):  # r16: "\b after Touches:" silently skipped the line
    w(tmp_path, 'S.md', '# s\n**FMT-1** x\n## V1 a\nTouches: FMT-1.\n')
    assert run(tmp_path, 'marks', 'S.md')[0] == 1
    w(tmp_path, 'S.md', '# s\n**FMT-1** x (amended by V1-1)\n## V1 a\nTouches: FMT-1.\n')
    assert run(tmp_path, 'marks', 'S.md')[0] == 0


def test_marks_touches_affected_same_line(tmp_path):
    w(tmp_path, 'S.md', '# s\n**EFF-2** x\n## V3 a\nTouches: EFF-2. Affected: W1.\n')
    assert 'EFF-2' in run(tmp_path, 'marks', 'S.md')[1]


def test_marks_prose_replaces_ignored(tmp_path):  # r15: quoted "replaces" is not a reference
    w(tmp_path, 'S.md', '# s\n**FMT-2** x\n## V1 a\n- **V1-1** accepted verbatim: "decoder replaces bad bytes as FMT-2 says"\nTouches: none.\n')
    assert run(tmp_path, 'marks', 'S.md')[0] == 0


def test_marks_item_supersedes(tmp_path):
    w(tmp_path, 'S.md', '# s\n**FMT-2** x\n## V1 a\n- **V1-1** supersedes FMT-2.\n')
    assert run(tmp_path, 'marks', 'S.md')[0] == 1


def test_marks_capital_amends_and_malformed(tmp_path):  # r14
    w(tmp_path, 'S.md', '# s\n**FMT-2** x (amended by V1)\n## V1 a\nAmends FMT-2, FMT_3, fmt3, EFF3.\n')
    out = run(tmp_path, 'marks', 'S.md')[1]
    assert 'FMT_3' in out and 'fmt3' in out and 'EFF3' in out and 'FMT-2:' not in out


def test_marks_v1_not_v12(tmp_path):
    w(tmp_path, 'S.md', '# s\n**FMT-1** x (amended by V12-1)\n## V1 a\nTouches: FMT-1.\n')
    assert run(tmp_path, 'marks', 'S.md', 'V1')[0] == 1


def test_marks_r4_only_in_r4_section_and_every_row(tmp_path):  # r8, r10
    w(tmp_path, 'S.md', """\
        # s
        ## Scope map
        | build | BUILD | now (V1) |
        ## R4 Failure contracts
        | `build` | crash | x |
        | `build` (added by V1) | full | y |
        ## V1 a
        Touches: R4[build].
        """)
    out = run(tmp_path, 'marks', 'S.md')[1]
    assert 'row at line 5' in out and 'line 6' not in out


def test_marks_adds_r4_is_not_a_change(tmp_path):  # r12
    w(tmp_path, 'S.md', '# s\n## R4 x\n| `get` | a |\n| `get` (added by V2) | b |\n## V2 t\nAdds: R4[get] new row. Touches: none.\n')
    assert run(tmp_path, 'marks', 'S.md')[0] == 0


def test_marks_superseded(tmp_path):  # r11, r13
    w(tmp_path, 'S.md', '# s\n**FMT-1** x\n## V1 a\nTouches: FMT-1.\n## V2 b (superseded by V3)\nTouches: FMT-1.\n')
    assert 'V1' in run(tmp_path, 'marks', 'S.md')[1]  # latest live section is V1
    w(tmp_path, 'S.md', '# s\n## V1 a (superseded by V2)\n- **V1-1** x\n## V2 b\nsupersedes V1-1. Touches: none.\n')
    assert run(tmp_path, 'marks', 'S.md')[0] == 0


# ---------------- ledger / acks / questions ----------------
def test_ledger_decisions_and_tags(tmp_path):
    w(tmp_path, 'S.md', 'ASSUMPTION-W1-1 accepted.\nASSUMPTION-W2-1 … W2-3 rejected.\n')
    w(tmp_path, 'A.md', '## ASSUMPTION-W1-1 [ACCEPTED V1] — a\n## ASSUMPTION-W2-1 [REJECTED V1: x] — b\n'
                        '## ASSUMPTION-W2-2 [REJECTED V1: x] — c\n## ASSUMPTION-W2-3 [REJECTED V1: x] — d\n')
    assert run(tmp_path, 'ledger', 'S.md', 'A.md')[0] == 0
    w(tmp_path, 'A.md', '## ASSUMPTION-W1-1 — a\n')
    assert run(tmp_path, 'ledger', 'S.md', 'A.md')[0] == 1


def test_ledger_prose_word_is_not_a_decision(tmp_path):  # r9
    w(tmp_path, 'S.md', '| `put` | rejected API-1 | x |\n')
    w(tmp_path, 'A.md', '## ASSUMPTION-API-1 — x\n')
    assert 'ASSUMPTION-API-1: no decision' in run(tmp_path, 'ledger', 'S.md', 'A.md')[1]


def test_ledger_punctuation_and_malformed(tmp_path):  # r12, r13, r15
    w(tmp_path, 'S.md', 'ASSUMPTION-W2-3 accepted\n')
    w(tmp_path, 'A.md', "## ASSUMPTION-W2-3 [ACCEPTED V1] — see ASSUMPTION-W2-3's note, (ASSUMPTION-W2-3), ASSUMPTION-W2-3—x.\n")
    assert run(tmp_path, 'ledger', 'S.md', 'A.md')[0] == 0
    w(tmp_path, 'A.md', '## ASSUMPTION-W-4-3 — x\n## ASSUMPTION-3W-1 — y\n')
    out = run(tmp_path, 'ledger', 'S.md', 'A.md')[1]
    assert 'ASSUMPTION-W-4-3' in out and 'ASSUMPTION-3W-1' in out and 'ASSUMPTION-W-4:' not in out


def test_ledger_proposed_tolerates_missing_tags(tmp_path):  # r15
    w(tmp_path, 'INTERFACES.proposed.md', 'ASSUMPTION-CLI-1 accepted\n')
    w(tmp_path, 'A.md', '## ASSUMPTION-CLI-1 — x\n')
    assert run(tmp_path, 'ledger', 'INTERFACES.proposed.md', 'A.md')[0] == 0


def test_acks(tmp_path):
    w(tmp_path, 'S.md', '## V1 a\nAffected: W1, W2 (consumer).\n## V2 b (superseded by V3)\nAffected: W9.\n## V3 c\nAffected: none.\n')
    w(tmp_path, 'A.md', 'ACK V1 W1\nACK V1 W2\n')
    assert run(tmp_path, 'acks', 'S.md', 'A.md')[0] == 0
    w(tmp_path, 'A.md', 'ACK V1 W1\n')
    assert 'ACK V1 W2' in run(tmp_path, 'acks', 'S.md', 'A.md')[1]
    w(tmp_path, 'S.md', '## V1 a\nAffected: W-2.\n')
    assert 'malformed' in run(tmp_path, 'acks', 'S.md', 'A.md')[1]


def test_questions(tmp_path):
    w(tmp_path, 'QUESTIONS.md', '## Q-W1-1 [ANSWERED V0] — a\n## Q-PROJ-1 [ANSWERED V2] — b\n')
    assert run(tmp_path, 'questions', '.')[0] == 0
    w(tmp_path, 'QUESTIONS.md', '## Q-W1-1 — open\n## Q-3W-1 — bad\n')
    out = run(tmp_path, 'questions', 'QUESTIONS.md')[1]
    assert 'unanswered: Q-W1-1' in out and 'malformed' in out


def test_coverage_no_table(tmp_path):  # r8
    w(tmp_path, 'S.md', '## Coverage\nno table yet\n')
    assert 'no table' in run(tmp_path, 'coverage', 'S.md')[1]


# ---------------- rules / prompts ----------------
def test_templates_pass_rules():
    for f in os.listdir(T):
        assert subprocess.run([sys.executable, os.path.join(SKILL, 'spec_check.py'), 'rules', os.path.join(T, f)],
                              capture_output=True).returncode == 0, f


def test_filled_prompts_with_code_pass(tmp_path):  # r14, r15: quoted code / verbatim requests are not placeholders
    w(tmp_path, 'prompts/writer_CLI_r2.md', filled('writer_brief.md',
      'Your role: writer CLI. Project root: /p (use absolute paths; stay inside it).\n'
      'Read INTERFACES.md fully, then the existing code of every module you depend on.\n'
      'Task: fix cli.py. Project specifics: Python 3.13, pytest.\n'
      "Fix task: C9 — `if len(v) < 0 and x > 2` returns -> None for <empty> input (class: missing validation).\n"
      "Owner's calls: retry count.\n"))
    assert run(tmp_path, 'rules', 'prompts/writer_CLI_r2.md')[0] == 0
    c = open(os.path.join(T, 'counterspec_brief.md')).read()
    c = c.replace("<the user's request verbatim, including any stated future plans; nothing added by the orchestrator>",
                  'A tool with <table> views and a -> b pipes')
    c = c.replace('<~/.acgd/<project>/counterspec_<A|B>_r<N>.md (absolute path)>', '/w/counterspec_A_r1.md')
    c = '\n'.join(l for l in c.split('\n') if not l.startswith('[The existing system offers'))
    w(tmp_path, 'prompts/counterspec_A_r1.md', c)
    assert run(tmp_path, 'rules', 'prompts/counterspec_A_r1.md')[0] == 0


def test_unfilled_prompts_fail(tmp_path):
    w(tmp_path, 'prompts/writer_W1_r1.md', open(os.path.join(T, 'writer_brief.md')).read())
    assert run(tmp_path, 'rules', 'prompts/writer_W1_r1.md')[0] == 1
    w(tmp_path, 'prompts/writer_W1_r2.md', filled('writer_brief.md',
      'Your role: writer W1. Project root: /p.\nTask: x.\n[Fix task:] Findings to fix, each with its class: a.\n'))
    assert '[Fix task:]' in run(tmp_path, 'rules', 'prompts/writer_W1_r2.md')[1]
    w(tmp_path, 'prompts/writer_W1_r3.md', filled('writer_brief.md', 'Your role: writer W1. Project root: /p.\nTask: x.\n')
      .replace('- Owner rule', '- Owner rule!'))
    assert 'differs' in run(tmp_path, 'rules', 'prompts/writer_W1_r3.md')[1]
    w(tmp_path, 'prompts/writer_W1_r4.md', filled('writer_brief.md', 'Your role: writer W1. Project root: /p.\nTask: x.\n')
      .replace('<your id>', 'W1'))
    assert 'placeholders like <your id>' in run(tmp_path, 'rules', 'prompts/writer_W1_r4.md')[1]


# ---------------- all ----------------
def test_all_filled_project_passes_with_and_without_prompts(tmp_path):  # r14: AGENTS checks without prompts/
    project(tmp_path)
    assert run(tmp_path, 'all', 'INTERFACES.md', 'ASSUMPTIONS.md')[0] == 0
    os.makedirs(tmp_path / 'prompts')
    w(tmp_path, 'prompts/writer_W1_r1.txt', 'Question Q-W1-1 answered by amendment V1: ...')  # .txt not checked
    assert run(tmp_path, 'all', 'INTERFACES.md', 'ASSUMPTIONS.md')[0] == 0


def test_all_agents_problems_without_prompts_dir(tmp_path):
    project(tmp_path, fill=False)
    os.remove(tmp_path / 'CLAUDE.md')
    a = (tmp_path / 'AGENTS.md').read_text().replace('Ask the user: no', 'Ask the user: maybe')
    (tmp_path / 'AGENTS.md').write_text(a)
    out = run(tmp_path, 'all', 'INTERFACES.md', 'ASSUMPTIONS.md')[1]
    assert 'maybe' in out and '<project> not filled' in out and 'CLAUDE.md missing' in out


def test_all_absolute_workdir_in_agents(tmp_path):  # r13, r14
    project(tmp_path)
    a = (tmp_path / 'AGENTS.md').read_text().replace('~/.acgd/demo/', '/home/u/.acgd/demo/')
    (tmp_path / 'AGENTS.md').write_text(a)
    assert run(tmp_path, 'all', 'INTERFACES.md', 'ASSUMPTIONS.md')[0] == 0


def test_all_symlink_and_copy(tmp_path):
    project(tmp_path)
    os.remove(tmp_path / 'CLAUDE.md')
    (tmp_path / 'CLAUDE.md').write_text('different')
    assert 'differs' in run(tmp_path, 'all', 'INTERFACES.md', 'ASSUMPTIONS.md')[1]


def test_all_missing_spec(tmp_path):
    out = run(tmp_path, 'all', 'INTERFACES.md', 'ASSUMPTIONS.md')
    assert out[0] == 1 and 'spec not found' in out[1]


# ---------------- verify_citations ----------------
def test_citations(tmp_path):
    w(tmp_path, 'a.py', 'a\nb\nc\nd\ne\nf\ng\nh\ni\nj\nTARGET\n')
    w(tmp_path, 'b.py', '# Cite: a.py:1-11 "TARGET"\n# Cite: a.py:9 "TARGET"\n')
    assert run(tmp_path, '.', script='verify_citations.py')[0] == 0
    w(tmp_path, 'c.py', '# Cite: a.py:1 "TARGET"\n')
    assert run(tmp_path, '.', script='verify_citations.py')[0] == 1


def test_citations_skips_history_and_venvs(tmp_path):
    for f in ('ASSUMPTIONS.md', 'QUESTIONS.md', 'PROCESS.md', 'STATUS.md', 'prompts/x.md', 'snapshots/s/y.py',
              'env/z.py', '.venv/q.py', 'target/doc/src/x.rs.html'):  # nds: rustdoc HTML of cited comments
        w(tmp_path, f, '# Cite: nowhere.py:1 "x"\n')
    w(tmp_path, 'env/pyvenv.cfg', '')
    assert run(tmp_path, '.', script='verify_citations.py')[0] == 0


def test_filled_prompts_quoting_template_words_pass(tmp_path):  # r16: <item>, <summary>, <project> in real content
    w(tmp_path, 'prompts/writer_W1_r1.md', filled('writer_brief.md',
      'Your role: writer W1. Project root: /p (use absolute paths; stay inside it).\n'
      'Read INTERFACES.md fully, then the existing code of every module you depend on.\n'
      'Task: emit one <item> per entry; see <details><summary>x</summary></details> and <project>/data.\n'
      'Project specifics: Python.\n'))
    assert run(tmp_path, 'rules', 'prompts/writer_W1_r1.md')[0] == 0


def test_partly_filled_prompt_fails(tmp_path):
    w(tmp_path, 'prompts/writer_W1_r1.md', filled('writer_brief.md',
      'Your role: writer W1. Project root: <absolute project root> (use absolute paths; stay inside it).\nTask: x.\n'))
    assert '<absolute project root>' in run(tmp_path, 'rules', 'prompts/writer_W1_r1.md')[1]


def test_questions_answered_proj(tmp_path):  # r16: PROJ changes need no amendment
    w(tmp_path, 'QUESTIONS.md', '## Q-W1-1 [ANSWERED PROJ] — add pytest-timeout to the test config\n')
    assert run(tmp_path, 'questions', '.')[0] == 0


def test_marks_req_ids(tmp_path):  # r16: user requirements have ids
    w(tmp_path, 'S.md', '# s\n- **REQ-2** "exports round to 6 minutes"\n## V2 a\nTouches: REQ-2, req3.\n')
    out = run(tmp_path, 'marks', 'S.md')[1]
    assert 'REQ-2: defined' in out and 'req3' in out


def test_marks_adds_checked(tmp_path):  # r18: Adds: entries were never checked
    w(tmp_path, 'S.md', '# s\n**HLP-4** x (added by V1)\n## V1 a\nAdds: HLP-4. Touches: none.\n')
    assert run(tmp_path, 'marks', 'S.md')[0] == 0
    w(tmp_path, 'S.md', '# s\n## V1 a\nAdds: HLP-4, FMT-9. Touches: none.\n**FMT-9** y\n')
    out = run(tmp_path, 'marks', 'S.md')[1]
    assert 'HLP-4: listed under Adds: but not defined' in out
    w(tmp_path, 'S.md', '# s\n**FMT-9** y\n## V1 a\nAdds: FMT-9.\n')
    assert '(added by V1)' in run(tmp_path, 'marks', 'S.md')[1]


def _load(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), '..', name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V0 = "# INTERFACES\n## Failure model\n| a | b |\n## R3 Cross-module calls\n- **CALL-1** `f()` — the snapshot is taken every ten ticks; errors raise ValueError.\n## Changelog\n- V0\n"


def test_lost_clauses_on_a_v0_spec_and_a_moved_rule():  # crashed without a "## V1" section
    lc = _load('lost_clauses')
    new = V0.replace("the snapshot is taken every ten ticks; ", "") + "## V1 x\n"
    assert lc.lost(V0, V0) == []
    assert lc.lost(V0, new) == ["the snapshot is taken every ten ticks"]


def test_topic_on_a_v0_spec_labels_the_entry():
    tp = _load('topic')
    assert tp.topic(V0, ["snapshot"]) == ["[CALL-1] - **CALL-1** `f()` — the snapshot is taken every ten ticks"]


def test_by_identifier_groups_a_rule_stated_in_two_entries():
    bi = _load('by_identifier')
    spec = V0.replace("## Changelog", "- **CALL-2** `g()` — when `f` fails it retries; errors raise ValueError.\n## Changelog")
    g = bi.groups(spec)
    assert set(g) == {"f"} and {e for e, _ in g["f"]} == {"CALL-1", "CALL-2"}
