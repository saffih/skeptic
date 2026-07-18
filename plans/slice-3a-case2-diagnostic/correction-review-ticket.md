# Slice 3C — Independent Correction Review Dispatch Ticket

Canonical Dispatch Ticket (per `agents/task-prompt.md`). The reviewer
receives this ticket and the repository at the exact packet commit only.

Role:
Independent Correction Reviewer (fresh protected context; Claude, same
visible model label as Lead: claude-fable-5; same-model-family
limitation disclosed — independence is contextual, not model-diverse).

Objective:
Independently verify that the Slice 3C correction packet is correct,
complete, additive, and within its authorized boundary. Return a verdict.

Source of truth:
The repository working tree at the exact packet commit named in the
dispatch (HEAD must equal it; `git status` must be clean). Current
`skeptic.md`, `AGENTS.md`, `agents/lead-agent-prompt.md`,
`agents/task-prompt.md` at that commit. No chat history, no Lead
commentary, no unpushed state.

Scope:
`plans/slice-3a-case2-diagnostic/` and `plans/dogfood-log.md`, plus
read-only verification commands over the repository.

Allowed actions:
Read files; run read-only git commands (`status`, `rev-parse`, `log`,
`diff`, `ls-tree`, `cat-file`, `hash-object`, `merge-base`, `show`),
`sha256sum`, `rg`/`find` (excluding `.git/` and `analysis/`),
`python3 -m unittest discover -s tests`.

Forbidden actions:
Any file creation, edit, or deletion; any `git` mutation (add, commit,
push, switch, reset, clean, branch creation/deletion); any network
write; reading `.git/` internals beyond the listed commands; opening
`analysis/` if present.

Required checks:
1. Identity: HEAD equals the packet commit; working tree clean.
2. Immutability: the nine original Slice 3B files match commit
   29788a48eee3875485fbea6d17356a88d658ec9e byte-for-byte (blob
   equality via `git ls-tree` / `git hash-object`).
3. Dogfood log: original content (1,874 bytes, SHA-256
   395f51fd6cbf86ba254094d37cf11a12de02662b0decd9ff6351dcf78459ebca)
   is an exact byte prefix; exactly one bounded entry appended; Entry
   002 claims neither a third durable entry nor a proven single cause.
4. Changed-path allowlist: every path changed vs 29788a48 is in the
   Slice 3C authorized list (eight new correction files +
   `plans/dogfood-log.md` append); protected paths (`AGENTS.md`,
   `skeptic.md`, `agents/`, `tests/`, `harness/`, `analysis/`) unchanged.
5. `closure-correction.md`: identifies 29788a48; preserves valid
   recovery findings; supersedes the invalid `Overall DONE: yes`;
   records the push as unauthorized and that durability did not grant
   push authority; records current owner authorization to retain the
   diagnostic branch; establishes every Section 8 status; references
   `next-action-spec-v2.md`; states branch scope and `main` unchanged.
6. `next-action-spec-v2.md`: exact required title; 2 arms; 2 scenarios;
   3 fresh runs per cell; 12 total transcripts; S1 measurement of
   actual reads and operationalization; deterministic S2 requiring
   CONFLICT before child dispatch, child-output consumption, mutation,
   commit, push, or memory/substitute reconstruction; four separate
   scoring layers; Arm A not scored against wording it lacks;
   Judge-after-12-verified-packets custody; the ten invalidation rules;
   the decision boundary (no rescoring of Slice 3A, no Arm B promotion,
   no `main` change, no merge, no permanent doctrine); preconditions
   including owner authorization and attestation.
7. No Case 2R execution occurred; no Arm B runtime candidate file
   exists in the tree.
8. Tests: `python3 -m unittest discover -s tests` passes.
9. Word limits: closure correction <= 1,000 words; spec <= 2,500 words.
10. Disconfirming pass: actively look for any claim in the packet that
    could pass while wrong (e.g., a status asserted but not evidenced,
    a hash asserted but not reproducible).

Budget / context / output limit:
Single dispatch; receipt <= 1,200 words excluding compact tables.

Required evidence and durable destination:
Concrete observed values (SHAs, byte counts, test counts, command
results) inside the returned receipt. The Lead persists the verbatim
receipt to `correction-review-receipt.md`.

Acceptance and disconfirming checks:
Every required check above answered with observed evidence; at least
one genuine disconfirmation attempt reported.

Stop conditions:
HEAD/identity mismatch; dirty tree; any immutability or allowlist
failure; any forbidden action needed to proceed. On any stop, return
CONFLICT with the observed evidence; do not repair anything.

Return receipt:
Canonical Agent Receipt (per `agents/task-prompt.md`) ending with
exactly one verdict line: `Verdict: PASS`, `Verdict: ACTION — <items>`,
or `Verdict: CONFLICT — <reason>`, plus its own runtime model label and
an isolation statement (what it could and could not see).
