# Artifact Reference Contract (Outcome A)

## Overview

The Artifact Reference contract defines a provider-neutral mechanism for cross-agent handoff of substantial context. References carry identity, integrity, and retrieval metadata without requiring automatic inline expansion of artifact bodies.

## Core Principles

### 1. Reference vs. Inline Decision Rule

**Inline (small, decision-critical):**
- Small instructions, bounded objectives, validation criteria, IDs
- Maximum ~256 UTF-8 bytes
- Decision-critical content: risk of misunderstanding > cost of inline
- Example: dispatch ID, rejection criteria, role name

**Reference (substantial, reusable, boundary-surviving):**
- Target Tasks, evidence manifests, plans, logs, diffs, full source
- Already persisted and accessibly stored
- Reused across multiple agents or sessions
- Survives agent boundary; archived after task completion
- Example: Target Task file, Plan artifact, checkpoint

### 2. ArtifactReference Semantics

An ArtifactReference carries:
- **reference_id**: unique identifier (≤64 bytes)
- **path_or_uri**: filesystem path or URI (≤512 bytes)
- **sha256**: lowercase hex SHA-256 (64 chars exactly)
- **byte_size**: serialized size in bytes (≥0)
- **media_type**: MIME type (e.g., "text/markdown", "application/json")
- **authority_class**: source trust level (reference_implementation, contract, checkpoint, evidence, generated)
- **focused_retrieval_guidance**: what receiver should extract (≤512 bytes)
- **complete_read_required**: boolean flag
- **complete_read_reason**: reason if complete_read_required=True

### 3. Receiver Responsibilities

When receiving an ArtifactReference:
1. **Verify access** before reading
2. **Verify hash** against expected value
3. **Respect focused_retrieval_guidance** — fetch only what needed for next authorized action
4. **Record complete_read_required flag** — if True, must read entire artifact
5. **Never assume completeness** from reference alone
6. **Fail closed** if reference mismatch or inaccessible

### 4. Sender Responsibilities

When creating an ArtifactReference:
1. **Compute exact SHA-256** of artifact as-written
2. **Validate size** before serialization
3. **Provide focused guidance** specific to receiver's next action
4. **Set complete_read_required** only when entire artifact is needed for correctness
5. **Document authority_class** so receiver knows trust level
6. **Never expand inline** when reference is required

## Provider-Neutral Scope

### What is NOT specified

- Filesystem layout (repository, shared workspace, cloud storage — any accessible location)
- Artifact API (files, database, REST endpoint — any retrieval mechanism)
- Durability guarantees (fsync, crash-safety — provider-specific)
- Transport protocol (HTTP, local disk, MCP — implementation detail)

### What IS specified

- Reference structure (fields, validation, size limits)
- Hash verification (SHA-256, exact format)
- Access semantics (verify before read, fail closed)
- Focused retrieval discipline (do not auto-expand)
- Authority classification (how to interpret trust level)

## Example: Target Task Reference

```python
ArtifactReference(
    reference_id="task-compact-handoff-001",
    path_or_uri="experiments/body-brain-artifacts/target-task-compact-handoff-rotation-001.md",
    sha256="d48f9ae34bbcdadc909a69c650d20d1805b782afc507a02dd22861985a9c3da8",
    byte_size=10019,
    media_type="text/markdown",
    authority_class="reference_implementation",
    focused_retrieval_guidance="Read entire file for complete task statement and acceptance criteria",
    complete_read_required=True,
    complete_read_reason="Task statement is immutable requirement; must be read in full to understand all 7 outcomes and terminal conditions"
)
```

## Example: Evidence Manifest Reference

```python
ArtifactReference(
    reference_id="manifest-compact-handoff-001",
    path_or_uri="experiments/body-brain-artifacts/evidence-manifest-001.json",
    sha256="03ef1d7d226e07f22e43666b56979f43d172ae8931e1da124bb189ab6362a47c",
    byte_size=6398,
    media_type="application/json",
    authority_class="evidence",
    focused_retrieval_guidance="Verify access and hash. Use focused retrieval guidance therein to access only required repository state.",
    complete_read_required=False,
    complete_read_reason=None
)
```

## Size Budget

- ArtifactReference structure when serialized: typically 500–800 bytes per reference
- Dispatch tickets may contain 2–4 references: ≤3,200 bytes out of 8,192-byte budget
- Checkpoint may contain 10–20 references: ≤16,000 bytes out of 32,768-byte budget
- Compact return may reference 2–3 artifacts: ≤2,400 bytes out of 4,096-byte budget

## Validation Rules

### Acceptable ArtifactReference

- All fields present and non-empty (except optional complete_read_reason)
- reference_id: non-empty, ≤64 UTF-8 bytes
- path_or_uri: safe path or URI, ≤512 UTF-8 bytes, no absolute paths if filesystem-based
- sha256: valid lowercase hex, exactly 64 characters
- byte_size: non-negative integer
- media_type: non-empty, ≤256 UTF-8 bytes
- authority_class: one of the 5 defined classes
- focused_retrieval_guidance: non-empty, ≤512 UTF-8 bytes
- complete_read_required: boolean (True if and only if complete_read_reason is provided)

### Reject (Fail Closed)

- Missing field or None where required
- Invalid format (non-hex SHA-256, negative size, empty guidance)
- Oversized fields
- Unknown authority_class
- complete_read_reason without complete_read_required=True
- Path traversal or absolute path in filesystem reference

## Preservation

This contract remains provider-neutral and does not specify:
- Provider's context window or token limits
- Hidden routing or model selection
- Data durability or crash-safety beyond hash verification
- Transport encryption or authentication
- Artifact persistence duration

Receivers must treat reference as "valid reference to current artifact" (hash-bound to exact point in time) without claiming hidden provider guarantees.

## Integration Points

- **Dispatch Ticket** (Outcome B): uses ArtifactReference for Task, Manifest, Plan
- **Checkpoint** (Outcome D): embeds list of ArtifactReference for all external state
- **Compact Return** (Outcome F): references artifacts instead of embedding bodies
- **Resume Validator** (Outcome E): verifies ArtifactReference hashes before continuing
