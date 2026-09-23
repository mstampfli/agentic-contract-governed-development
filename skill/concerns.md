# Concern catalog — kinds of cross-module problems to decide for every seam

Each entry: what goes wrong, and where it was observed. Add a row whenever a late finding fits no existing concern.

| Id | Concern | Question to answer for each seam | Observed |
|---|---|---|---|
| C1 | Data shape | Exact encoding, byte order, None vs empty, representation (raw/hex), one codec? | strata MVCC key; tinyq A duplicate record format |
| C2 | Limits & sizes | Max record / frame / batch / fetch on both sides — do they nest? | tinykv A, tinyq A (stuck consumer) |
| C3 | Error mapping | Which error class/code/message crosses the boundary, and what does the receiver infer from it? | tinyq V2-2/V12-4/V14-1 |
| C4 | Outcome reporting | After a failure: did it happen / not happen / unknown? Lost responses? Can the caller tell? | tinyq A (duplicates), V6-2/V12-3 |
| C5 | Crash & recovery | Torn writes, fsync ordering, what recovery keeps or truncates | tinyq V11-1 (data-loss draft) |
| C6 | Concurrency & locks | Who serialises what; lock order; thread-safety claims | tinyq V11-2, V16-5 |
| C7 | Process exclusivity | Several processes on the same state — prevented how? | tinyq B (two brokers, one data dir) |
| C8 | Resource lifecycle | Open / close / reopen / poison; who releases fds, temp files | tinyq V10-2, V12-1, stale fd |
| C9 | Validation ownership | Which side validates which input; is anything validated nowhere? | tinykv B (client int→bytes), tinyq V14-1 |
| C10 | Cancellation & interrupts | In scope or not; if in, exact semantics | tinyq V15 (should have been decided first) |
| C11 | Ordering & identity | Offsets, sequence numbers, ids: assigned where, monotonic, contiguous? | tinyq FMT-7 |
| C12 | Compatibility | On-disk / wire format versions, upgrades | — (not yet observed) |
| C13 | Trust boundary | Untrusted input from the network or files: sizes, paths, names; for browsers: origin (CORS/CSRF) and output escaping | tinyq topic names ".", ".." |
| C14 | Derived data & caches | Who updates or invalidates a cache / index / derived copy when its source changes; how stale may a reader see it? | — (found by the new-agent simulation) |
| C15 | Shared memory across processes / copies | Which ranges stay shared (MAP_SHARED, SysV shm, memfd) between processes or copies of one — can a write through one side reach the other; is a "copy" really independent? | pgit V0 review (fork keeps MAP_SHARED shared) |
