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
| C16 | Start-up & first actions | Who performs each component's first actions at power-on / load (schedules its first events, sets initial state), with which context, in which order — can a component that only reacts to events ever start? | nds r11 review (no device could schedule its first LCD event → the first frame never ends) |
| C17 | Pointer / handle validity across interfaces | Can a pointer, reference or handle obtained through an interface outlive its object, or be invalidated (moved, reborrowed, reallocated) by later calls on that interface — who guarantees its address and lifetime? | nds BASE r1 review (JIT keeps pointers to per-CPU slots and timing tables across later `&mut ctx` calls) |
| C18 | Duplicated logic | Do both sides of this seam (or any other module) each implement the same job — from a check or constant up to a whole mechanism (parser, auth / session manager, a type for the same concept) — instead of one registered home — same thing behaving differently per path, a fix needing every copy edited? Judged by job, not looks | tinyq A/B blind audits (high-severity duplication / inconsistency findings 6→3 / 5→2); unregistered convention → two exception types |
| C19 | Exact thresholds on accumulated floats | Does a threshold ("at least 1", "expires at tick T", "rounded down to ticks") compare a value built by repeated float arithmetic or by float conversion of a decimal (0.7 h × 60)? It can land a hair below the exact value and fire one step late or never — compute such values exactly (integers, fractions, the float's shortest decimal) | creature seam core r9 (sign budget 0.9999999999999999 at the exact refill tick; hours_to_ticks(0.7) = 41) |
