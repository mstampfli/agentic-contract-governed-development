"""Sweep aid: every clause of every registry entry that mentions a term, labelled by entry — one topic side by side,
to see a rule stated in two entries. It only shows where to read; it is never the sweep itself.
Usage: topic.py SPEC 'regex' [...]"""
import re, sys

ENTRY = re.compile(r"(?:\| |- \*\*|### )((?:HLP|EFF|FMT|CALL|REQ)-\d+|`[A-Za-z_.]+`|[A-Z][a-z ()/-]+?)[ *|]")


def registries(s):
    start = s.find("## Failure model")
    start = 0 if start < 0 else start
    end = re.search(r"^## (V\d+ |Changelog)", s[start:], re.M)
    body = s[start:start + end.start()] if end else s[start:]
    return re.sub(r"^## Coverage.*?(?=^## )", "", body, flags=re.M | re.S)   # coverage cells are pointers


def topic(spec, patterns):
    out, entry = [], "?"
    for line in registries(spec).split("\n"):
        m = ENTRY.match(line)
        if m:
            entry = m.group(1)
        for pat in patterns:
            for cl in re.split(r"; |\. (?=[A-Z])", line):
                if re.search(pat, cl):
                    out.append(f"[{entry}] {cl.strip()}")
    return out


if __name__ == "__main__":
    for l in dict.fromkeys(topic(open(sys.argv[1]).read(), sys.argv[2:])):
        print(l[:330])
