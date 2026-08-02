"""Canonical machine-readable STT Plan protocol (v25)."""
PLAN_SCHEMA = {
    "schema_version": 2,
    "delivery_kinds": {
        "inspect": {"mandatory_done": ["inventory_scope_completed", "report_bound_to_baseline", "mission_objective_satisfied", "final_find_loop_clean"]},
        "workspace_change": {"mandatory_done": ["all_declared_final_commands_succeeded", "changed_paths_bound_to_workspace", "mission_objective_satisfied", "final_find_loop_clean"]},
    },
    "step_kinds": ["change", "validation", "inspect", "task"],
    "reviewer_claim_ids": ["mission_objective_satisfied", "final_find_loop_clean", "report_bound_to_baseline"],
    "deterministic_predicate_ids": ["all_declared_final_commands_succeeded", "changed_paths_bound_to_workspace", "inventory_scope_completed"],
}
SCHEMA_VERSION = 2
