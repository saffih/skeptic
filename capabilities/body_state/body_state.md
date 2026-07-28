# Metadata-only Body state

The canonical Body state is UTF-8 canonical JSON with exactly one final LF and a maximum serialized size of 32,768 bytes. It has exactly: `TASK_ID`, `SEALED_PLAN_REFERENCE`, `SEALED_PLAN_SHA256`, `CURRENT_STEP`, `COMPLETED_STEP_IDS`, `VALIDATED_FACTS`, `OPEN_BLOCKERS`, `ARTIFACT_REFERENCES`, `NEXT_AUTHORIZED_ACTION`, and `VALIDATION_STATUS`.

Artifact references have exactly `reference_id`, `repository_relative_path`, `sha256`, `byte_size`, `artifact_type`, `description`, and `read_condition`. Short strings are at most 256 UTF-8 bytes; IDs are 64 bytes and paths 512 bytes. Paths are safe repository-relative POSIX paths. Hashes are lowercase SHA-256. The standard-library validator streams each referenced file and checks existence, size, and hash. Facts and blockers contain only short summaries and artifact IDs; facts require evidence. Raw content, reports, logs, diffs, reasoning, and transcripts remain external.

The fixed limits bound the handoff object while allowing multiple references. External artifact size does not enter Body state.
