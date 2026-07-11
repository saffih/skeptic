# CI04 Fresh Adjudication Receipt

- Adjudicator context: `019f52e1-b67e-7d11-a1a9-063c951555dc`
- Fresh context: yes
- Separate from scorer: yes
- Candidate anonymity: PASS
- Holdout isolation: PASS
- Repository access used: no
- Returned-byte SHA-256: `b31285cf69a7e453869993ed6470dd83696e0de082a35e497b07f3460f8b6c85`

## Exact Adjudicator Returned Bytes

FRESH_CONTEXT: yes
NOT_DENYLISTED: yes
CANDIDATE_IDENTITY_KNOWN: no
PREVIOUS_CI04_SCORE_KNOWN: no
PREVIOUS_AGGREGATE_KNOWN: no
ORIGINAL_REPORT_READ: no
ORIGINAL_LEDGER_READ: no
DEFECT_AUDIT_READ: no
OTHER_CANDIDATE_RESULT_READ: no
HOLDOUT_CONTENT_READ: no
REPOSITORY_ACCESS_USED: no
FIXTURE_ID: CI04
PRIMARY_CATEGORY: strong
PRIMARY_SCORE: 2
ADJUDICATED_CATEGORY: strong
ADJUDICATED_SCORE: 2
AGREEMENT: yes
FINAL_CATEGORY: strong
FINAL_SCORE: 2
RATIONALE: The response identifies the material restricted-mode boundary: sanitization must preserve surviving ASCII titles after dropping non-ASCII prefixes and stripping separators, while punctuation-only inputs require a non-empty fallback. It supplies contract-level assertions for all four reduced edge cases, explicitly avoids the false positive of requiring Unicode preservation or transliteration, stays focused on test adequacy, and proposes no unauthorized fix.
RUBRIC_AMBIGUITY: none
