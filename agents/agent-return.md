# Agent Completion Envelope

The Agent Completion Envelope is a minimal correlation and transport-integrity check for delegated model-agent returns.

It can detect missing, mismatched, truncated, malformed, contradictory, or duplicate returns. It does not authenticate the agent and does not prove the work is correct.

## Dispatch

The Lead assigns a dispatch ID unique within the parent task and states the expected output and acceptance checks.

```text
dispatch_id: AG-004-7K2P
expected_output: patch
required_validation: focused tests
```

## Required return

```text
BEGIN_AGENT_RETURN
dispatch_id: AG-004-7K2P
status: COMPLETE
output: patch-inline
validation: PASS
blocker: NONE
END_AGENT_RETURN
```

Required fields: `dispatch_id`, `status`, `output`, `validation`, and `blocker`.

Allowed status values: `COMPLETE`, `PARTIAL`, `BLOCKED`, `FAILED`.

Allowed validation values: `PASS`, `FAIL`, `NOT_RUN`, `NOT_APPLICABLE`, `UNKNOWN`.

Optional fields: `changed`, `check`, `next`.

## Mechanical result

The deterministic checker returns one of:

- `AGENT_ENVELOPE_VALID`
- `AGENT_ENVELOPE_INVALID`
- `AGENT_RETURN_MISSING`
- `AGENT_RETURN_DUPLICATE`

A matching, structurally valid envelope is followed by role-specific acceptance:

- `DOWNSTREAM_WORK_ACCEPTED`
- `DOWNSTREAM_WORK_REJECTED`
- `DOWNSTREAM_WORK_UNVERIFIABLE`

`AGENT_ENVELOPE_VALID` never implies `DOWNSTREAM_WORK_ACCEPTED`.

Treat missing or mismatched dispatch identity, duplicate fields, unsupported values, truncation, duplicate envelopes, empty required output, `COMPLETE` with a blocker, and `COMPLETE` with `validation: FAIL` as invalid.

A deterministic tool may omit this model-agent envelope when the runtime already returns equivalent structured invocation identity, status, output, and error metadata. Record that exception.
