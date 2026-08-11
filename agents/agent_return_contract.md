# Agent Return Contract

## Purpose

This is the generic return/control interface between a bounded delegated
model-agent role and its parent control plane. It lets the parent determine,
without reading substantive work, which dispatch a return belongs to; whether
the invocation completed, partially completed, blocked, or failed; where its
durable result lives; what validation evidence accompanies it; whether a
blocker exists; and how to continue — whether continuation is already
host/control-fixed, or depends on semantic judgment that the delegated role
resolves by supplying `next`.

It does not make the parent understand substantive work. Substantive bodies
remain outside the parent's context and are referenced according to
`docs/context-rules.md`. A structurally valid envelope is not semantic
acceptance.

## Dispatch correlation

The parent assigns a `dispatch_id` unique within the parent task before
dispatch; the return carries the same `dispatch_id`. This contract owns only
that correlation. The objective, admitted references, authority,
prohibitions, requested route, expected result, and validation/acceptance
gates for the dispatch belong to the dispatching role's own contract (for
example `agents/lead_agent.md`) and are not duplicated here.

## Return envelope

```text
BEGIN_AGENT_RETURN
dispatch_id: AG-004-7K2P
status: COMPLETE
output: artifact-ref
validation: PASS
blocker: NONE
END_AGENT_RETURN
```

Required fields: `dispatch_id`, `status`, `output`, `validation`, `blocker`.

`status` is one of `COMPLETE`, `PARTIAL`, `BLOCKED`, `FAILED`. It reports only
whether the delegated invocation fulfilled its delegated execution
obligation — not whether any check it ran passed. A role can correctly
report `COMPLETE` while also reporting a failed check: a bounded test runner
that finishes running the requested suite is `COMPLETE` whether the suite
passed or failed.

`output` is a receiver-resolvable reference to the durable artifact, control
result, or bounded fact the invocation produced, per
`docs/context-rules.md`. Use the explicit value `NONE` only when the
invocation legitimately produced no durable result; an absent or empty
`output` is invalid rather than treated as "no output."

`validation` reports only what the delegated role itself ran and observed:
one of `PASS`, `FAIL`, `NOT_RUN`, `NOT_APPLICABLE`, `UNKNOWN`. It states the
reported outcome of the role's own checks, not semantic acceptance of the
work — a governing semantic authority may still reject `validation: PASS`
work, or accept work returned as `NOT_RUN`. `status` and `validation` are
reported independently: `status: COMPLETE` with `validation: FAIL` is a
normal, structurally valid combination — the invocation finished and the
checks it ran failed. The optional `evidence` field carries a
receiver-resolvable reference to the underlying validation record when one
exists.

`blocker` is `NONE` when nothing blocks the return, or a compact blocker fact
or receiver-resolvable reference when `status` is `BLOCKED`, `PARTIAL`, or
`FAILED`. It carries a fact, not an argument: reading it must not require the
parent to interpret substantive reasoning. Interpreting what a blocker means
for continuation is a semantic act performed by a bounded role, not the
parent.

Optional field: `evidence` (described above).

## Continuation

`next` is conditionally required.

It is required when the delegated role's semantic judgment determines what
should happen next, or when the parent would otherwise have to inspect
substantive output to choose the next action.

It may be absent when the return is terminal under already-fixed governing
control state — including a `BLOCKED` return the delegated role cannot
itself resolve, which leaves the parent's already-fixed stop-on-blocker rule
to apply — or when the next transition is completely host-fixed or
deterministic.

When present, `next` is either compact machine-followable control state, or a
receiver-resolvable reference to durable successor/control state that
identifies the intent it serves, per `durable-semantic-continuation` in
`docs/context-rules.md`. A successor reference tied to intent that has
since been superseded requires semantic rebinding before it may be used; this
contract does not itself decide staleness, only that the reference must carry
enough identity for that check to be made. `next` must not contain
substantive reasoning merely so the parent can understand it — supporting
semantic reasoning belongs in the durable artifact `next` references.

## Mechanical validity

A deterministic checker establishes only structural and correlation
validity. It returns one of:

- `AGENT_ENVELOPE_VALID`
- `AGENT_ENVELOPE_INVALID`
- `AGENT_RETURN_MISSING`
- `AGENT_RETURN_DUPLICATE`

Treat as invalid: missing or mismatched `dispatch_id`; a malformed or
duplicate envelope; duplicate fields; an unsupported enum value; `output`
absent or empty; `status: COMPLETE` combined with a non-`NONE` blocker;
`status` of `BLOCKED`, `PARTIAL`, or `FAILED` combined with `blocker: NONE`;
and truncation. `status: COMPLETE` combined with `validation: FAIL` is not on
this list — it is a structurally valid combination (see `status` and
`validation` above), not a protocol error.

The checker does not evaluate whether `output` is correct, whether
`validation` reflects real checks, or whether `next` names the right
successor. `AGENT_ENVELOPE_VALID` never implies the work is accepted.

## Semantic acceptance boundary

A valid envelope is a transport and correlation guarantee, not a judgment
about the work. Whether the returned work is accepted, rejected, or
unverifiable is a semantic outcome decided by the governing semantic
authority for that role's obligation, and is recorded there, not as a value
of this interface. A control plane such as `agents/lead_agent.md` may
orchestrate dispatching that decision to the governing semantic authority;
it does not itself define what acceptance means for an arbitrary role's
work.

## Equivalent deterministic returns

A deterministic runtime may omit the textual envelope only when its native
structured return already provides, with equivalent mechanical
observability, everything this contract requires for the circumstance at
hand: correlation, status, output, validation and blocker information, and
any `next` that this circumstance conditionally requires. It need not
duplicate a field that is legitimately not applicable to that return.

The exception applies only when the parent can map the native structure to
this contract's semantics by fixed, deterministic rule. If producing that
mapping requires semantic interpretation, the native return is not
mechanically equivalent and this exception does not apply. This exception
does not define, and must not be used to introduce, an alternate or
provider-specific return schema; it recognizes an existing deterministic
structure as already sufficient. Record that the exception was taken.
