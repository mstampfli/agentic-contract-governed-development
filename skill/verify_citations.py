#!/usr/bin/env python3
"""Verify `Cite: <path>:<line> "<snippet>"` annotations point at real text.

usage: verify_citations.py <root> [--window N]
Skips snapshots/, prompts/, .git/, __pycache__/, node_modules/, virtualenv and tool caches, and the root files
QUESTIONS.md, ASSUMPTIONS.md, PROCESS.md, STATUS.md (snapshots, prompts, ledgers and the process log are history: their
citations are not kept current).
Paths in citations are relative to <root>. A citation passes if the snippet (whitespace-normalized)
occurs within +-N lines (default 3) of the cited line, or of the cited range `path:A-B`.
"""
import os, re, sys

CITE = re.compile(r'Cite:\s*([^\s:]+):(\d+)(?:-(\d+))?\s+"((?:[^"\\]|\\.)+)"')

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

HISTORY = {'QUESTIONS.md', 'ASSUMPTIONS.md', 'PROCESS.md', 'STATUS.md'}


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    root = sys.argv[1]
    win = int(sys.argv[sys.argv.index('--window') + 1]) if '--window' in sys.argv else 3
    cache, total, bad = {}, 0, []
    skip = {'snapshots', 'prompts', '.git', '__pycache__', 'node_modules', '.venv', 'venv', '.tox', '.mypy_cache', '.pytest_cache', 'target'}
    for dp, dns, fs in os.walk(root):
        dns[:] = [d for d in dns if d not in skip and not os.path.isfile(os.path.join(dp, d, 'pyvenv.cfg'))]  # any virtualenv
        for f in fs:
            if dp == root and f in HISTORY:
                continue  # ledgers and process log are history: citations there are not kept current
            p = os.path.join(dp, f)
            if f.endswith(('.pyc', '.png', '.jpg', '.gif', '.pdf', '.zip', '.gz', '.so', '.o', '.bin', '.lock')):
                continue
            for ln, line in enumerate(open(p, encoding='utf-8', errors='replace'), 1):
                for m in CITE.finditer(line):
                    total += 1
                    tpath, tline, snip = m.group(1), int(m.group(2)), norm(m.group(4).replace('\\"', '"'))
                    tend = max(tline, int(m.group(3) or tline))
                    full = os.path.join(root, tpath)
                    if full not in cache:
                        cache[full] = open(full, encoding='utf-8', errors='replace').read().split('\n') if os.path.isfile(full) else None
                    lines = cache[full]
                    where = f'{os.path.relpath(p, root)}:{ln}'
                    if lines is None:
                        bad.append(f'{where}: cited file missing: {tpath}')
                        continue
                    lo, hi = max(0, tline - 1 - win), min(len(lines), tend + win)
                    if snip not in norm(' '.join(lines[lo:hi])):
                        bad.append(f'{where}: snippet not found near {tpath}:{tline}: "{snip[:70]}"')
    print(f'citations: {total}  invalid: {len(bad)}')
    for b in bad:
        print('  ' + b)
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
