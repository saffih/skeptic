import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_target_task_smoke import SmokeError, parse_agent_transcript


def stream(*events):
    return b"".join(json.dumps(event, separators=(",", ":")).encode() + b"\n" for event in events)


class SmokeTranscriptTests(unittest.TestCase):
    def write(self, raw):
        handle = tempfile.NamedTemporaryFile(delete=False)
        handle.write(raw)
        handle.close()
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return Path(handle.name)

    def valid(self):
        events = []
        for number, role in enumerate(("target-task-planner", "target-task-reviewer", "target-task-worker"), 1):
            tool_id = f"agent-{number}"
            events.extend((
                {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": tool_id, "name": "Agent", "input": {"subagent_type": role}}]}},
                {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": tool_id, "content": [{"type": "text", "text": '{"status":"COMPLETE","summary":"receipt-only"}'}]}]}},
            ))
        return self.write(stream(*events))

    def test_valid_synthetic_stream_has_all_roles_and_correlated_results(self):
        result = parse_agent_transcript(self.valid())
        self.assertEqual(result["roles"], ["target-task-planner", "target-task-reviewer", "target-task-worker"])
        self.assertEqual(result["agent_calls"], 3)

    def test_nonempty_final_output_without_agent_calls_fails(self):
        path = self.write(stream({"type": "result", "result": "hello"}))
        with self.assertRaises(SmokeError):
            parse_agent_transcript(path)

    def test_fabricated_receipts_without_transcript_calls_fail(self):
        path = self.write(stream({"type": "result", "result": '{"status":"COMPLETE","receipt":"fabricated"}'}))
        with self.assertRaises(SmokeError):
            parse_agent_transcript(path)

    def test_unknown_or_ambiguous_agent_role_fails(self):
        path = self.write(stream(
            {"type": "tool_use", "id": "a", "name": "Agent", "input": {"subagent_type": "reviewer"}},
        ))
        with self.assertRaises(SmokeError):
            parse_agent_transcript(path)

    def test_oversized_or_body_bearing_result_fails(self):
        oversized = self.write(stream(
            {"type": "tool_use", "id": "a", "name": "Agent", "input": {"subagent_type": "target-task-planner"}},
            {"type": "tool_result", "tool_use_id": "a", "content": "x" * 5000},
        ))
        with self.assertRaises(SmokeError):
            parse_agent_transcript(oversized)
        body = self.write(stream(
            {"type": "tool_use", "id": "a", "name": "Agent", "input": {"subagent_type": "target-task-planner"}},
            {"type": "tool_result", "tool_use_id": "a", "content": [{"type": "json", "value": {"body": "plan body"}}]},
        ))
        with self.assertRaises(SmokeError):
            parse_agent_transcript(body)


if __name__ == "__main__":
    unittest.main()
