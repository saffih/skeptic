"""Deterministic checks for delegated-agent envelopes and RunSkeptic receipts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BEGIN = "BEGIN_AGENT_RETURN"
END = "END_AGENT_RETURN"
REQUIRED_AGENT = {"dispatch_id", "status", "output", "validation", "blocker"}
OPTIONAL_AGENT = {"changed", "check", "next"}
STATUSES = {"COMPLETE", "PARTIAL", "BLOCKED", "FAILED"}
VALIDATIONS = {"PASS", "FAIL", "NOT_RUN", "NOT_APPLICABLE", "UNKNOWN"}

RECEIPT_ALIASES = {
    "source": ("source read",),
    "companions": ("companion files read", "companion files"),
    "permission": ("permission mode",),
    "done": ("done statement", "done"),
    "prompt": ("prompt review level and task feasibility", "prompt review", "prompt review / feasibility", "prompt review level / feasibility"),
    "steps": ("major steps run", "major steps"),
    "thinkers": ("thinkers considered", "thinkers"),
    "evidence": ("evidence used", "evidence"),
    "decision": ("decision path",),
    "verification": ("verification performed", "verification"),
    "unknowns": ("unresolved conflicts / unknowns", "unresolved", "unknowns"),
    "final": ("final output category", "final task output category"),
}
STEPS = ("GATE", "FUNDAMENTAL SCAN", "MAP", "CONFIDENCE", "STABILIZE", "EVIDENCE", "DECIDE", "ACT", "VERIFY", "LEARN")
THINKERS = ("CH", "OM", "FE", "PO", "KT", "SH")
BOUNDARY_VALID = "BOUNDARY_GOVERNANCE_VALID"
BOUNDARY_INVALID = "BOUNDARY_GOVERNANCE_INVALID"


def normalize(value: str) -> str:
    value = value.lower().replace("’", "'").replace("-", " ")
    value = re.sub(r"[`*_#>|]", " ", value)
    value = re.sub(r"[^a-z0-9/+\- ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def check_agent_envelope(text: str, expected_dispatch_id: str, output_required: bool = False) -> dict:
    begins, ends = text.count(BEGIN), text.count(END)
    if begins == 0 and ends == 0:
        return {"result": "AGENT_RETURN_MISSING", "defects": ["no envelope"]}
    if begins != 1 or ends != 1:
        result = "AGENT_RETURN_DUPLICATE" if begins > 1 or ends > 1 else "AGENT_ENVELOPE_INVALID"
        return {"result": result, "defects": [f"begin={begins}, end={ends}"]}
    start, finish = text.index(BEGIN) + len(BEGIN), text.index(END)
    if finish < start:
        return {"result": "AGENT_ENVELOPE_INVALID", "defects": ["reversed markers"]}
    values, defects = {}, []
    allowed = REQUIRED_AGENT | OPTIONAL_AGENT
    for raw in text[start:finish].splitlines():
        line = raw.strip()
        if not line:
            continue
        if ":" not in line:
            defects.append(f"malformed line: {line}")
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        if key not in allowed:
            defects.append(f"unknown field: {key}")
        elif key in values:
            defects.append(f"duplicate field: {key}")
        else:
            values[key] = value
    defects.extend(f"missing field: {field}" for field in sorted(REQUIRED_AGENT - values.keys()))
    if defects:
        return {"result": "AGENT_ENVELOPE_INVALID", "defects": defects}
    if values["dispatch_id"] != expected_dispatch_id:
        defects.append("dispatch_id mismatch")
    if values["status"] not in STATUSES:
        defects.append("unsupported status")
    if values["validation"] not in VALIDATIONS:
        defects.append("unsupported validation")
    if output_required and not values["output"]:
        defects.append("empty required output")
    if values["status"] == "COMPLETE" and values["blocker"].upper() != "NONE":
        defects.append("COMPLETE with blocker")
    if values["status"] == "COMPLETE" and values["validation"] == "FAIL":
        defects.append("COMPLETE with failed validation")
    return {"result": "AGENT_ENVELOPE_INVALID" if defects else "AGENT_ENVELOPE_VALID", **values, "defects": defects}


def field_for(label: str) -> str | None:
    label = normalize(label)
    for field, aliases in RECEIPT_ALIASES.items():
        if any(label == alias or label.startswith(alias + " ") for alias in aliases):
            return field
    return None


def extract_receipt(text: str) -> tuple[dict, list, int | None]:
    lines = text.splitlines()
    heading = next((i for i, line in enumerate(lines) if "runskeptic receipt" in normalize(line)), None)
    if heading is None:
        return {}, ["no receipt heading"], None
    values, defects = {}, []
    for raw in lines[heading + 1:]:
        line = raw.strip()
        if not line:
            continue
        table = re.match(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$", line)
        bold = re.match(r"^[-*]?\s*\*\*([^*]+?):\*\*\s*(.*)$", line)
        plain = re.match(r"^[-*]?\s*([^:]+):\s*(.*)$", line)
        match = table or bold or plain
        if not match:
            continue
        label, value = match.groups()
        if normalize(label).replace(" ", "") in {"field", "---"}:
            continue
        field = field_for(label)
        if field:
            value = value.strip()
            if field in values and values[field] != value:
                defects.append(f"conflicting duplicate field: {field}")
            values[field] = value
    defects.extend(f"missing receipt field: {field}" for field in sorted(set(RECEIPT_ALIASES) - values.keys()))
    return values, defects, heading


def check_skeptic_receipt(text: str, expected_source: str | None = None, expected_source_sha: str | None = None, require_task_prompt: bool = False) -> dict:
    fields, defects, heading = extract_receipt(text)
    if defects:
        return {"result": "SKEPTIC_SUBSTANTIVE_RERUN_REQUIRED", "fields": fields, "defects": defects}
    if "unavailable" in normalize(fields["source"]):
        return {"result": "SKEPTIC_RECEIPT_CONFLICT", "fields": fields, "defects": ["source unavailable"]}
    if expected_source and expected_source.lower() not in fields["source"].lower():
        defects.append("expected source missing")
    if expected_source_sha and expected_source_sha.lower() not in fields["source"].lower():
        defects.append("expected source SHA missing")
    if require_task_prompt and "agents/task-prompt.md" not in fields["companions"]:
        defects.append("required Task Prompt companion missing")
    if not any(mode in normalize(fields["permission"]) for mode in ("read only", "patch local", "fix if valid")):
        defects.append("unsupported permission mode")
    missing_steps = [token for token in STEPS if token not in fields["steps"].upper()]
    missing_thinkers = [token for token in THINKERS if token not in fields["thinkers"].upper()]
    if missing_steps:
        defects.append("missing steps: " + ", ".join(missing_steps))
    if missing_thinkers:
        defects.append("missing thinkers: " + ", ".join(missing_thinkers))
    finals = [value for value in ("HANDLED", "CONFLICT") if value in fields["final"].upper()]
    if len(finals) != 1:
        defects.append("invalid final category")
    body = "\n".join(text.splitlines()[:heading]).upper() if heading is not None else ""
    body_finals = [value for value in ("HANDLED", "CONFLICT") if value in body]
    if len(body_finals) == 1 and finals and body_finals[0] != finals[0]:
        return {"result": "SKEPTIC_RECEIPT_CONFLICT", "fields": fields, "defects": ["body/receipt category conflict"]}
    if "PASS" in fields["decision"].upper() and any(token in fields["unknowns"].upper() for token in ("BLOCKING", "UNRESOLVED ACTION", "CONFLICT")):
        return {"result": "SKEPTIC_RECEIPT_CONFLICT", "fields": fields, "defects": ["PASS with blocking state"]}
    return {"result": "SKEPTIC_SUBSTANTIVE_RERUN_REQUIRED" if defects else "SKEPTIC_RECEIPT_VALID", "fields": fields, "defects": defects}


def check_boundary_governance(text: str) -> dict:
    """Reject explicit boundary contradictions without requiring ceremony."""
    value = normalize(text)
    defects: list[str] = []

    def asserted(phrase: str) -> bool:
        for match in re.finditer(re.escape(phrase), value):
            prefix = value[: match.start()].split()[-5:]
            if not ({"not", "never", "cannot"} & set(prefix)):
                return True
        return False

    contradictions = {
        "Boundary Agent cannot be mandatory for every delegation": (
            "boundary agent is required for every delegation",
            "must use a boundary agent for every delegation",
        ),
        "Boundary Agent cannot prove substantive correctness": (
            "boundary agent proves substantive correctness",
            "boundary agent guarantees substantive correctness",
            "boundary agent proves the work is correct",
        ),
        "Boundary Agent cannot prove runtime isolation": (
            "boundary agent proves runtime isolation",
            "boundary agent guarantees runtime isolation",
        ),
        "delegated context cannot be assumed fresh": (
            "delegated contexts are always fresh",
            "every delegated context is fresh",
            "delegation always creates a fresh context",
        ),
        "boundary routing cannot default to the strongest model": (
            "boundary agent must use the strongest model",
            "always use the strongest model for boundary",
            "boundary processing always uses the strongest model",
        ),
    }
    for defect, phrases in contradictions.items():
        if any(asserted(phrase) for phrase in phrases):
            defects.append(defect)

    recursive = any(
        phrase in value
        for phrase in (
            "recursive delegation",
            "delegated agents may delegate",
            "delegates further",
            "subagents may delegate",
        )
    )
    if recursive:
        required = {
            "transitive subtree rule": "transitive",
            "deterministic-first routing": "deterministic first",
            "conditional Boundary Agent selection": "boundary agent",
            "completion-envelope validation": "agent completion envelope",
            "independent work acceptance": "independent work acceptance",
            "compact upward reporting": "compact upward reporting",
        }
        defects.extend(
            f"recursive delegation missing {label}"
            for label, marker in required.items()
            if marker not in value
        )
    return {"result": BOUNDARY_INVALID if defects else BOUNDARY_VALID, "defects": defects}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    agent = sub.add_parser("agent-envelope")
    agent.add_argument("input_file")
    agent.add_argument("--expected-dispatch-id", required=True)
    agent.add_argument("--output-required", action="store_true")
    receipt = sub.add_parser("skeptic-receipt")
    receipt.add_argument("input_file")
    receipt.add_argument("--expected-source")
    receipt.add_argument("--expected-source-sha")
    receipt.add_argument("--require-task-prompt", action="store_true")
    boundary = sub.add_parser("boundary-governance")
    boundary.add_argument("input_file")
    for child in (agent, receipt, boundary):
        child.add_argument("--json", action="store_true")
    args = parser.parse_args()
    text = Path(args.input_file).read_text(encoding="utf-8")
    if args.command == "agent-envelope":
        result = check_agent_envelope(text, args.expected_dispatch_id, args.output_required)
    elif args.command == "skeptic-receipt":
        result = check_skeptic_receipt(text, args.expected_source, args.expected_source_sha, args.require_task_prompt)
    else:
        result = check_boundary_governance(text)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result["result"])
    return 0 if result["result"] in {"AGENT_ENVELOPE_VALID", "SKEPTIC_RECEIPT_VALID", BOUNDARY_VALID} else 1


if __name__ == "__main__":
    raise SystemExit(main())
