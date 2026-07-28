# Frozen migration manifest

Bound to repository `saffih/skeptic`, base commit `305fc1a33f4fd40e8db05eda3420c3991e09f66c`, base tree `20881bb258af2dd6c1f334f36b3d34b9344f76ff`. This file is frozen before structural mutation; its SHA-256 is recorded beside it.

| old path | classification | new path | import / command mapping | exposure |
|---|---|---|---|---|
| `agents/lead-agent-prompt.md` | role | `agents/lead_agent.md` | documentation references only | REPOSITORY_INTERNAL |
| `agents/boundary-agent.md` | role | `agents/boundary_agent.md` | documentation references only | REPOSITORY_INTERNAL |
| `agents/model-routing.md` | policy | `agents/model_routing_policy.md` | documentation references only | REPOSITORY_INTERNAL |
| `agents/agent-return.md` | contract | `agents/agent_return_contract.md` | documentation references only | REPOSITORY_INTERNAL |
| `agents/task-prompt.md` | workflow | `workflows/task_prompt.md` | documentation references only | DOCUMENTED_PUBLIC_INTERFACE |
| `agents/task-prompt-builder.md` | workflow | `workflows/task_prompt_builder.md` | documentation references only | DOCUMENTED_PUBLIC_INTERFACE |
| `agents/body-state.md` | capability contract | `capabilities/body_state/body_state.md` | `harness.body_state` -> `capabilities.body_state.body_state`; `python -m harness.body_state` -> `python -m capabilities.body_state.body_state` | REPOSITORY_INTERNAL |
| `harness/body_state.py` | implementation | `capabilities/body_state/body_state.py` | same as above | REPOSITORY_INTERNAL |
| `agents/checkpoint.md` | capability contract | `capabilities/immutable_checkpoint/immutable_checkpoint.md` | `harness.checkpoint` -> `capabilities.immutable_checkpoint.immutable_checkpoint` | REPOSITORY_INTERNAL |
| `harness/checkpoint.py` | implementation | `capabilities/immutable_checkpoint/immutable_checkpoint.py` | same as above | REPOSITORY_INTERNAL |
| `agents/resume.md` | capability contract | `capabilities/restart_admission/restart_admission.md` | `harness.resume` -> `capabilities.restart_admission.restart_admission`; CLI module follows move | REPOSITORY_INTERNAL |
| `harness/resume.py` | implementation | `capabilities/restart_admission/restart_admission.py` | same as above | REPOSITORY_INTERNAL |
| `agents/execution-envelope.md` | capability contract | `capabilities/execution_envelope/execution_envelope.md` | `harness.execution_envelope` -> `capabilities.execution_envelope.execution_envelope` | REPOSITORY_INTERNAL |
| `harness/execution_envelope.py` | implementation | `capabilities/execution_envelope/execution_envelope.py` | same as above | REPOSITORY_INTERNAL |
| `agents/focused-retrieval.md` | capability contract | `capabilities/focused_retrieval/focused_retrieval.md` | `harness.focused_retrieval` -> `capabilities.focused_retrieval.focused_retrieval` | REPOSITORY_INTERNAL |
| `harness/focused_retrieval.py` | implementation | `capabilities/focused_retrieval/focused_retrieval.py` | same as above | REPOSITORY_INTERNAL |
| `tests/test_body_state.py` | test | `tests/capabilities/body_state/test_body_state.py` | unittest discovery from `tests` | REPOSITORY_INTERNAL |
| `tests/test_checkpoint.py` | test | `tests/capabilities/immutable_checkpoint/test_immutable_checkpoint.py` | unittest discovery from `tests` | REPOSITORY_INTERNAL |
| `tests/test_resume.py` | test | `tests/capabilities/restart_admission/test_restart_admission.py` | unittest discovery from `tests` | REPOSITORY_INTERNAL |
| `tests/test_execution_envelope.py` | test | `tests/capabilities/execution_envelope/test_execution_envelope.py` | unittest discovery from `tests` | REPOSITORY_INTERNAL |
| `tests/test_focused_retrieval.py` | test | `tests/capabilities/focused_retrieval/test_focused_retrieval.py` | unittest discovery from `tests` | REPOSITORY_INTERNAL |

Examples and fixtures: capability-specific JSON examples currently under `experiments/body-brain-artifacts/examples/` are classified as examples and are moved only when direct ownership is established; unrelated benchmark fixtures remain unrelated. `harness/quickcompare.py` is an unrelated benchmark harness and is not moved. No known external consumer or required shim was found in the base repository scan.

Before-migration route allowlists and exact byte/character/line measurements are recorded in `CONTEXT-BEFORE.json` after this manifest is frozen. Unknown hidden runtime context is not measured.
