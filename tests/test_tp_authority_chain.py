"""Static contract tests for the three-level TP orientation chain.

These prove only the written contract, not model behavior.
"""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def raw(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def flat(path: str) -> str:
    return " ".join(raw(path).split())


class TpAuthorityChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agents_raw = raw("AGENTS.md")
        cls.agents = flat("AGENTS.md")
        cls.first = flat("MUST_READ_FIRST.md")
        cls.task = flat("workflows/task_prompt.md")
        cls.task_raw = raw("workflows/task_prompt.md")
        cls.brain = flat("agents/tp_brain.md")

    def test_agents_md_opens_with_the_must_read_first_pointer(self) -> None:
        self.assertTrue(
            self.agents_raw.startswith(
                "<!-- MUST READ FIRST -->\n"
                "Read `MUST_READ_FIRST.md` before routing or executing repository work.\n"
            ),
            "AGENTS.md must open with the MUST_READ_FIRST pointer",
        )

    def test_agents_md_is_a_router_for_tp_not_an_implementation(self) -> None:
        self.assertIn("This file is a router", self.agents)
        self.assertIn("read `workflows/task_prompt.md`, which is the complete and only TP authority", self.agents)
        # AGENTS.md must route, not restate any TP rule. Any imperative about
        # what the TP controller may read, persist, or dispatch belongs to
        # workflows/task_prompt.md, so no TP-rule vocabulary may appear here.
        # Naming the TP Brain role and where it is defined is routing; stating
        # what the controller may load, persist, read, or dispatch is not.
        for leaked in (
            "closed deterministic bootstrap",
            "TP Brain dispatch",
            "control authorities",
            "Read nothing task-specific",
            "persist",
            "before the first",
            "must not read",
        ):
            self.assertNotIn(leaked, self.agents)

    def test_agents_md_does_not_add_loads_to_the_closed_tp_bootstrap(self) -> None:
        # AGENTS.md obliges control planes to read context-stewardship; TP's
        # load set is closed, so the Task Prompt path must be exempted.
        self.assertIn(
            "This does not apply on the Task Prompt path, whose load set `workflows/task_prompt.md` closes.",
            self.agents,
        )

    def test_must_read_first_owns_only_universal_orientation(self) -> None:
        for phrase in (
            "Model context is scarce working capacity",
            "file-backed",
            "fresh bounded invocations",
            "may independently retrieve any source already authorized",
            "does not imply a shared contract",
            "`TP:` routes to `workflows/task_prompt.md`",
            "`RunSkeptic` routes to `skeptic.md`",
            "STT is a separate system",
            "`UNKNOWN`",
        ):
            self.assertIn(phrase, self.first)
        # It must stay an orientation file, not a second TP recipe.
        for leaked in ("work block", "TP Brain", "dispatch"):
            self.assertNotIn(leaked, self.first)

    def test_task_prompt_is_the_single_self_contained_tp_authority(self) -> None:
        self.assertIn("complete and only authority for the Task Prompt (TP) workflow", self.task)
        # Self-containment: TP states its own rules rather than deferring to
        # Planner, Validator, generic Lead, Boundary, or a return contract.
        for foreign in (
            "agents/planner.md",
            "agents/boundary_agent.md",
            "agents/agent_return_contract.md",
            "agents/lead_agent.md",
            "Agent Completion Envelope",
        ):
            self.assertNotIn(foreign, self.task)
        self.assertIn("TP has no Planner role and no Validator role.", self.task)

    def test_task_prompt_defines_one_compact_result_structure(self) -> None:
        # The return exists to carry mechanical control, not content: the
        # controller must be able to act on it without reading anything
        # substantive, and nothing substantive may ride along inline.
        self.assertIn("### TP result packet", self.task_raw)
        self.assertIn("TP_RESULT\ndispatch_id:", self.task_raw)
        for line in (
            "dispatch_id: <the identifier the controller issued>",
            "status: DONE | BLOCKED | CONFLICT",
            "result_ref: <receiver-resolvable reference to the durable artifact, or NONE>",
            "next: <block_ref> | BRAIN_REDISPATCH | MISSION_COMPLETE | NONE",
            "route: LOW | MEDIUM | STRONG | NONE",
        ):
            self.assertIn(line, self.task_raw)
        self.assertIn("`route` is the sole mechanically returned routing field", self.task)
        self.assertIn("ACTUAL_ROUTING_UNKNOWN", self.task)

    def test_old_verbose_result_packet_is_not_retained(self) -> None:
        # Requirement: exactly one runtime packet. The verbose fields must be
        # gone as packet members, not merely deprecated alongside the new one.
        self.assertIn("This is TP's only runtime return shape", self.task)
        self.assertIn(
            "`route` is the sole mechanically returned routing field",
            self.task,
        )
        for dropped in (
            "- `output` — resolvable references to durable artifacts it produced",
            "- `notes` — compact deviations, unknowns, and blockers",
            "- `routing` — requested model class and effort",
        ):
            self.assertNotIn(dropped, self.task_raw)

    def test_task_prompt_fixes_one_concrete_fresh_invocation_transport(self) -> None:
        self.assertIn("## Transport", self.task_raw)
        for phrase in (
            "actual new native subagent context",
            "launch fresh native subagent(role, route, effort, reference packet)",
            "The host supplies the native capability",
            "LOW = gpt-5.6-luna",
            "MEDIUM = gpt-5.6-terra",
            "STRONG = gpt-5.6-sol",
        ):
            self.assertIn(phrase, self.task)

    def test_no_claude_p_transport_fallback(self) -> None:
        # Provider-specific escape hatches are removed: an unavailable mapped
        # route must stop the run, not reroute it.
        self.assertNotIn("claude -p", self.task)
        self.assertNotIn("claude-p", self.task)
        self.assertNotIn("codex exec", self.task)
        self.assertIn(
            "no fallback model is substituted",
            self.task,
        )
        self.assertIn("`ROUTE_UNAVAILABLE`", self.task)
        self.assertIn(
            "then launches a fresh Brain at the current Brain route",
            self.task,
        )
        self.assertIn(
            "unavailable `gpt-5.6-luna` is not silently replaced by `gpt-5.6-terra`",
            self.task,
        )

    def test_brain_dispatch_packet_is_exactly_four_reference_fields(self) -> None:
        self.assertIn("TP_BRAIN\nworkflow_ref:", self.task_raw)
        for line in (
            "workflow_ref: <receiver-resolvable reference to workflows/task_prompt.md>",
            "intent_ref: <receiver-resolvable reference to the persisted verbatim TP intent>",
            "run_ref: <receiver-resolvable reference to run storage>",
            "dispatch_id: <mechanically generated identifier unique within this task>",
        ):
            self.assertIn(line, self.task_raw)
        # The reproduced failure was the controller expanding authority,
        # expected-result semantics, and schema prose into this very packet.
        self.assertIn(
            "No task body, authority body, prohibition list, schema prose, mission "
            "summary, expected-result prose, work-block definition, repository "
            "evidence, or other substantive content may be copied into the invocation",
            self.task,
        )
        self.assertIn("This is the whole packet; there is no optional extra field", self.task)
        self.assertIn("Brain resolves `workflow_ref` and `intent_ref` itself", self.task)
        # The superseded expanded dispatch fields must not survive anywhere.
        for dropped in (
            "- **admitted references** —",
            "- **authority** — this file's \"TP Brain\" section",
            "- **prohibitions** — this file's \"Brain boundaries\"",
            "- **expected result** — one TP result packet",
        ):
            self.assertNotIn(dropped, self.task_raw)

    def test_block_dispatch_packet_is_exactly_four_reference_fields(self) -> None:
        self.assertIn("TP_BLOCK\nworkflow_ref:", self.task_raw)
        for line in (
            "block_ref: <receiver-resolvable reference to the durable work-block artifact>",
            "run_ref: <receiver-resolvable reference to run storage>",
            "dispatch_id: <mechanically generated identifier unique within this task>",
        ):
            self.assertIn(line, self.task_raw)
        self.assertIn("The worker independently reads `workflow_ref` and `block_ref`", self.task)
        self.assertIn(
            "they are not copied through the controller and are not restated in the dispatch",
            self.task,
        )

    def test_first_brain_route_is_fixed_medium_with_no_task_body_override(self) -> None:
        self.assertIn(
            "The initial Brain route is always `MEDIUM`. Brain never starts at `LOW`.",
            self.task,
        )
        self.assertNotIn("unless the task input explicitly fixes a different Brain route", self.task)

    def test_brain_exposes_one_next_action_never_an_inline_block_list(self) -> None:
        self.assertIn(
            "Brain never returns an inline work-block list, an ordered set of blocks, "
            "an expanded block definition, or more than one block reference at a time",
            self.task,
        )
        self.assertIn(
            "Brain returns one TP result packet exposing exactly one next action and route",
            self.task,
        )
        self.assertIn(
            "a receiver-resolvable reference to a single durable work-block artifact",
            self.task,
        )
        # Substantive non-routing fields live in the artifact; route has one
        # separate mechanical source in TP_RESULT.
        self.assertIn(
            "The referenced work-block artifact — not the return, and not the dispatch — "
            "supplies every substantive non-routing value",
            self.task,
        )
        self.assertIn(
            "`TP_RESULT.route` is the single route and model selection for that block",
            self.task,
        )
        self.assertNotIn("from Brain it is either work blocks or `MISSION_COMPLETE`", self.task)

    def test_every_block_returns_to_a_fresh_brain(self) -> None:
        self.assertIn("Continuation is never deterministic beyond one step", self.task)
        self.assertIn(
            "After every work block, whatever its status, the controller dispatches "
            "a fresh Brain",
            self.task,
        )
        self.assertIn(
            "There is no case in which the controller advances to a following block "
            "on its own, because it was never given one",
            self.task,
        )
        self.assertIn(
            "This deliberately favors a simple domain-blind controller over reducing "
            "the number of Brain invocations",
            self.task,
        )
        self.assertIn("The controller holds no plan, no block queue", self.task)
        # The superseded deterministic-advance rule must be gone.
        self.assertNotIn("the next block in Brain's ordered set", self.task)

    def test_controller_may_not_read_task_specific_material_before_brain(self) -> None:
        for phrase in (
            "reading a file the task text names",
            "grepping or searching for a term the task text uses",
            "listing or inspecting history, plans, tests, or prior work",
            "composing a summary, restatement, decomposition, or work-block list",
        ):
            self.assertIn(phrase, self.task)

    def test_brain_must_delegate_rather_than_absorb_the_mission(self) -> None:
        self.assertIn("Brain must not absorb the whole mission into its own context", self.task)
        self.assertIn(
            "A MEDIUM Brain may request one fresh STRONG Brain with the same "
            "workflow, intent, and run references",
            self.task,
        )
        self.assertIn("after that escalation Brain cannot downgrade", self.task)
        self.assertIn("If a discovery or analysis step can be described well enough to delegate, it is delegated", self.task)

    def test_no_fallback_to_semantic_work_in_the_controller(self) -> None:
        self.assertIn("## When fresh invocation is impossible", self.task_raw)
        self.assertIn("It never falls back to performing the semantic work itself", self.task)

    def test_completion_is_split_between_brain_and_controller(self) -> None:
        self.assertIn("Semantic completion is Brain's decision", self.task)
        self.assertIn("Mechanical completion is the controller's", self.task)
        self.assertIn("The final transition of every TP run is therefore a Brain dispatch", self.task)
        self.assertIn("it does not declare completion on its own", self.task)

    def test_mission_completion_has_a_mechanical_representation(self) -> None:
        # The controller cannot inspect results, so "done" must be a value it
        # can read off the packet rather than a judgement it makes.
        self.assertIn("`MISSION_COMPLETE`", self.task)
        self.assertIn("`MISSION_COMPLETE` is the only way a TP run ends successfully, and only Brain may emit it", self.task)
        self.assertIn(
            "`next` carries a single block reference, `BRAIN_REDISPATCH`, or "
            "`MISSION_COMPLETE` only from Brain",
            self.task,
        )
        # ...and must not be contradicted by a blanket terminal-approval ban.
        self.assertNotIn("approve its own control state as terminal", self.task)

    def test_blocked_brain_stops_rather_than_promoting_the_controller(self) -> None:
        self.assertIn("When a Brain dispatch itself returns `BLOCKED` or `CONFLICT`", self.task)
        self.assertIn("the controller stops and reports the blocker", self.task)
        self.assertIn("it does not take over the judgement Brain declined to make", self.task)

    def test_deterministic_checks_are_bounded_children_too(self) -> None:
        self.assertIn(
            "Deterministic checks are work blocks like any other; the controller does not run them in its own context",
            self.task,
        )

    def test_controller_persists_exact_intent_outside_tracked_state(self) -> None:
        self.assertIn("writes the verbatim task text to a durable host-authorized file", self.task)
        self.assertIn("never edits, summarizes, or re-expresses the persisted text", self.task)
        self.assertIn("Run state is never written into tracked repository state", self.task)

    def test_substantial_material_moves_by_reference(self) -> None:
        self.assertIn(
            "Substantial objectives, sources, and results move by receiver-resolvable reference",
            self.task,
        )
        self.assertIn(
            "the controller never carries a substantive body through itself to hand to the next block",
            self.task,
        )

    def test_controller_reports_its_run(self) -> None:
        self.assertIn("The report states the objective reference, control identity, dispatches", self.task)
        self.assertIn("Hidden runtime facts are reported as `UNKNOWN`", self.task)

    def test_tp_brain_file_is_a_stub_without_authority(self) -> None:
        self.assertIn("TP Brain is defined by `workflows/task_prompt.md`", self.brain)
        self.assertIn("routing stub and carries no authority of its own", self.brain)

    def test_tp_and_stt_stay_separate_systems(self) -> None:
        self.assertIn("STT is a separate system", self.task)
        self.assertIn("TP neither defines nor redesigns it", self.task)


if __name__ == "__main__":
    unittest.main()
