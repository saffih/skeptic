# Target Task Working-MVP Gap Closure

## Binding

- Starting commit: `6c7957e7599cd800f6f4d79c55fad807e1b50fcd`
- Starting tree: resolve and record during application before the first edit.
- Branch: `claude/target-task-system-replacement-et60rd`
- Pull request: `#22`
- Live paid provider smoke: not authorized by this implementation slice.

## Retained capabilities

The implementation reuses the current exact `TT:` mission persistence, private task root, immutable/content-addressed artifacts, append-only hash-chained ledger, sealed Plan identity, immutable cursor, operation admission and outcome correlation, host-receipt validation, focused retrieval, review-loop gates, candidate/remote manifests, and provider evidence adapters.

## Gaps closed

1. A sealed Plan receives one canonical, hash-bound executable companion. Each companion step carries only references, routing policy, authority, prohibitions, validation commands, and result rules. A minimal sealed Plan without this companion cannot be prepared for execution.
2. One thin controller exposes bootstrap, status, prepare, accept, advance, retry, stop, handoff, resume, and execution validation.
3. Ingress, dispatch, and return always pass through the existing store, runtime validation, and Boundary lifecycle functions.
4. Provider-neutral routing resolves canonical roles/model classes through adapter-owned aliases. Unsupported Lead routing returns `RELAUNCH_REQUIRED`; it never claims the top-level model changed.
5. A host-owned deterministic recorded launcher executes in CI, persists raw provider evidence and required outputs, and returns only a compact production receipt.
6. Controller projections are bounded and reject substantive body fields.
7. Optional focused retrieval runs behind the controller; its excerpt is persisted outside the Lead and only a reference returns.
8. The generic smoke performs two separately admitted, accepted, and advanced steps and truthfully stops at `STEP_VALIDATED`, not `CLOSED`.

## Minimal architecture

```text
Lead
  -> compact controller operation
Controller
  -> existing Boundary/store/runtime APIs
Boundary
  -> executable Plan companion + validated references + resolved route
Host launcher / Planner / Worker / Reviewer / Command
  -> durable outputs + raw provider evidence + compact canonical receipt
Boundary
  -> validate + persist + ledger/cursor transition
Controller
  -> compact reference-only projection
Lead
```

The sealed Plan remains the lifecycle identity. The executable companion is deterministically located at:

```text
plans/execution/<sealed-plan-sha256>.json
```

This avoids a second Plan, ledger, cursor, or orchestration engine.

## File ownership

- `concepts/target_task/executable_plan.py`: executable companion schema, binding, persistence, reference validation.
- `concepts/target_task/routing.py`: canonical route resolution only.
- `concepts/target_task/launcher.py`: host-owned invocation boundary and deterministic recorded host.
- `concepts/target_task/controller.py`: compact operational surface over existing lifecycle APIs.
- `concepts/target_task/boundary.py`: one exact-request recovery correction and one persisted retry wrapper.
- `adapters/*/adapter.py`: provider-owned concrete aliases and launch availability.
- `scripts/target_task.py`: CLI only.
- `scripts/generic_host_smoke.py`: credit-free lifecycle proof.
- tests: exact contracts and negative probes.

## Ordered slices

1. Add executable Plan companion and tests.
2. Add adapter-owned routing aliases and provider-neutral resolver.
3. Add recorded-host launcher.
4. Add Boundary exact-request recovery and persisted retry.
5. Add thin controller and CLI.
6. Replace schema-only smoke with two-step lifecycle proof.
7. Add negative probes and documentation.
8. Run deterministic verification.
9. Run full source-fresh RunSkeptic Fix Loop; restart after every change and require three unchanged qualifying passes.
10. Commit, push normally, update PR #22 truthfully. Do not merge or run paid live smoke in this slice.

## Invariants

- Mission, Plan, outputs, reviews, logs, transcripts, and excerpts never appear in durable Lead/controller returns.
- The ledger and cursor remain the only lifecycle state authorities.
- The executable companion is bound to the exact sealed Plan SHA and exact ordered Plan steps.
- Operation preparation is legal only from the latest durable `STEP_READY` cursor.
- A return is accepted only for the latest durable admitted operation and exact request embedded in dispatch evidence.
- Advancement consumes one validated `AWAITING_ADVANCE` operation exactly once.
- Retry is legal only from a durable `FAILED` operation.
- Timeout/indeterminate completion becomes `UNKNOWN` and cannot advance.
- Provider/model resolution is a route decision, not proof of execution. Actual routing is proven only by raw provider evidence bound into a routing-evidence artifact.
- `STEP_VALIDATED` is not `CLOSED`; final RunSkeptic, integration, and remote verification remain separate gates.
- Hidden host context isolation remains `UNKNOWN`.

## Negative probes

- sealed Plan without executable companion;
- missing instruction/output-contract reference;
- duplicate artifact reference ID/path;
- Plan/companion task, hash, order, objective, role, or success-criteria mismatch;
- task/source root confusion;
- stale operation, duplicate accept, duplicate advance, illegal retry;
- body-bearing or oversized controller receipt;
- arbitrary transcript text or synthetic receipt;
- role/provider/step/attempt mismatch;
- unavailable explicit provider;
- unavailable economical Lead route returns `RELAUNCH_REQUIRED`;
- timeout becomes `UNKNOWN`;
- wrong-task candidate/remote manifest and nonempty final-review `OPEN_ITEMS` remain blocked by existing gates;
- generic smoke must show exactly two separately accepted steps.

## Deterministic verification

```text
python3 -m compileall concepts/target_task adapters scripts tests
python3 -m unittest tests.concepts.target_task.test_executable_plan
python3 -m unittest tests.concepts.target_task.test_routing
python3 -m unittest tests.concepts.target_task.test_controller
python3 scripts/generic_host_smoke.py
python3 -m unittest discover -s tests -t .
bash -n scripts/target_task_smoke.sh
git diff --check
```

No live paid provider smoke is part of this deterministic proof.

## Terminal DONE

DONE requires the implementation, tests, generic lifecycle proof, full test suite, three source-fresh unchanged qualifying RunSkeptic passes, normal push, exact remote commit/tree verification, and current PR body. Until those publication and review gates pass, the state is resumable rather than complete.
