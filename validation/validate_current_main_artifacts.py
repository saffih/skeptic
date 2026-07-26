#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TERMINAL_CATEGORIES = {
    "CURRENT_MAIN_BEHAVIORALLY_SUPPORTED",
    "CURRENT_MAIN_REGRESSION_FOUND",
    "CURRENT_MAIN_VALIDATION_INCONCLUSIVE",
    "MODEL_CREDITS_OR_RUNTIME_BLOCKED",
    "VALIDATION_INFRASTRUCTURE_DEFECT",
    "OWNER_DECISION_REQUIRED",
}


def classify_terminal(record: dict[str, Any]) -> str:
    if not record.get("infrastructure_valid", False):
        return "VALIDATION_INFRASTRUCTURE_DEFECT"
    if record.get("runtime_blocked", False):
        return "MODEL_CREDITS_OR_RUNTIME_BLOCKED"
    if record.get("owner_decision_required", False):
        return "OWNER_DECISION_REQUIRED"
    if (
        record.get("critical_material_losses", 0) > 0
        or record.get("candidate_only_dangerous_failures", 0) > 0
        or record.get("noncritical_material_losses", 0) >= 2
        or record.get("material_negative_control_growth", False)
    ):
        return "CURRENT_MAIN_REGRESSION_FOUND"
    if (
        record.get("incomparable_required_scenarios", 0) > 0
        or record.get("material_judge_inconsistency", False)
        or not record.get("all_required_families_valid", False)
    ):
        return "CURRENT_MAIN_VALIDATION_INCONCLUSIVE"
    return "CURRENT_MAIN_BEHAVIORALLY_SUPPORTED"


def validate_scenario_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    manifest = json.loads(path.read_text(encoding="utf-8"))
    visible = manifest.get("visible_fixtures", [])
    contracts = manifest.get("scenario_contracts", {})
    required = set(manifest.get("required_families", []))
    if len(visible) != 6:
        errors.append("expected exactly six visible fixtures")
    if len(set(visible)) != len(visible):
        errors.append("visible fixture paths must be unique")
    fixtures = []
    for relative in visible:
        fixture_path = path.parent / relative
        if not fixture_path.is_file():
            errors.append(f"missing fixture: {relative}")
            continue
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixtures.append(fixture)
        missing = [
            key
            for key in manifest["schema"]["fixture_required_fields"]
            if key not in fixture
        ]
        if missing:
            errors.append(f"{relative} missing fields: {','.join(missing)}")
    ids = [fixture.get("id") for fixture in fixtures]
    if len(ids) != len(set(ids)):
        errors.append("fixture ids must be unique")
    if set(ids) != set(contracts):
        errors.append("scenario contracts must match fixture ids")
    covered = {
        family
        for contract in contracts.values()
        for family in contract.get("families", [])
    }
    missing_families = sorted(required - covered)
    if missing_families:
        errors.append("missing required families: " + ",".join(missing_families))
    if sum(bool(item.get("negative_control")) for item in contracts.values()) < 2:
        errors.append("at least two negative controls are required")
    budget = manifest.get("budget", {})
    if budget != {"generator_calls": 16, "judge_calls": 8, "retry_calls": 0, "total_calls": 24}:
        errors.append("unexpected fixed call budget")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario-manifest", type=Path, required=True)
    parser.add_argument("--result-record", type=Path)
    args = parser.parse_args()
    errors = validate_scenario_manifest(args.scenario_manifest)
    if args.result_record:
        record = json.loads(args.result_record.read_text(encoding="utf-8"))
        actual = classify_terminal(record)
        if actual not in TERMINAL_CATEGORIES:
            errors.append("invalid terminal category")
        if record.get("terminal_verdict") != actual:
            errors.append(f"terminal verdict mismatch: expected {actual}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("CURRENT_MAIN_VALIDATION_ARTIFACTS_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
