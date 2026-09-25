"""Sweep aid: clauses of the old spec's registries (Failure model .. before the first amendment / Changelog) whose
text no longer appears in the new spec — each one is reworded (check it still holds) or a rule that was lost.
It only shows where to read; it is never the sweep itself (rules.md → All roles "Sweep").
Usage: lost_clauses.py OLD NEW [min_words]"""
import re, sys


def registries(s):
    start = s.find("## Failure model")
    start = 0 if start < 0 else start
    end = re.search(r"^## (V\d+ |Changelog)", s[start:], re.M)
    return s[start:start + end.start()] if end else s[start:]


def norm(t):
    t = re.sub(r"\((amended|added) by[^)]*\)|\(reviewed in[^)]*\)|\bV\d+-\d+\b", " ", t.lower())
    return re.sub(r"[^a-z0-9]+", " ", t).split()


def lost(old, new, n=5):
    newn = " " + " ".join(norm(registries(new))) + " "
    out = []
    for line in registries(old).split("\n"):
        for cl in re.split(r"; |\. |\| | — ", line):
            w = norm(cl)
            if len(w) >= n and " " + " ".join(w) + " " not in newn:
                out.append(cl.strip())
    return out


if __name__ == "__main__":
    for cl in lost(open(sys.argv[1]).read(), open(sys.argv[2]).read(), int(sys.argv[3]) if len(sys.argv) > 3 else 5):
        print("-", cl[:400])
