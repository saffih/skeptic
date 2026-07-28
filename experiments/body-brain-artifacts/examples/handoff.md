# Example metadata-only handoff

State: `experiments/body-brain-artifacts/examples/body-state.json`
Validator: `capabilities/body_state/body_state.py`

The handoff carries references only. It contains no report, log, diff, source excerpt, transcript, or reviewer reasoning. The receiving Body reads an artifact only when its `read_condition` is met and validates again before taking `NEXT_AUTHORIZED_ACTION`.
