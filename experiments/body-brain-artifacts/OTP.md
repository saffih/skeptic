# Optimized Task Prompt (OTP)

OTP is the recommended additive orchestration contract for routine repository work. It preserves the Task Prompt (TP) workflow and its existing behavior; a task selects OTP explicitly when it supplies an economy envelope.

## Economy contract

### Planning mode

Use exactly one of:

- `DETERMINISTIC` — no Brain invocation; execute from sufficient existing evidence and reusable procedure.
- `PLAN_ONCE` — at most one Brain invocation, followed by Body acceptance and execution of the sealed plan.
- `ESCALATED` — use only when explicitly authorized; record the authorization and the stronger route used.

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

## Execution order

Prefer, in order: deterministic execution; existing evidence; cached knowledge; a reusable procedure; one Brain planning pass; and a stronger model only after explicit authorization. Never consume reasoning budget when deterministic execution is sufficient.

## Acceptance

An OTP plan must satisfy the normal TP checks—task identity, required sections, completion marker, authorization, and mechanical executability—and must also fit the task's declared cost envelope. A technically executable plan that exceeds any authorized budget is rejected.

## Compatibility

TP remains supported. A task without an OTP contract follows the existing TP workflow and receipt fields; OTP adds budget and accounting fields without changing the Body, Brain, plan-sealing, or validation contracts.
