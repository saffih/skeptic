# Optimized Task Prompt (OTP)

OTP is the recommended additive orchestration contract for routine repository work. It preserves the Task Prompt (TP) workflow and its existing behavior; a task selects OTP explicitly when it supplies an economy envelope.

## Economy contract

### Planning mode

Use exactly one of:

- `PLAN_ONCE` — exactly one Brain invocation, followed by Body acceptance and execution of the sealed plan.
- `DETERMINISTIC` — compatibility label for a TP-style task that does not enter the OTP planning lifecycle. It is not an OTP execution path.
- `ESCALATED` — use only when explicitly authorized; it still uses exactly one Brain planning invocation and records the authorization and stronger route used.

### Agent budget

The task declares the maximum Brain invocations and the number of additional agents allowed. An omitted or unknown value is not permission to add agents. OTP-001 defaults to `maximum Brain invocations: 1` and `additional agents: 0`.

### Model budget

The task records the requested Body route, requested Brain route, maximum authorized route, and escalation policy. Requested and observed routes are separate facts. Escalation is prohibited unless the task explicitly authorizes it.

### Context budget

The task lists authoritative inputs. The Body reads those paths only, does not perform a broad repository scan or recursive discovery, and opens an additional path only when a specific implementation decision cannot be resolved from the authoritative inputs. Missing inputs remain explicit.

### Execution budget

The task may cap benchmark executions, QuickCompare executions, Skeptic reviews, and retries. The Body checks these limits before execution and records actual use. A zero limit means do not run that activity unless correctness cannot otherwise be established; if it is required, stop and record the insufficiency rather than silently exceeding the limit.

### Stop policy

Stop with an explicit status when:

- a budget is exhausted;
- required evidence is insufficient;
- a requested route is unavailable; or
- the requested work exceeds authorization.

Do not substitute a stronger model, add an agent, widen discovery, retry, or perform an unlisted validation activity. Record the reason and the evidence available at the stop.

## Planning and execution order

For OTP, invoke exactly one Brain during planning. The Brain produces both an Execution Plan and an Acceptance Plan. The Body verifies and seals both before execution; it must not substitute deterministic sufficiency for the required planning invocation.

After the plan is sealed, execute the ordered steps, run deterministic validation, and only then execute the declared final review mode. A stronger model is permitted only after explicit authorization.

## Acceptance

An OTP plan must satisfy the normal TP checks—task identity, required sections, completion marker, authorization, and mechanical executability—and must also fit the task's declared cost envelope. A technically executable plan that exceeds any authorized budget is rejected.

The Acceptance Plan is mandatory and must contain exactly one explicit value for each field:

```text
FINAL_REVIEW_REQUIRED: YES | NO
FINAL_REVIEW_MODE: NONE | BRAIN_REVIEW | RUN_SKEPTIC
FINAL_REVIEW_REASON: <required rationale>
VALIDATION_REQUIREMENTS: <deterministic validation required before final acceptance>
```

The Body seals the Acceptance Plan with the rest of the plan before execution. Execution cannot add, remove, or change its review mode. If execution discovers a condition requiring a different review strategy, it stops with `REPLAN_REQUIRED`; only a new Brain planning phase may authorize the change.

The lifecycle is fixed:

```text
exactly one Brain plan
  -> Body acceptance and seal
  -> execution
  -> deterministic validation
  -> STOP on validation failure, with no judgment review
  -> pre-authorized NONE, BRAIN_REVIEW, or exactly-once RUN_SKEPTIC
  -> Body final acceptance
  -> terminal receipt
```

`RUN_SKEPTIC` is never opportunistic and is never skipped when pre-authorized. Final acceptance always remains a Body responsibility and combines the execution receipt, deterministic validator receipt, and required final-review receipt.

## Compatibility

TP remains supported. A task without an OTP contract follows the existing TP workflow and receipt fields. OTP adds budget, Acceptance Plan, sealed-review, deterministic-validation, and final-acceptance fields without changing TP behavior.
