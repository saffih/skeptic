"""Build prompts for the Skeptic detection harness."""


def build_prompt(
    question_set: dict,
    artifact_content: str,
    artifact_name: str,
) -> tuple[str, str]:
    """Build system and user prompts for artifact analysis.

    Args:
        question_set: Dict with "description" and "questions" keys.
            questions is a dict mapping question IDs to question text.
        artifact_content: The full text content of the artifact to analyze.
        artifact_name: Filename or identifier for the artifact.

    Returns:
        Tuple of (system_prompt, user_prompt).
    """
    questions = question_set["questions"]
    set_description = question_set.get("description", "")

    system_prompt = f"""\
You are a code-analysis agent running a Skeptic detection pass.

Your task:
- Analyze the provided artifact using ONLY the provided questions.
- For each question, evaluate whether the artifact has issues, risks, or is clean.
- Output your analysis as structured JSON.

Output format — a JSON object with exactly two keys:

{{
  "findings": [
    {{
      "id": "F1",
      "description": "Short description of the issue",
      "location": "File, line range, or section where the issue exists",
      "classification": "ACTION | CONFLICT | PASS",
      "severity": "high | medium | low",
      "triggered_by": ["QID1", "QID2"],
      "evidence": "Concrete evidence from the artifact supporting this finding",
      "confidence": "high | medium | low"
    }}
  ],
  "clean_areas": [
    {{
      "area": "Description of clean area",
      "verified_by": ["QID1", "QID2"]
    }}
  ]
}}

Rules:
- classification must be one of: ACTION (fix needed), CONFLICT (decision needed), PASS (no issue).
- triggered_by must list the question IDs that surfaced the finding.
- Do not invent questions beyond those provided.
- Do not omit questions — if a question reveals no issue, note the area as clean.
- Be specific about location and evidence.
- Output ONLY the JSON object. No preamble, no markdown fences, no commentary.

Question set: {set_description}
"""

    question_list = "\n".join(
        f"  {qid}: {text}" for qid, text in sorted(questions.items())
    )

    user_prompt = f"""\
Analyze this artifact using the questions below.

### Artifact: `{artifact_name}`

```
{artifact_content}
```

### Questions

{question_list}
"""

    return system_prompt, user_prompt
