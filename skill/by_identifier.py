"""Sweep aid: group every clause of every registry entry by each backticked identifier it mentions; the groups that
span two or more entries are the places a rule may be stated twice (read each: one statement, pointers elsewhere).
It only shows where to read; it is never the sweep itself (rules.md → All roles "Sweep").
Usage: by_identifier.py SPEC"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from topic import ENTRY, registries  # noqa: E402


def groups(spec):
    """{identifier: [(entry, clause), ...]} for identifiers mentioned by clauses of two or more entries."""
    out, entry = collections.defaultdict(list), "?"
    for line in registries(spec).split("\n"):
        m = ENTRY.match(line)
        if m:
            entry = m.group(1)
        for cl in re.split(r"; |\. (?=[A-Z])", line):
            for ident in set(re.findall(r"`([A-Za-z_][A-Za-z0-9_.]*)(?:\(|`)", cl)):
                out[ident].append((entry, cl.strip()))
    return {k: v for k, v in sorted(out.items()) if len({e for e, _ in v}) >= 2}


if __name__ == "__main__":
    for ident, cls in groups(open(sys.argv[1]).read()).items():
        print(f"=== {ident}  ({len({e for e, _ in cls})} entries)")
        for e, c in cls:
            print(f"  [{e}] {c[:230]}")
