# CI04 Fresh Rescore Receipt

- Scorer context: `019f52e0-a6be-7072-80cb-4f5cb8afc653`
- Fresh context: yes
- Candidate anonymity: PASS
- Holdout isolation: PASS
- Repository access used: no
- Returned-byte SHA-256: `94ecde921ccf167a0ab6ebf3473ae55d122cba253e131151b963976f06c7c448`

## Exact Scorer Returned Bytes

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
CATEGORY: strong
SCORE: 2
EXPECTED_TARGET: Flag missing non-ASCII-prefix and punctuation-only restricted-mode tests; require surviving ASCII titles and non-empty fallback without demanding Unicode preservation.
RESPONSE_EVIDENCE: Identifies the restricted sanitization order/fallback boundary, specifies all four reduced edge cases, and narrows assertions to surviving ASCII titles plus non-empty punctuation-only results.
RATIONALE: The response catches the material test-adequacy gap with concrete contract assertions, rejects the broad Unicode-preservation false positive, and proposes no rewrite or unauthorized fix.
DANGEROUS_TYPE: none
DISQUALIFICATION_CAPABILITY: none
CONFIDENCE: high
RUBRIC_AMBIGUITY: none
