from __future__ import annotations

DEFAULT_LIMITS = {
    "max_plan_steps": 12,
    "max_plan_candidates": 4,
    "max_plan_reviews": 10,
    "max_evidence_rounds_per_purpose": 3,
    "max_evidence_refs_per_round": 64,
    "max_evidence_bytes_per_round": 67108864,
    "max_final_find_reviews": 6,
    "max_workspace_bytes": 2147483648,
    "max_workspace_files": 200000,
    "max_single_file_bytes": 268435456,
    "max_scope_entries_per_step": 256,
    "max_read_scope_bytes_per_step": 67108864,
    "max_changed_paths_per_step": 256,
    "max_commands_per_change_step": 4,
    "max_total_commands": 24,
    "max_request_bytes": 524288,
    "max_semantic_result_bytes": 16777216,
    "max_command_log_bytes": 67108864,
    "max_semantic_operation_seconds": 1800,
    "max_task_depth": 4,
    "max_task_state_bytes": 8589934592,
    "min_free_space_reserve_bytes": 1073741824,
}

EVENT_TYPES = {
    "TASK_CREATED", "METHODOLOGY_BOUND", "INVENTORY_RECORDED", "TOOLCHAIN_BOUND",
    "EVIDENCE_BUNDLE_EXTENDED", "PLAN_CANDIDATE_RECORDED", "PLAN_REVIEW_RECORDED", "PLAN_BASELINE_SUPERSEDED",
    "PLAN_SEALED", "OPERATION_ADMITTED", "OPERATION_RESULT", "OPERATION_UNKNOWN", "TASK_BLOCKED_UNKNOWN",
    "VALIDATION_RECORDED", "FINAL_SUBJECT_FROZEN",
    "FINAL_REVIEW_RECORDED", "TERMINAL_RECEIPT_RECORDED", "INSPECTION_RECORDED", "TASK_BOUND", "TASK_RESULT_ACCEPTED",
}
