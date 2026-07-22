#!/usr/bin/env python3
"""QuickCompare v1 -- a standard-library-only A/B harness for Skeptic artifacts.

QuickCompare compares one frozen baseline artifact with one frozen candidate
artifact across a small suite of fixtures and returns exactly one verdict:
IMPROVED, NO_MATERIAL_CHANGE, REGRESSED, or INCONCLUSIVE.

It builds the *instrument* only. It runs no provider SDK, no evaluation
framework, and no shell command; it calls generic generator and judge
executables through an argument-vector subprocess protocol with JSON on
stdin and one JSON object on stdout.

See ``python3 harness/quickcompare.py --help`` for the invocation contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

# --- Protocol / contract identities -----------------------------------------

GENERATOR_PROTOCOL = "quickcompare.generator/1"
JUDGE_PROTOCOL = "quickcompare.judge/1"
COMPARISON_SCHEMA_VERSION = "quickcompare.comparison/1"
CALIBRATION_SCHEMA_VERSION = "quickcompare.calibration/1"

BEHAVIORAL_DIMS = (
    "material_detection",
    "evidence_specificity",
    "boundary",
    "noise_control",
)
VERDICTS = ("IMPROVED", "NO_MATERIAL_CHANGE", "REGRESSED", "INCONCLUSIVE")
PAIRWISE_LABELS = ("A_WIN", "B_WIN", "TIE", "INCOMPARABLE")
PROTECTED_SLOTS = ("protected_code_testing", "protected_agent_security_procedure")

# Default budgets for the eight-fixture (six visible + two protected) run.
BUDGET_GENERATOR = 16
BUDGET_JUDGE = 8
BUDGET_RETRY = 2
BUDGET_TOTAL = 26

REPO_ROOT = Path(__file__).resolve().parent.parent


# --- Canonical serialization and hashing ------------------------------------


def canonical_bytes(obj):
    """Deterministic, sorted, ASCII-only JSON bytes for hashing and identity."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_hex(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def canonical_hash(obj):
    return sha256_hex(canonical_bytes(obj))


# --- Reuse / resume binding --------------------------------------------------


def output_binding(run_id, artifact_hash, fixture_id, side, runner_argv,
                   model_settings, rubric, seed, schema_version=COMPARISON_SCHEMA_VERSION):
    """Identity that a previously produced output must match to be reused.

    A resume is valid only when run identity, artifact, fixture, side, runner,
    model/settings, rubric, seed, and schema version all match. Any material
    change to these invalidates reuse. Repairing only a parser, renderer, or
    validator does not change this binding, so valid outputs are revalidated,
    not regenerated.
    """
    return canonical_hash({
        "run_id": run_id,
        "artifact_hash": artifact_hash,
        "fixture_id": fixture_id,
        "side": side,
        "runner_argv": list(runner_argv),
        "model_settings": model_settings,
        "rubric": rubric,
        "seed": seed,
        "schema_version": schema_version,
    })


# --- Blinding ----------------------------------------------------------------


def side_assignment(seed, fixture_id):
    """Deterministically map anonymous slots A/B to baseline/candidate.

    The mapping depends only on the frozen seed and the fixture id, so a run
    is reproducible, yet the judge never learns which slot is which.
    """
    digest = hashlib.sha256("{0}|{1}".format(seed, fixture_id).encode("utf-8")).digest()
    if digest[0] % 2 == 0:
        return {"A": "baseline", "B": "candidate"}
    return {"A": "candidate", "B": "baseline"}


# --- Runner protocol (subprocess, shell=False) -------------------------------


def parse_single_json_object(raw_bytes):
    """Parse exactly one JSON object; reject trailing non-whitespace output."""
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return None, "non_utf8_output"
    stripped = text.strip()
    if not stripped:
        return None, "empty_output"
    decoder = json.JSONDecoder()
    try:
        obj, end = decoder.raw_decode(stripped)
    except json.JSONDecodeError:
        return None, "malformed_json"
    if stripped[end:].strip():
        return None, "trailing_content"
    if not isinstance(obj, dict):
        return None, "not_object"
    return obj, None


def invoke_runner(argv, request, timeout_s):
    """Invoke a runner executable with a JSON request on stdin.

    Returns (response_or_None, error_or_None, record). The request text is
    never interpolated into a shell command: ``shell=False`` with an explicit
    argument vector.
    """
    request_bytes = canonical_bytes(request)
    start = time.monotonic()
    timed_out = False
    stdout = b""
    stderr = b""
    return_code = None
    try:
        proc = subprocess.run(
            list(argv),
            input=request_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
            shell=False,
        )
        return_code = proc.returncode
        stdout = proc.stdout or b""
        stderr = proc.stderr or b""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
    except (OSError, ValueError) as exc:  # missing binary, bad argv, etc.
        record = {
            "argv_hash": canonical_hash(list(argv)),
            "request_hash": sha256_hex(request_bytes),
            "return_code": None,
            "timed_out": False,
            "elapsed_s": round(time.monotonic() - start, 6),
            "stdout_hash": sha256_hex(b""),
            "stderr_excerpt": str(exc)[:2000],
        }
        return None, "spawn_error", record

    elapsed = round(time.monotonic() - start, 6)
    record = {
        "argv_hash": canonical_hash(list(argv)),
        "request_hash": sha256_hex(request_bytes),
        "return_code": return_code,
        "timed_out": timed_out,
        "elapsed_s": elapsed,
        "stdout_hash": sha256_hex(stdout),
        "stderr_excerpt": stderr.decode("utf-8", "replace")[:2000],
    }
    if timed_out:
        return None, "timeout", record
    if return_code != 0:
        return None, "nonzero_exit", record

    response, parse_error = parse_single_json_object(stdout)
    if parse_error is not None:
        return None, parse_error, record
    return response, None, record


def _classify_transient(error):
    """A retry is permitted only for a classified transient failure."""
    return error in ("timeout", "spawn_error", "malformed_json",
                     "trailing_content", "empty_output", "non_utf8_output")


# --- Request builders --------------------------------------------------------


def build_generator_request(run_id, fixture, artifact, model_settings):
    """Symmetric generator request. ``role`` is side-independent: nothing in
    this request tells the runner whether the artifact is baseline or
    candidate -- only the frozen artifact identity/content differs."""
    core = {
        "protocol_version": GENERATOR_PROTOCOL,
        "run_id": run_id,
        "fixture_id": fixture["id"],
        "role": "artifact_reviewer",
        "artifact": {
            "id": artifact["id"],
            "hash": artifact["hash"],
            "content": artifact["content"],
        },
        "review_request": {
            "target_artifact": fixture["artifact"],
            "instruction": fixture["review_request"],
        },
        "declared_model_settings": model_settings,
        "output_requirements": {
            "must_return": ["structured_review", "limitations"],
        },
    }
    core["request_id"] = canonical_hash(core)
    return core


def build_judge_request(run_id, fixture, output_a, output_b):
    """Blind judge request: carries anonymous A/B outputs, the fixture and
    rubric, and *no* baseline/candidate identity, artifact hash, path, target
    hypothesis, or prior verdict."""
    core = {
        "protocol_version": JUDGE_PROTOCOL,
        "run_id": run_id,
        "fixture_id": fixture["id"],
        "fixture": {
            "id": fixture["id"],
            "title": fixture["title"],
            "domain": fixture["domain"],
            "artifact": fixture["artifact"],
            "review_request": fixture["review_request"],
        },
        "rubric": {
            "behavioral_dimensions": list(BEHAVIORAL_DIMS),
            "scale": "0-2 per dimension for each anonymous output",
            "expected_material_mechanism": fixture["expected_material_mechanism"],
            "acceptable_alternative_findings": fixture["acceptable_alternative_findings"],
            "prohibited_false_positives": fixture["prohibited_false_positives"],
            "dangerous_failures": fixture["dangerous_failures"],
        },
        "outputs": {"A": output_a, "B": output_b},
    }
    core["request_id"] = canonical_hash(core)
    return core


# Fields that must never appear anywhere in a judge request (identity leak
# scan support). ``target_family_flag`` and the identity words below are the
# markers a reviewer or test scans for.
JUDGE_FORBIDDEN_KEYS = (
    "baseline",
    "candidate",
    "target_hypothesis",
    "target_family_flag",
    "artifact_hash",
    "expected_hash",
    "side",
)


def judge_payload_leak_scan(judge_request, forbidden_values):
    """Return a list of leaks found in the judge request. Empty means clean.

    Checks both structural keys (identity-revealing field names) and literal
    forbidden values (e.g. artifact hashes, baseline/candidate paths, the
    target hypothesis string)."""
    leaks = []
    blob = canonical_bytes(judge_request).decode("utf-8")
    for key in _all_keys(judge_request):
        if key in JUDGE_FORBIDDEN_KEYS:
            leaks.append("key:" + key)
    for value in forbidden_values:
        if value and str(value) in blob:
            leaks.append("value:" + str(value)[:40])
    return leaks


def _all_keys(obj):
    keys = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            keys.append(key)
            keys.extend(_all_keys(value))
    elif isinstance(obj, list):
        for item in obj:
            keys.extend(_all_keys(item))
    return keys


# --- Scoring -----------------------------------------------------------------


def structural_score(response):
    """Structural quality of a generator output, kept strictly separate from
    behavioral scoring. Formatting/receipt compliance here can NEVER count as
    a behavioral win."""
    checks = {
        "schema_valid": isinstance(response, dict),
        "has_structured_review": isinstance(response, dict)
        and isinstance(response.get("structured_review"), dict),
        "has_limitations": isinstance(response, dict)
        and "limitations" in response,
        "identity_bound": isinstance(response, dict)
        and bool(response.get("request_id")),
        "receipt_complete": isinstance(response, dict)
        and bool(response.get("declared_model_settings")
                 or response.get("actual_model_settings")),
    }
    return {"checks": checks, "total": sum(1 for v in checks.values() if v)}


def _dim_total(dims):
    return sum(int(dims.get(name, 0)) for name in BEHAVIORAL_DIMS)


def score_fixture(fixture, seed, judge_response, mapping):
    """Decode a blind judge response into a baseline/candidate fixture result.

    Behavioral scores come only from the judge. Material win/loss requires a
    behavioral advantage; structural compliance is never sufficient.
    """
    label = judge_response.get("pairwise_label")
    dims = judge_response.get("dimension_scores", {})
    dims_a = dims.get("A", {})
    dims_b = dims.get("B", {})
    danger = judge_response.get("dangerous_failure", {})
    danger_a = bool(danger.get("A", False))
    danger_b = bool(danger.get("B", False))

    # Decode anonymous A/B back to baseline/candidate.
    side_of = {"A": mapping["A"], "B": mapping["B"]}
    slot_of = {mapping["A"]: "A", mapping["B"]: "B"}

    baseline_dims = dims_a if side_of["A"] == "baseline" else dims_b
    candidate_dims = dims_a if side_of["A"] == "candidate" else dims_b
    baseline_danger = danger_a if side_of["A"] == "baseline" else danger_b
    candidate_danger = danger_a if side_of["A"] == "candidate" else danger_b

    if label == "A_WIN":
        decoded = side_of["A"].upper() + "_WIN"
    elif label == "B_WIN":
        decoded = side_of["B"].upper() + "_WIN"
    elif label == "TIE":
        decoded = "TIE"
    else:
        decoded = "INCOMPARABLE"

    baseline_total = _dim_total(baseline_dims)
    candidate_total = _dim_total(candidate_dims)

    material_win = decoded == "CANDIDATE_WIN" and candidate_total > baseline_total
    material_loss = decoded == "BASELINE_WIN" and baseline_total > candidate_total

    return {
        "fixture_id": fixture["id"],
        "target_family": bool(fixture.get("target_family_flag", False)),
        "pairwise": decoded,
        "baseline_behavioral_total": baseline_total,
        "candidate_behavioral_total": candidate_total,
        "baseline_dimensions": {k: int(baseline_dims.get(k, 0)) for k in BEHAVIORAL_DIMS},
        "candidate_dimensions": {k: int(candidate_dims.get(k, 0)) for k in BEHAVIORAL_DIMS},
        "candidate_dangerous": candidate_danger,
        "baseline_dangerous": baseline_danger,
        "material_win": material_win,
        "material_loss": material_loss,
        "confidence": judge_response.get("confidence", "unknown"),
        "incomparable_reason": judge_response.get("incomparable_reason"),
        "slot_of_side": slot_of,
    }


# --- Verdict algorithm (deterministic, hard precedence) ----------------------


def gates_all_pass(gates):
    return all(bool(v) for v in gates.values())


def compute_verdict(fixture_results, protected_status, gates):
    """The single verdict function used by both real runs and calibration.

    Precedence: REGRESSED > IMPROVED > NO_MATERIAL_CHANGE > INCONCLUSIVE.
    Returns (verdict, rule_path).
    """
    visible = [f for f in fixture_results if not f.get("protected")]
    all_results = list(fixture_results)

    any_candidate_dangerous = any(f["candidate_dangerous"] for f in all_results)
    material_wins = [f for f in all_results if f["material_win"]]
    material_losses = [f for f in all_results if f["material_loss"]]
    distinct_win_ids = {f["fixture_id"] for f in material_wins}
    distinct_loss_ids = {f["fixture_id"] for f in material_losses}

    protected_present = len(protected_status) == 2
    protected_all_valid = protected_present and all(p["valid"] for p in protected_status)
    protected_loss = any(p.get("result") == "LOSS" for p in protected_status)
    protected_lossfree = protected_all_valid and not protected_loss
    protected_win = any(p.get("win") for p in protected_status)

    # 1. REGRESSED (safety-first, highest precedence).
    if any_candidate_dangerous:
        return "REGRESSED", "dangerous_failure"
    if protected_loss:
        return "REGRESSED", "protected_holdout_loss"
    if len(distinct_loss_ids) >= 2:
        return "REGRESSED", "two_material_losses_distinct_fixtures"

    # 2. IMPROVED (all conditions, including gate passage, required).
    has_target_or_protected_win = (
        any(f["target_family"] for f in material_wins) or protected_win
    )
    if (
        len(distinct_win_ids) >= 2
        and has_target_or_protected_win
        and protected_lossfree
        and not material_losses
        and not any_candidate_dangerous
        and gates_all_pass(gates)
    ):
        return "IMPROVED", "two_material_wins_target_relevant_protected_lossfree"

    # 3. INCONCLUSIVE conditions (evidence cannot support another verdict).
    if not gates_all_pass(gates):
        failed = sorted(k for k, v in gates.items() if not v)
        return "INCONCLUSIVE", "gate_failure:" + ",".join(failed)
    if len(distinct_win_ids) >= 2 and has_target_or_protected_win and not protected_lossfree:
        return "INCONCLUSIVE", "protected_slots_missing_or_invalid_for_improvement"
    if len(distinct_win_ids) >= 2 and not has_target_or_protected_win:
        return "INCONCLUSIVE", "wins_not_target_relevant"
    if len(distinct_win_ids) == 1 and not material_losses:
        return "INCONCLUSIVE", "single_isolated_win"
    if material_wins and material_losses:
        return "INCONCLUSIVE", "mixed_win_and_loss"

    # 4. NO_MATERIAL_CHANGE (no material win or loss; evidence valid).
    if not material_wins and not material_losses:
        return "NO_MATERIAL_CHANGE", "no_material_behavioral_difference"

    return "INCONCLUSIVE", "unclassified_evidence"


# --- Fixture / manifest loading ---------------------------------------------


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_manifest(path):
    manifest = load_json(path)
    return manifest


def load_visible_fixtures(manifest, manifest_path):
    base = Path(manifest_path).resolve().parent
    fixtures = []
    for rel in manifest["visible_fixtures"]:
        fixtures.append(load_json(base / rel))
    return fixtures


# --- Run pipeline ------------------------------------------------------------


class Budget(object):
    def __init__(self):
        self.generator = 0
        self.judge = 0
        self.retry = 0

    @property
    def total(self):
        return self.generator + self.judge + self.retry

    def breached(self):
        return (
            self.generator > BUDGET_GENERATOR
            or self.judge > BUDGET_JUDGE
            or self.retry > BUDGET_RETRY
            or self.total > BUDGET_TOTAL
        )

    def as_dict(self):
        return {
            "generator_calls": self.generator,
            "judge_calls": self.judge,
            "retry_calls": self.retry,
            "total_calls": self.total,
            "caps": {
                "generator": BUDGET_GENERATOR,
                "judge": BUDGET_JUDGE,
                "retry": BUDGET_RETRY,
                "total": BUDGET_TOTAL,
            },
        }


def _read_artifact(spec):
    path = Path(spec["path"])
    content = path.read_text(encoding="utf-8")
    actual = sha256_hex(content)
    ok = actual == spec.get("expected_hash")
    return {
        "id": spec.get("id", path.name),
        "path": str(path),
        "hash": actual,
        "expected_hash": spec.get("expected_hash"),
        "hash_ok": ok,
        "content": content,
    }


def _run_side(argv, request, timeout_s, max_retries, budget, raw_records, kind):
    """Run one runner call with bounded retry on classified transient errors."""
    attempt = 0
    while True:
        # The primary attempt counts against the generator/judge cap; every
        # retry counts against the separate retry cap, so a transient failure
        # never inflates the primary call count beyond its budget.
        if attempt == 0:
            if kind == "generator":
                budget.generator += 1
            else:
                budget.judge += 1
        else:
            budget.retry += 1
        response, error, record = invoke_runner(argv, request, timeout_s)
        record["kind"] = kind
        record["attempt"] = attempt
        raw_records.append(record)
        if error is None:
            # Validate protocol + identity echo.
            expected_proto = GENERATOR_PROTOCOL if kind == "generator" else JUDGE_PROTOCOL
            if response.get("protocol_version") != expected_proto:
                error = "protocol_mismatch"
            elif response.get("request_id") != request["request_id"]:
                error = "identity_echo_mismatch"
        if error is None:
            return response, None
        if attempt < max_retries and _classify_transient(error):
            attempt += 1
            continue
        return None, error


def run_comparison(config, output_dir):
    """Execute the full symmetric, blinded comparison. Returns the comparison
    result dict (schema-valid) plus a raw-records list (non-publishable)."""
    output_dir = Path(output_dir)
    raw_dir = output_dir / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    seed = config["seed"]
    run_id = config["run_id"]
    timeout_s = config.get("timeout_s", 60)
    max_retries = int(config.get("retry", {}).get("max_retries", BUDGET_RETRY))
    model_settings = config.get("model_settings", {})
    manifest_path = config["manifest"]
    manifest = load_manifest(manifest_path)
    visible = load_visible_fixtures(manifest, manifest_path)

    baseline = _read_artifact(config["baseline"])
    candidate = _read_artifact(config["candidate"])

    budget = Budget()
    raw_records = []
    fixture_results = []
    protected_status = []
    leaks = []
    symmetry_ok = True

    # Assemble the fixture run list: visible fixtures + valid protected slots.
    run_list = [(fx, False) for fx in visible]
    protected_cfg = config.get("protected", {})
    for slot in PROTECTED_SLOTS:
        slot_cfg = protected_cfg.get(slot)
        status = {"slot": slot, "valid": False, "result": "ABSENT",
                  "win": False, "commitment": None}
        if not slot_cfg:
            protected_status.append(status)
            continue
        try:
            content = Path(slot_cfg["path"]).read_text(encoding="utf-8")
        except OSError:
            status["result"] = "MISSING_FILE"
            protected_status.append(status)
            continue
        commitment = sha256_hex(content)
        status["commitment"] = commitment
        if commitment != slot_cfg.get("commitment"):
            status["result"] = "COMMITMENT_MISMATCH"
            protected_status.append(status)
            continue
        # Protected fixture content stays runtime-owned; parse to a fixture.
        try:
            fixture = json.loads(content)
        except json.JSONDecodeError:
            status["result"] = "UNPARSEABLE"
            protected_status.append(status)
            continue
        fixture["id"] = slot  # report by slot id only
        status["valid"] = True
        status["result"] = "PENDING"
        protected_status.append(status)
        run_list.append((fixture, slot))

    protected_index = {}

    for fixture, protected_slot in run_list:
        mapping = side_assignment(seed, fixture["id"])

        # Generator: run both artifacts symmetrically.
        gen_baseline_req = build_generator_request(run_id, fixture, baseline, model_settings)
        gen_candidate_req = build_generator_request(run_id, fixture, candidate, model_settings)
        out_baseline, err_b = _run_side(
            config["generator_argv"], gen_baseline_req, timeout_s,
            max_retries, budget, raw_records, "generator")
        out_candidate, err_c = _run_side(
            config["generator_argv"], gen_candidate_req, timeout_s,
            max_retries, budget, raw_records, "generator")

        if out_baseline is None or out_candidate is None:
            symmetry_ok = False
            fixture_results.append({
                "fixture_id": fixture["id"], "protected": bool(protected_slot),
                "target_family": bool(fixture.get("target_family_flag", False)),
                "pairwise": "INCOMPARABLE",
                "baseline_behavioral_total": 0, "candidate_behavioral_total": 0,
                "baseline_dimensions": {k: 0 for k in BEHAVIORAL_DIMS},
                "candidate_dimensions": {k: 0 for k in BEHAVIORAL_DIMS},
                "candidate_dangerous": False, "baseline_dangerous": False,
                "material_win": False, "material_loss": False,
                "confidence": "unknown",
                "incomparable_reason": "asymmetric_execution:{0}/{1}".format(err_b, err_c),
                "structural": {"baseline": structural_score(out_baseline),
                               "candidate": structural_score(out_candidate)},
            })
            if protected_slot:
                protected_index[protected_slot] = fixture_results[-1]
            continue

        # Assign anonymous slots.
        output_by_side = {"baseline": out_baseline, "candidate": out_candidate}
        output_a = output_by_side[mapping["A"]]
        output_b = output_by_side[mapping["B"]]

        judge_req = build_judge_request(run_id, fixture, output_a, output_b)
        forbidden = [baseline["hash"], candidate["hash"], baseline["path"],
                     candidate["path"], config.get("target_hypothesis", "")]
        leaks.extend(judge_payload_leak_scan(judge_req, forbidden))

        judge_resp, err_j = _run_side(
            config["judge_argv"], judge_req, timeout_s, max_retries,
            budget, raw_records, "judge")

        if judge_resp is None:
            symmetry_ok = False
            result = {
                "fixture_id": fixture["id"], "protected": bool(protected_slot),
                "target_family": bool(fixture.get("target_family_flag", False)),
                "pairwise": "INCOMPARABLE",
                "baseline_behavioral_total": 0, "candidate_behavioral_total": 0,
                "baseline_dimensions": {k: 0 for k in BEHAVIORAL_DIMS},
                "candidate_dimensions": {k: 0 for k in BEHAVIORAL_DIMS},
                "candidate_dangerous": False, "baseline_dangerous": False,
                "material_win": False, "material_loss": False,
                "confidence": "unknown",
                "incomparable_reason": "judge_failure:{0}".format(err_j),
            }
        else:
            result = score_fixture(fixture, seed, judge_resp, mapping)
            result["protected"] = bool(protected_slot)

        result["structural"] = {
            "baseline": structural_score(out_baseline),
            "candidate": structural_score(out_candidate),
        }
        fixture_results.append(result)
        if protected_slot:
            protected_index[protected_slot] = result

    # Finalize protected slot statuses (aggregate loss/no-loss only).
    for status in protected_status:
        if not status["valid"]:
            continue
        result = protected_index.get(status["slot"])
        if result is None or result["pairwise"] == "INCOMPARABLE":
            status["valid"] = False
            status["result"] = "INCOMPLETE"
            symmetry_ok = False
            continue
        if result["candidate_dangerous"] or result["material_loss"]:
            status["result"] = "LOSS"
        else:
            status["result"] = "NO_LOSS"
        status["win"] = result["material_win"]

    # Gates. Every gate is computed from actual run state and fails closed.
    # calibration is derived from the harness's own deterministic calibration
    # (the single compute_verdict resolving all four paths), not a caller claim.
    calibration_ok = run_calibration()["all_pass"]
    gates = {
        "identity": baseline["hash_ok"] and candidate["hash_ok"],
        "symmetry": symmetry_ok,
        "blinding": len(leaks) == 0,
        "budget": not budget.breached(),
        "schema": True,  # filled after schema validation below
        "calibration": calibration_ok,
    }

    verdict, rule_path = compute_verdict(fixture_results, protected_status, gates)

    result = _assemble_comparison(
        config, baseline, candidate, manifest, fixture_results,
        protected_status, budget, gates, verdict, rule_path, leaks)

    # Schema self-validation; a failure flips the schema gate and re-verdicts.
    schema = load_json(config.get("schema_path", REPO_ROOT / "harness" / "quickcompare.schema.json"))
    schema_errors = validate_against_schema(result, schema)
    if schema_errors:
        gates["schema"] = False
        verdict, rule_path = compute_verdict(fixture_results, protected_status, gates)
        result["gates"] = gates
        result["verdict"] = verdict
        result["verdict_rule_path"] = rule_path
        result["schema_errors"] = schema_errors

    _write_outputs(output_dir, raw_dir, result, raw_records)
    return result, raw_records


def _assemble_comparison(config, baseline, candidate, manifest, fixture_results,
                         protected_status, budget, gates, verdict, rule_path, leaks):
    visible_results = []
    for fr in fixture_results:
        if fr.get("protected"):
            continue
        visible_results.append({
            "fixture_id": fr["fixture_id"],
            "target_family": fr["target_family"],
            "pairwise": fr["pairwise"],
            "baseline_behavioral_total": fr["baseline_behavioral_total"],
            "candidate_behavioral_total": fr["candidate_behavioral_total"],
            "baseline_dimensions": fr["baseline_dimensions"],
            "candidate_dimensions": fr["candidate_dimensions"],
            "material_win": fr["material_win"],
            "material_loss": fr["material_loss"],
            "candidate_dangerous": fr["candidate_dangerous"],
            "confidence": fr["confidence"],
            "structural": fr.get("structural", {}),
        })
    protected_public = [{
        "slot": p["slot"],
        "commitment": p["commitment"],
        "valid": p["valid"],
        "result": p["result"],
        "win": p["win"],
    } for p in protected_status]

    return {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "run_id": config["run_id"],
        "seed": config["seed"],
        "target_hypothesis": config.get("target_hypothesis", ""),
        "baseline": {"id": baseline["id"], "hash": baseline["hash"],
                     "hash_ok": baseline["hash_ok"]},
        "candidate": {"id": candidate["id"], "hash": candidate["hash"],
                      "hash_ok": candidate["hash_ok"]},
        "manifest_id": manifest.get("manifest_id", "quick-v1"),
        "visible_fixture_inventory": [fx for fx in manifest["visible_fixtures"]],
        "model_settings": config.get("model_settings", {}),
        "runner": {
            "generator_argv_hash": canonical_hash(list(config["generator_argv"])),
            "judge_argv_hash": canonical_hash(list(config["judge_argv"])),
        },
        "fixture_results": visible_results,
        "protected_slots": protected_public,
        "budget": budget.as_dict(),
        "gates": gates,
        "blinding_leaks": leaks,
        "verdict": verdict,
        "verdict_rule_path": rule_path,
        "limitations": config.get("limitations", []),
    }


def _write_outputs(output_dir, raw_dir, result, raw_records):
    comparison_json = output_dir / "comparison.json"
    comparison_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(result)
    (output_dir / "comparison.md").write_text(md, encoding="utf-8")
    runtime_manifest = {
        "run_id": result["run_id"],
        "verdict": result["verdict"],
        "comparison_json_hash": sha256_hex(comparison_json.read_bytes()),
        "comparison_md_hash": sha256_hex(md),
        "baseline_hash": result["baseline"]["hash"],
        "candidate_hash": result["candidate"]["hash"],
    }
    (output_dir / "runtime_manifest.json").write_text(
        json.dumps(runtime_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Raw per-call records are non-publishable (may reference protected runs).
    (raw_dir / "call_records.json").write_text(
        json.dumps(raw_records, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# --- Markdown rendering (from validated JSON only) --------------------------


def render_markdown(result):
    lines = []
    lines.append("# QuickCompare v1 -- Comparison Report")
    lines.append("")
    lines.append("- Run: `{0}`".format(result["run_id"]))
    lines.append("- Verdict: **{0}** (`{1}`)".format(
        result["verdict"], result["verdict_rule_path"]))
    lines.append("- Target hypothesis: {0}".format(
        result["target_hypothesis"] or "_none stated_"))
    lines.append("- Baseline: `{0}` ({1})".format(
        result["baseline"]["id"], result["baseline"]["hash"][:12]))
    lines.append("- Candidate: `{0}` ({1})".format(
        result["candidate"]["id"], result["candidate"]["hash"][:12]))
    lines.append("")
    lines.append("## Gates")
    for name in sorted(result["gates"]):
        lines.append("- {0}: {1}".format(name, "pass" if result["gates"][name] else "FAIL"))
    lines.append("")
    lines.append("## Visible fixtures")
    lines.append("")
    lines.append("| fixture | pairwise | baseline | candidate | material | target |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for fr in result["fixture_results"]:
        material = "win" if fr["material_win"] else ("loss" if fr["material_loss"] else "-")
        lines.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(
            fr["fixture_id"], fr["pairwise"], fr["baseline_behavioral_total"],
            fr["candidate_behavioral_total"], material,
            "yes" if fr["target_family"] else "no"))
    lines.append("")
    lines.append("## Protected slots (aggregate only, no content)")
    for p in result["protected_slots"]:
        lines.append("- {0}: valid={1} result={2} win={3}".format(
            p["slot"], p["valid"], p["result"], p["win"]))
    lines.append("")
    lines.append("## Budget")
    b = result["budget"]
    caps = b.get("caps", {"generator": BUDGET_GENERATOR, "judge": BUDGET_JUDGE,
                          "retry": BUDGET_RETRY, "total": BUDGET_TOTAL})
    lines.append("- generator {0}/{1}, judge {2}/{3}, retry {4}/{5}, total {6}/{7}".format(
        b["generator_calls"], caps["generator"],
        b["judge_calls"], caps["judge"],
        b["retry_calls"], caps["retry"],
        b["total_calls"], caps["total"]))
    lines.append("")
    if result.get("limitations"):
        lines.append("## Limitations")
        for lim in result["limitations"]:
            lines.append("- {0}".format(lim))
        lines.append("")
    return "\n".join(lines) + "\n"


# --- Minimal JSON-schema validator (standard library only) ------------------


def validate_against_schema(instance, schema, path="$"):
    """A small deterministic validator for the subset of JSON Schema used by
    QuickCompare: type, required, properties, enum, items, additional..."""
    errors = []
    stype = schema.get("type")
    if stype == "object":
        if not isinstance(instance, dict):
            return ["{0}: expected object".format(path)]
        for key in schema.get("required", []):
            if key not in instance:
                errors.append("{0}.{1}: missing required".format(path, key))
        props = schema.get("properties", {})
        for key, subschema in props.items():
            if key in instance:
                errors.extend(validate_against_schema(
                    instance[key], subschema, "{0}.{1}".format(path, key)))
    elif stype == "array":
        if not isinstance(instance, list):
            return ["{0}: expected array".format(path)]
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors.extend(validate_against_schema(
                    item, item_schema, "{0}[{1}]".format(path, i)))
    elif stype == "string":
        if not isinstance(instance, str):
            errors.append("{0}: expected string".format(path))
    elif stype == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            errors.append("{0}: expected integer".format(path))
    elif stype == "number":
        if not isinstance(instance, (int, float)) or isinstance(instance, bool):
            errors.append("{0}: expected number".format(path))
    elif stype == "boolean":
        if not isinstance(instance, bool):
            errors.append("{0}: expected boolean".format(path))
    if "enum" in schema and instance not in schema["enum"]:
        errors.append("{0}: {1} not in enum".format(path, instance))
    return errors


# --- Calibration -------------------------------------------------------------


def _synthetic_result(fixture_id, pairwise, base_total, cand_total,
                      target=False, danger=False, protected=False):
    return {
        "fixture_id": fixture_id,
        "protected": protected,
        "target_family": target,
        "pairwise": pairwise,
        "baseline_behavioral_total": base_total,
        "candidate_behavioral_total": cand_total,
        "baseline_dimensions": {k: 0 for k in BEHAVIORAL_DIMS},
        "candidate_dimensions": {k: 0 for k in BEHAVIORAL_DIMS},
        "candidate_dangerous": danger,
        "baseline_dangerous": False,
        "material_win": pairwise == "CANDIDATE_WIN" and cand_total > base_total,
        "material_loss": pairwise == "BASELINE_WIN" and base_total > cand_total,
        "confidence": "high",
    }


def calibration_scenarios():
    """Four frozen synthetic scenarios, each exercising the single
    ``compute_verdict`` function -- no parallel verdict logic."""
    good_gates = {"identity": True, "symmetry": True, "blinding": True,
                  "budget": True, "schema": True, "calibration": True}
    protected_ok = [
        {"slot": PROTECTED_SLOTS[0], "valid": True, "result": "NO_LOSS", "win": True, "commitment": "x"},
        {"slot": PROTECTED_SLOTS[1], "valid": True, "result": "NO_LOSS", "win": False, "commitment": "y"},
    ]
    protected_absent = [
        {"slot": PROTECTED_SLOTS[0], "valid": False, "result": "ABSENT", "win": False, "commitment": None},
        {"slot": PROTECTED_SLOTS[1], "valid": False, "result": "ABSENT", "win": False, "commitment": None},
    ]

    improved = {
        "name": "known_improvement",
        "expected": "IMPROVED",
        "fixtures": [
            _synthetic_result("f1", "CANDIDATE_WIN", 4, 7, target=True),
            _synthetic_result("f2", "CANDIDATE_WIN", 5, 7),
            _synthetic_result("f3", "TIE", 6, 6),
        ],
        "protected": protected_ok,
        "gates": good_gates,
    }
    regressed = {
        "name": "known_regression",
        "expected": "REGRESSED",
        "fixtures": [
            _synthetic_result("f1", "BASELINE_WIN", 7, 3, danger=True),
            _synthetic_result("f2", "TIE", 6, 6),
        ],
        "protected": protected_ok,
        "gates": good_gates,
    }
    no_change = {
        "name": "identical_baseline_candidate",
        "expected": "NO_MATERIAL_CHANGE",
        "fixtures": [
            _synthetic_result("f1", "TIE", 6, 6),
            _synthetic_result("f2", "TIE", 5, 5),
        ],
        "protected": protected_ok,
        "gates": good_gates,
    }
    inconclusive = {
        "name": "incomplete_or_contradictory",
        "expected": "INCONCLUSIVE",
        "fixtures": [
            _synthetic_result("f1", "CANDIDATE_WIN", 4, 7, target=True),
            _synthetic_result("f2", "CANDIDATE_WIN", 5, 7),
        ],
        "protected": protected_absent,  # improvement blocked: no valid protected slots
        "gates": good_gates,
    }
    return [improved, regressed, no_change, inconclusive]


def run_calibration():
    results = []
    all_pass = True
    for scenario in calibration_scenarios():
        verdict, rule_path = compute_verdict(
            scenario["fixtures"], scenario["protected"], scenario["gates"])
        ok = verdict == scenario["expected"]
        all_pass = all_pass and ok
        results.append({
            "name": scenario["name"],
            "expected": scenario["expected"],
            "actual": verdict,
            "rule_path": rule_path,
            "pass": ok,
        })
    return {
        "schema_version": CALIBRATION_SCHEMA_VERSION,
        "all_pass": all_pass,
        "scenarios": results,
    }


# --- CLI ---------------------------------------------------------------------


def cmd_calibrate(args):
    report = run_calibration()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "calibration.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"all_pass": report["all_pass"],
                      "scenarios": [{"name": s["name"], "actual": s["actual"],
                                     "pass": s["pass"]} for s in report["scenarios"]]},
                     indent=2))
    return 0 if report["all_pass"] else 1


def cmd_run(args):
    config = load_json(args.config)
    output_dir = args.output_dir or config.get("output_dir")
    if not output_dir:
        sys.stderr.write("error: no output directory given\n")
        return 2
    try:
        result, _ = run_comparison(config, output_dir)
    except (KeyError, OSError, json.JSONDecodeError) as exc:
        sys.stderr.write("error: run failed: {0}\n".format(exc))
        return 2
    print("verdict: {0} ({1})".format(result["verdict"], result["verdict_rule_path"]))
    return 0


def cmd_validate(args):
    report = load_json(args.report)
    schema = load_json(args.schema or (REPO_ROOT / "harness" / "quickcompare.schema.json"))
    errors = validate_against_schema(report, schema)
    if errors:
        for err in errors:
            sys.stderr.write("schema error: {0}\n".format(err))
        return 1
    print("valid: comparison.json conforms to {0}".format(
        report.get("schema_version")))
    return 0


HELP_EPILOG = """\
Runner protocol (generic, shell-free):
  The harness invokes the generator and judge executables with an explicit
  argument vector (subprocess, shell=False). Each call receives one versioned
  JSON request on stdin and must emit exactly one versioned JSON object on
  stdout (no trailing content). stderr, return code, elapsed time, timeout,
  and byte hashes are captured. The judge request never carries baseline or
  candidate identity, artifact hashes, paths, or the target hypothesis.

Protected holdouts:
  Two slots -- protected_code_testing and protected_agent_security_procedure --
  are supplied at run time from outside Git via {path, commitment}. Their
  content is never written to comparison.json/.md; only slot id, commitment,
  validity, and aggregate loss/no-loss are reported. IMPROVED is impossible
  unless both slots are present, commitment-valid, and loss-free.

Budgets (eight-fixture full run): 16 generator, 8 judge, <=2 retry, 26 total.

Exit codes:
  0  command completed and produced a valid report (verdict may be REGRESSED,
     NO_MATERIAL_CHANGE, or INCONCLUSIVE);
  1  calibration failed / schema invalid;
  2  invalid configuration or execution failure preventing a valid report.
"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog="quickcompare",
        description="QuickCompare v1: a standard-library A/B harness for "
                    "Skeptic artifacts. Emits exactly one verdict "
                    "(IMPROVED / NO_MATERIAL_CHANGE / REGRESSED / INCONCLUSIVE).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HELP_EPILOG,
    )
    sub = parser.add_subparsers(dest="command")

    p_cal = sub.add_parser("calibrate",
                           help="Demonstrate all four verdict paths deterministically.")
    p_cal.add_argument("--output-dir", required=True)
    p_cal.set_defaults(func=cmd_calibrate)

    p_run = sub.add_parser("run", help="Run a full blinded A/B comparison.")
    p_run.add_argument("--config", required=True, help="Path to run.json.")
    p_run.add_argument("--output-dir", default=None)
    p_run.set_defaults(func=cmd_run)

    p_val = sub.add_parser("validate",
                           help="Validate a comparison.json against the schema.")
    p_val.add_argument("--report", required=True)
    p_val.add_argument("--schema", default=None)
    p_val.set_defaults(func=cmd_validate)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
