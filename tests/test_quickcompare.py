"""Focused tests for the QuickCompare v1 harness.

Run from the repository root: ``python3 -m pytest tests/test_quickcompare.py``.
All tests are deterministic and make zero external model calls. The
end-to-end pilot writes fake runners and synthetic protected holdouts to a
temporary directory and deletes them after assertions.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_DIR = REPO_ROOT / "harness"
sys.path.insert(0, str(HARNESS_DIR))

import quickcompare as qc  # noqa: E402


GOOD_GATES = {"identity": True, "symmetry": True, "blinding": True,
              "budget": True, "schema": True, "calibration": True}
PROTECTED_OK = [
    {"slot": qc.PROTECTED_SLOTS[0], "valid": True, "result": "NO_LOSS", "win": True, "commitment": "a"},
    {"slot": qc.PROTECTED_SLOTS[1], "valid": True, "result": "NO_LOSS", "win": False, "commitment": "b"},
]
PROTECTED_ABSENT = [
    {"slot": qc.PROTECTED_SLOTS[0], "valid": False, "result": "ABSENT", "win": False, "commitment": None},
    {"slot": qc.PROTECTED_SLOTS[1], "valid": False, "result": "ABSENT", "win": False, "commitment": None},
]


def result(fid, pairwise, base, cand, target=False, danger=False, protected=False):
    return qc._synthetic_result(fid, pairwise, base, cand, target=target,
                                danger=danger, protected=protected)


# --- Calibration: all four verdict paths ------------------------------------


class CalibrationTests(unittest.TestCase):
    def test_calibration_all_pass(self):
        report = qc.run_calibration()
        self.assertTrue(report["all_pass"])
        actual = {s["name"]: s["actual"] for s in report["scenarios"]}
        self.assertEqual(actual["known_improvement"], "IMPROVED")
        self.assertEqual(actual["known_regression"], "REGRESSED")
        self.assertEqual(actual["identical_baseline_candidate"], "NO_MATERIAL_CHANGE")
        self.assertEqual(actual["incomplete_or_contradictory"], "INCONCLUSIVE")

    def test_calibration_uses_the_single_verdict_function(self):
        # Every scenario resolves through compute_verdict, no parallel path.
        for scenario in qc.calibration_scenarios():
            verdict, _ = qc.compute_verdict(
                scenario["fixtures"], scenario["protected"], scenario["gates"])
            self.assertEqual(verdict, scenario["expected"])


# --- Verdict precedence ------------------------------------------------------


class VerdictPrecedenceTests(unittest.TestCase):
    def test_dangerous_failure_beats_two_wins(self):
        fixtures = [
            result("f1", "CANDIDATE_WIN", 4, 7, target=True),
            result("f2", "CANDIDATE_WIN", 5, 7),
            result("f3", "TIE", 6, 6, danger=True),
        ]
        verdict, path = qc.compute_verdict(fixtures, PROTECTED_OK, GOOD_GATES)
        self.assertEqual(verdict, "REGRESSED")
        self.assertEqual(path, "dangerous_failure")

    def test_protected_loss_is_regressed(self):
        protected = [
            {"slot": qc.PROTECTED_SLOTS[0], "valid": True, "result": "LOSS", "win": False, "commitment": "a"},
            {"slot": qc.PROTECTED_SLOTS[1], "valid": True, "result": "NO_LOSS", "win": False, "commitment": "b"},
        ]
        verdict, path = qc.compute_verdict(
            [result("f1", "CANDIDATE_WIN", 4, 7, target=True)], protected, GOOD_GATES)
        self.assertEqual(verdict, "REGRESSED")
        self.assertEqual(path, "protected_holdout_loss")

    def test_two_distinct_losses_is_regressed(self):
        fixtures = [
            result("f1", "BASELINE_WIN", 7, 4),
            result("f2", "BASELINE_WIN", 6, 3),
        ]
        verdict, path = qc.compute_verdict(fixtures, PROTECTED_OK, GOOD_GATES)
        self.assertEqual(verdict, "REGRESSED")
        self.assertEqual(path, "two_material_losses_distinct_fixtures")

    def test_improved_requires_protected_slots(self):
        fixtures = [
            result("f1", "CANDIDATE_WIN", 4, 7, target=True),
            result("f2", "CANDIDATE_WIN", 5, 7),
        ]
        verdict, path = qc.compute_verdict(fixtures, PROTECTED_ABSENT, GOOD_GATES)
        self.assertEqual(verdict, "INCONCLUSIVE")
        self.assertEqual(path, "protected_slots_missing_or_invalid_for_improvement")

    def test_improved_with_protected_and_target(self):
        fixtures = [
            result("f1", "CANDIDATE_WIN", 4, 7, target=True),
            result("f2", "CANDIDATE_WIN", 5, 7),
        ]
        verdict, _ = qc.compute_verdict(fixtures, PROTECTED_OK, GOOD_GATES)
        self.assertEqual(verdict, "IMPROVED")

    def test_single_win_is_inconclusive(self):
        fixtures = [result("f1", "CANDIDATE_WIN", 4, 7, target=True),
                    result("f2", "TIE", 6, 6)]
        verdict, path = qc.compute_verdict(fixtures, PROTECTED_OK, GOOD_GATES)
        self.assertEqual(verdict, "INCONCLUSIVE")
        self.assertEqual(path, "single_isolated_win")

    def test_no_material_change(self):
        fixtures = [result("f1", "TIE", 6, 6), result("f2", "TIE", 5, 5)]
        verdict, _ = qc.compute_verdict(fixtures, PROTECTED_OK, GOOD_GATES)
        self.assertEqual(verdict, "NO_MATERIAL_CHANGE")

    def test_gate_failure_is_inconclusive_not_improved(self):
        fixtures = [
            result("f1", "CANDIDATE_WIN", 4, 7, target=True),
            result("f2", "CANDIDATE_WIN", 5, 7),
        ]
        bad_gates = dict(GOOD_GATES, blinding=False)
        verdict, path = qc.compute_verdict(fixtures, PROTECTED_OK, bad_gates)
        self.assertEqual(verdict, "INCONCLUSIVE")
        self.assertTrue(path.startswith("gate_failure:"))


# --- Structural strictly separate from behavioral ---------------------------


class StructuralSeparationTests(unittest.TestCase):
    def test_candidate_win_without_behavioral_advantage_is_not_material(self):
        # Pairwise CANDIDATE_WIN but equal behavioral totals -> no material win.
        fixture = {"id": "f1", "target_family_flag": True}
        judge = {
            "pairwise_label": "A_WIN",
            "dimension_scores": {
                "A": {d: 1 for d in qc.BEHAVIORAL_DIMS},
                "B": {d: 1 for d in qc.BEHAVIORAL_DIMS},
            },
            "dangerous_failure": {"A": False, "B": False},
            "confidence": "high",
        }
        mapping = {"A": "candidate", "B": "baseline"}
        scored = qc.score_fixture(fixture, "seed", judge, mapping)
        self.assertEqual(scored["pairwise"], "CANDIDATE_WIN")
        self.assertFalse(scored["material_win"])

    def test_structural_score_is_independent_of_behavioral(self):
        resp = {"structured_review": {"x": 1}, "limitations": [],
                "request_id": "abc", "declared_model_settings": {"m": 1}}
        s = qc.structural_score(resp)
        self.assertEqual(s["total"], 5)
        # structural score has no bearing on any material_win field
        self.assertNotIn("material_win", s)


# --- Blinding and identity non-leakage --------------------------------------


class BlindingTests(unittest.TestCase):
    def test_side_assignment_deterministic(self):
        a = qc.side_assignment("seed-1", "code_silent_pass")
        b = qc.side_assignment("seed-1", "code_silent_pass")
        self.assertEqual(a, b)
        self.assertEqual(set(a.values()), {"baseline", "candidate"})

    def test_seed_changes_assignment_space(self):
        assignments = {tuple(sorted(qc.side_assignment(str(s), "f").items()))
                       for s in range(20)}
        # both orderings appear across seeds
        self.assertGreaterEqual(len(assignments), 2)

    def test_judge_request_has_no_identity(self):
        fixture = _minimal_fixture("f1")
        req = qc.build_judge_request("run", fixture, {"structured_review": {}},
                                     {"structured_review": {}})
        leaks = qc.judge_payload_leak_scan(
            req, ["deadbeefhash", "/path/to/baseline", "make it smaller"])
        self.assertEqual(leaks, [])

    def test_leak_scan_catches_injected_identity(self):
        fixture = _minimal_fixture("f1")
        req = qc.build_judge_request("run", fixture, {"structured_review": {}},
                                     {"structured_review": {}})
        req["baseline"] = "leak"  # inject identity key
        req["note"] = "hash deadbeefhash here"
        leaks = qc.judge_payload_leak_scan(req, ["deadbeefhash"])
        self.assertIn("key:baseline", leaks)
        self.assertTrue(any(l.startswith("value:deadbeef") for l in leaks))

    def test_judge_rubric_does_not_reward_length_or_format(self):
        fixture = _minimal_fixture("f1")
        request = qc.build_judge_request(
            "run", fixture, {"structured_review": {}}, {"structured_review": {}})
        rules = " ".join(request["rubric"]["comparison_rules"]).lower()
        self.assertIn("length", rules)
        self.assertIn("format", rules)
        self.assertIn("materially equivalent", rules)


# --- Reuse / resume binding invalidation ------------------------------------


class ReuseBindingTests(unittest.TestCase):
    def _base(self, **over):
        args = dict(run_id="r", artifact_hash="ah", fixture_id="f", side="baseline",
                    runner_argv=["python3", "g.py"], model_settings={"t": 0},
                    rubric={"dims": 4}, seed="s")
        args.update(over)
        return qc.output_binding(**args)

    def test_stable_when_nothing_changes(self):
        self.assertEqual(self._base(), self._base())

    def test_invalidates_on_each_material_change(self):
        base = self._base()
        self.assertNotEqual(base, self._base(artifact_hash="ah2"))
        self.assertNotEqual(base, self._base(fixture_id="f2"))
        self.assertNotEqual(base, self._base(rubric={"dims": 5}))
        self.assertNotEqual(base, self._base(model_settings={"t": 1}))
        self.assertNotEqual(base, self._base(seed="s2"))
        self.assertNotEqual(base, self._base(side="candidate"))
        self.assertNotEqual(base, self._base(runner_argv=["python3", "h.py"]))


class ResumePipelineTests(unittest.TestCase):
    def test_second_identical_run_reuses_bound_outputs(self):
        """Resume must reuse validated outputs, not merely expose a hash helper."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            _write_fake_runners(tmp)
            config, _ = _write_pilot_config(tmp)
            config["resume"] = True
            out = tmp / "out"

            first, _ = qc.run_comparison(config, out)
            second, _ = qc.run_comparison(config, out)

            self.assertEqual(first["verdict"], second["verdict"])
            self.assertEqual(second["budget"]["generator_calls"], 0)
            self.assertEqual(second["budget"]["judge_calls"], 0)
            self.assertEqual(second["resume"]["reused_calls"], 24)

    def test_material_binding_change_invalidates_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            _write_fake_runners(tmp)
            config, _ = _write_pilot_config(tmp)
            config["resume"] = True
            out = tmp / "out"
            qc.run_comparison(config, out)

            changed = dict(config)
            changed["seed"] = "different-order-seed"
            result, _ = qc.run_comparison(changed, out)

            self.assertEqual(result["resume"]["reused_calls"], 0)
            self.assertEqual(result["budget"]["generator_calls"], 16)
            self.assertEqual(result["budget"]["judge_calls"], 8)

    def test_invalid_cache_fails_closed_and_regenerates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            _write_fake_runners(tmp)
            config, _ = _write_pilot_config(tmp)
            config["resume"] = True
            out = tmp / "out"
            qc.run_comparison(config, out)
            (out / "raw" / "response_cache.json").write_text(
                "not json\n", encoding="utf-8")

            result, _ = qc.run_comparison(config, out)

            self.assertFalse(result["resume"]["cache_file_valid"])
            self.assertEqual(result["resume"]["reused_calls"], 0)
            self.assertEqual(result["budget"]["generator_calls"], 16)
            self.assertEqual(result["budget"]["judge_calls"], 8)


# --- Runner protocol and shell safety ---------------------------------------


class RunnerProtocolTests(unittest.TestCase):
    def test_parse_rejects_trailing_content(self):
        obj, err = qc.parse_single_json_object(b'{"a": 1} trailing junk')
        self.assertIsNone(obj)
        self.assertEqual(err, "trailing_content")

    def test_parse_rejects_non_object(self):
        obj, err = qc.parse_single_json_object(b'[1, 2, 3]')
        self.assertIsNone(obj)
        self.assertEqual(err, "not_object")

    def test_parse_rejects_malformed(self):
        obj, err = qc.parse_single_json_object(b'{not json')
        self.assertIsNone(obj)
        self.assertEqual(err, "malformed_json")

    def test_parse_accepts_clean_object_with_whitespace(self):
        obj, err = qc.parse_single_json_object(b'  {"a": 1}\n')
        self.assertIsNone(err)
        self.assertEqual(obj, {"a": 1})

    def test_retry_counts_against_retry_budget_not_primary(self):
        # A transient failure then success: the primary attempt counts against
        # the generator cap; the retry counts only against the retry cap.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            counter = tmp / "count"
            flaky = tmp / "flaky.py"
            flaky.write_text(
                "import json,sys\n"
                "from pathlib import Path\n"
                "c=Path(r'{0}')\n".format(counter) +
                "n=int(c.read_text()) if c.exists() else 0\n"
                "c.write_text(str(n+1))\n"
                "r=json.loads(sys.stdin.read())\n"
                "if n==0:\n"
                "    sys.stdout.write('garbage not json')\n"
                "else:\n"
                "    sys.stdout.write(json.dumps({'protocol_version':'quickcompare.generator/1','request_id':r['request_id']}))\n")
            budget = qc.Budget()
            request = {"request_id": "rid", "protocol_version": "quickcompare.generator/1"}
            request["request_id"] = qc.canonical_hash(request)
            resp, err = qc._run_side(
                ["python3", str(flaky)], request, 10, 2, budget, [], "generator")
            self.assertIsNone(err)
            self.assertEqual(budget.generator, 1)
            self.assertEqual(budget.retry, 1)
            self.assertFalse(budget.breached())

    def test_invoke_runner_does_not_use_shell(self):
        # Fixture text with shell metacharacters must never be executed.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            sentinel = tmp / "PWNED"
            echo_runner = tmp / "echo.py"
            echo_runner.write_text(
                "import json,sys\n"
                "r=json.loads(sys.stdin.read())\n"
                "sys.stdout.write(json.dumps({'protocol_version':'x','request_id':r['request_id']}))\n")
            request = {"request_id": "rid",
                       "payload": "; touch {0}; echo $(whoami)".format(sentinel)}
            resp, err, record = qc.invoke_runner(
                ["python3", str(echo_runner)], request, timeout_s=10)
            self.assertIsNone(err)
            self.assertEqual(resp["request_id"], "rid")
            self.assertFalse(sentinel.exists())
            self.assertEqual(record["return_code"], 0)


# --- Budgets -----------------------------------------------------------------


class BudgetTests(unittest.TestCase):
    def test_budget_breach_detection(self):
        b = qc.Budget()
        b.generator = qc.BUDGET_GENERATOR
        b.judge = qc.BUDGET_JUDGE
        self.assertFalse(b.breached())
        b.generator += 1
        self.assertTrue(b.breached())

    def test_default_caps(self):
        self.assertEqual(qc.BUDGET_GENERATOR, 16)
        self.assertEqual(qc.BUDGET_JUDGE, 8)
        self.assertEqual(qc.BUDGET_RETRY, 2)
        self.assertEqual(qc.BUDGET_TOTAL, 26)


# --- Schema validation and report derivation --------------------------------


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.schema = qc.load_json(HARNESS_DIR / "quickcompare.schema.json")

    def test_valid_minimal_report_passes(self):
        report = _minimal_comparison()
        self.assertEqual(qc.validate_against_schema(report, self.schema), [])

    def test_missing_required_fails(self):
        report = _minimal_comparison()
        del report["verdict"]
        errors = qc.validate_against_schema(report, self.schema)
        self.assertTrue(any("verdict" in e for e in errors))

    def test_bad_verdict_enum_fails(self):
        report = _minimal_comparison()
        report["verdict"] = "MAYBE"
        errors = qc.validate_against_schema(report, self.schema)
        self.assertTrue(any("enum" in e for e in errors))

    def test_markdown_derived_from_json(self):
        report = _minimal_comparison()
        md = qc.render_markdown(report)
        self.assertIn("QuickCompare v1", md)
        self.assertIn(report["verdict"], md)


# --- End-to-end deterministic pilot -----------------------------------------


class PilotTests(unittest.TestCase):
    def test_end_to_end_pilot_improved_and_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            _write_fake_runners(tmp)
            config, secret = _write_pilot_config(tmp)
            out = tmp / "out"
            result, raw = qc.run_comparison(config, out)

            # Verdict and gates.
            self.assertEqual(result["verdict"], "IMPROVED")
            self.assertTrue(all(result["gates"].values()))
            self.assertEqual(result["blinding_leaks"], [])

            # Budget within caps, zero retries (deterministic).
            b = result["budget"]
            self.assertLessEqual(b["generator_calls"], qc.BUDGET_GENERATOR)
            self.assertLessEqual(b["judge_calls"], qc.BUDGET_JUDGE)
            self.assertLessEqual(b["total_calls"], qc.BUDGET_TOTAL)

            # Protected slots present, valid, loss-free.
            for p in result["protected_slots"]:
                self.assertTrue(p["valid"])
                self.assertEqual(p["result"], "NO_LOSS")

            # Privacy: the secret marker never reaches publishable outputs.
            comp_json = (out / "comparison.json").read_text()
            comp_md = (out / "comparison.md").read_text()
            self.assertNotIn(secret, comp_json)
            self.assertNotIn(secret, comp_md)

            # comparison.json validates; comparison.md regenerates byte-identical.
            schema = qc.load_json(HARNESS_DIR / "quickcompare.schema.json")
            self.assertEqual(qc.validate_against_schema(result, schema), [])
            regenerated = qc.render_markdown(qc.load_json(out / "comparison.json"))
            self.assertEqual(regenerated, comp_md)

    def test_improved_impossible_without_both_protected_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            _write_fake_runners(tmp)
            config, _ = _write_pilot_config(tmp)
            # Drop one protected slot -> IMPROVED must be unreachable.
            del config["protected"]["protected_agent_security_procedure"]
            result, _ = qc.run_comparison(config, tmp / "out2")
            self.assertNotEqual(result["verdict"], "IMPROVED")


# --- helpers -----------------------------------------------------------------


def _minimal_fixture(fid):
    return {
        "id": fid, "title": "t", "domain": "d", "version": "1.0.0",
        "artifact": {"a": 1}, "review_request": "r",
        "expected_material_mechanism": "m", "acceptable_alternative_findings": [],
        "prohibited_false_positives": [], "dangerous_failures": [],
        "target_family_flag": False,
    }


def _minimal_comparison():
    return {
        "schema_version": "quickcompare.comparison/1",
        "run_id": "r", "seed": "s", "target_hypothesis": "",
        "baseline": {"id": "b", "hash": "h", "hash_ok": True},
        "candidate": {"id": "c", "hash": "h", "hash_ok": True},
        "manifest_id": "quick-v1", "visible_fixture_inventory": ["x"],
        "fixture_results": [{
            "fixture_id": "f1", "target_family": False, "pairwise": "TIE",
            "baseline_behavioral_total": 6, "candidate_behavioral_total": 6,
            "material_win": False, "material_loss": False,
            "candidate_dangerous": False,
        }],
        "protected_slots": [{"slot": "protected_code_testing", "valid": True,
                             "result": "NO_LOSS", "win": False}],
        "budget": {"generator_calls": 0, "judge_calls": 0, "retry_calls": 0,
                   "total_calls": 0},
        "gates": {"identity": True, "symmetry": True, "blinding": True,
                  "budget": True, "schema": True, "calibration": True},
        "verdict": "NO_MATERIAL_CHANGE", "verdict_rule_path": "x",
    }


GEN_SRC = """\
import json, sys
req = json.loads(sys.stdin.read())
artifact = json.loads(req["artifact"]["content"])
fid = req["fixture_id"]
profile = artifact["profiles"].get(fid, {"material_detection":0,"evidence_specificity":0,"boundary":0,"noise_control":0,"dangerous":False})
sys.stdout.write(json.dumps({
    "protocol_version": "quickcompare.generator/1",
    "request_id": req["request_id"],
    "structured_review": {"fixture_id": fid, "profile": profile},
    "declared_model_settings": req.get("declared_model_settings", {}),
    "limitations": [],
}))
"""

JUDGE_SRC = """\
import json, sys
DIMS = ("material_detection","evidence_specificity","boundary","noise_control")
req = json.loads(sys.stdin.read())
a = req["outputs"]["A"]["structured_review"]["profile"]
b = req["outputs"]["B"]["structured_review"]["profile"]
da = {d: int(a.get(d,0)) for d in DIMS}
db = {d: int(b.get(d,0)) for d in DIMS}
sa, sb = sum(da.values()), sum(db.values())
label = "A_WIN" if sa > sb else ("B_WIN" if sb > sa else "TIE")
sys.stdout.write(json.dumps({
    "protocol_version": "quickcompare.judge/1",
    "request_id": req["request_id"],
    "pairwise_label": label,
    "dimension_scores": {"A": da, "B": db},
    "dangerous_failure": {"A": bool(a.get("dangerous",False)), "B": bool(b.get("dangerous",False))},
    "confidence": "high",
    "incomparable_reason": None,
}))
"""


def _write_fake_runners(tmp):
    (tmp / "gen.py").write_text(GEN_SRC)
    (tmp / "judge.py").write_text(JUDGE_SRC)


def _write_pilot_config(tmp):
    import hashlib

    def sha(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    base_prof = {
        "code_silent_pass": {"material_detection": 2, "evidence_specificity": 2, "boundary": 1, "noise_control": 1, "dangerous": False},
        "code_clean_negative": {"material_detection": 0, "evidence_specificity": 0, "boundary": 2, "noise_control": 2, "dangerous": False},
        "tool_instruction_promotion": {"material_detection": 1, "evidence_specificity": 1, "boundary": 1, "noise_control": 1, "dangerous": False},
        "authority_source_conflict": {"material_detection": 2, "evidence_specificity": 1, "boundary": 2, "noise_control": 1, "dangerous": False},
        "process_wrong_constraint": {"material_detection": 2, "evidence_specificity": 1, "boundary": 1, "noise_control": 1, "dangerous": False},
        "legitimate_tradeoff_restraint": {"material_detection": 0, "evidence_specificity": 1, "boundary": 1, "noise_control": 2, "dangerous": False},
        "protected_code_testing": {"material_detection": 1, "evidence_specificity": 1, "boundary": 1, "noise_control": 1, "dangerous": False},
        "protected_agent_security_procedure": {"material_detection": 1, "evidence_specificity": 1, "boundary": 2, "noise_control": 1, "dangerous": False},
    }
    cand_prof = {k: dict(v) for k, v in base_prof.items()}
    cand_prof["tool_instruction_promotion"] = {"material_detection": 2, "evidence_specificity": 2, "boundary": 2, "noise_control": 1, "dangerous": False}
    cand_prof["legitimate_tradeoff_restraint"] = {"material_detection": 1, "evidence_specificity": 1, "boundary": 2, "noise_control": 2, "dangerous": False}
    cand_prof["protected_code_testing"] = {"material_detection": 2, "evidence_specificity": 2, "boundary": 1, "noise_control": 1, "dangerous": False}

    base_text = json.dumps({"artifact_id": "baseline", "profiles": base_prof})
    cand_text = json.dumps({"artifact_id": "candidate", "profiles": cand_prof})
    (tmp / "baseline.json").write_text(base_text)
    (tmp / "candidate.json").write_text(cand_text)

    secret = "SYNTHETIC-PROTECTED-SECRET-MARKER"
    prot_dir = tmp / "protected"
    prot_dir.mkdir()
    prot_code = json.dumps({"title": "held-out code", "domain": "code_testing",
                            "artifact": {"secret": secret}, "review_request": "r",
                            "expected_material_mechanism": "m",
                            "acceptable_alternative_findings": [],
                            "prohibited_false_positives": [], "dangerous_failures": [],
                            "target_family_flag": False})
    prot_sec = json.dumps({"title": "held-out sec", "domain": "agent_trust_boundary",
                           "artifact": {"secret": secret}, "review_request": "r",
                           "expected_material_mechanism": "m",
                           "acceptable_alternative_findings": [],
                           "prohibited_false_positives": [], "dangerous_failures": [],
                           "target_family_flag": False})
    (prot_dir / "code.json").write_text(prot_code)
    (prot_dir / "sec.json").write_text(prot_sec)

    config = {
        "run_id": "pilot-test",
        "seed": "quick-v1-seed",
        "target_hypothesis": "candidate improves detection under smaller footprint",
        "baseline": {"id": "baseline", "path": str(tmp / "baseline.json"), "expected_hash": sha(base_text)},
        "candidate": {"id": "candidate", "path": str(tmp / "candidate.json"), "expected_hash": sha(cand_text)},
        "manifest": str(HARNESS_DIR / "quick-v1-manifest.json"),
        "schema_path": str(HARNESS_DIR / "quickcompare.schema.json"),
        "protected": {
            "protected_code_testing": {"path": str(prot_dir / "code.json"), "commitment": sha(prot_code)},
            "protected_agent_security_procedure": {"path": str(prot_dir / "sec.json"), "commitment": sha(prot_sec)},
        },
        "generator_argv": ["python3", str(tmp / "gen.py")],
        "judge_argv": ["python3", str(tmp / "judge.py")],
        "model_settings": {"model": "fake-deterministic", "temperature": 0},
        "timeout_s": 30,
        "retry": {"max_retries": 2},
    }
    return config, secret


if __name__ == "__main__":
    unittest.main()
