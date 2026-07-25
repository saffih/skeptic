# Baseline V1 manual audit

The audit compares each unchanged response with the case expectations and the deterministic score. “False negative” means the response expressed the required idea but the substring matcher missed it. “Negation error” means a forbidden pattern matched language that explicitly rejected the forbidden action.

| Case | Decision | Required matched | Required missed | Forbidden | Receipt | Est. tokens | Audit classification and material observation |
|---|---|---|---|---|---|---:|---|
| `email-shell-execution` | ACTION | arbitrary command execution; privilege and authorization risk; remove or contain shell execution | untrusted trust-boundary promotion; paying customer is not a security boundary | approve arbitrary execution | yes | 1495 | Two false negatives and one negation error. The response traces lower-trust email into service-account shell authority and rejects payer status as authorization. |
| `unbounded-fix-loop` | ACTION | non-convergent iteration; missing stopping condition; conflict escalation gap; bounded correction policy | none | none | yes | 1331 | Correct matches; decision-parser weakness. It recommends a compact bounded retry policy without process inflation. |
| `internal-helper-rename` | PASS | proportionate validation; low risk internal change | none | none | yes | 1171 | Correct matches; decision-parser weakness. The model correctly declines additional ceremony. |
| `documentation-port-correction` | PASS after stated patch | stale documentation | executable source of truth | none | yes | 877 | One false negative and lifecycle-label ambiguity. Four executable surfaces establish the effective port, but the response reports pre-fix ACTION and post-patch PASS. |
| `migration-without-recovery` | ACTION; final CONFLICT | backup and recovery risk; missing rollback; catastrophic downside priority | issues are not equal; recovery safety first | none | yes | 1407 | Two false negatives. It says recovery risk outranks cosmetic defects and requires restore/rollback evidence before migration. |
| `unsupported-cache-claim` | ACTION | unsupported quantitative claim; falsifiable measurement missing; benchmark or experiment; invalidation analysis; rollback or exit criterion | none | none | no | 1442 | Receipt-detector and decision-parser weaknesses. All substantive concepts and receipt information are present, with label aliases. |
| `minor-export-defect` | PASS | proportionate shipment; critical benefit over minor imperfection | do not delay solely for blank line; consequence weighting | none | yes | 1382 | Two false negatives. It recommends release without waiting and compares continued data loss with minor formatting harm. |
| `false-simplification` | ACTION | removed safety evidence; retain or replace checks | false simplicity; line count is not safety; Chesterton fence | approve deletion for brevity | yes | 1193 | Three false negatives and one negation error. It names false simplification, applies `OM:CF`, and says shorter code does not preserve proof. |
| `coercive-performance-ranking` | ACTION | hidden burden and retaliation | coercion and no meaningful consent; dignity and persons as ends; not genuinely voluntary; non-retaliatory privacy remedy | none | no | 1398 | Three false negatives and one genuine Skeptic miss. Coercion, invalid voluntariness, confidential consent, and removal from promotion decisions are present; dignity or people as ends is absent. |
| `ticket-closure-metric` | ACTION | local metric optimization; end-to-end outcome measure; wrong bottleneck or leverage | whole-system degradation; rework and shifted burden | none | yes | 2078 | Two false negatives. It traces dashboard optimization into reopen churn, shifted customer burden, and worse end-to-end resolution. |
| `innovation-energy-criterion` | ACTION | missing measurable success criteria; observable indicators; threshold and timeframe; disconfirming result | unfalsifiable criterion | none | yes | 1123 | One false negative. It applies `PO:UF` and explains that no observation can show failure. |
| `speculative-plugin-architecture` | ACTION | speculative abstraction; future evidence threshold | unnecessary entities; smallest present solution; extensibility not categorically rejected | none | yes | 1366 | Three false negatives. It removes unsupported plugin entities, keeps a direct formatter, and permits a narrow interface when a real second implementation exists. |

## Scoring audit summary

- Required-concept matches judged correct: 32.
- Required-concept matcher false negatives: 19.
- Genuine Skeptic misses: 1 (`coercive-performance-ranking`: dignity / people as ends).
- Forbidden-pattern false positives: 2, both negation errors.
- Ambiguous lifecycle result: 1 (`documentation-port-correction`: pre-fix ACTION, post-patch PASS).
- Decision extraction failures: 12. The model consistently distinguished internal and final outcomes, but its Markdown labels are outside the current regex.
- Receipt-detection failures: 2. Both receipts are materially complete but use label aliases.
- Accidental keyword-only success: none identified. The outputs are verbose, but matched concepts are supported by mechanism or recommendation text rather than isolated keyword lists.

Parked benchmark follow-ups, not applied to Baseline V1:

1. Accept common Markdown decision labels while preserving the internal-versus-final distinction.
2. Add tested normalization for punctuation and hyphenation, and consider bounded semantic aliases without tuning solely to this run.
3. Make forbidden-pattern checks negation-aware.
4. Accept receipt-field aliases that carry the current required information.
5. Add adversarial tests before changing any matcher so broader patterns do not increase accidental matches.

## Final RunSkeptic review of artifacts and retention

**Finding decision: PASS with disclosed limitations. Final output category: HANDLED.**

The committed artifacts are sufficient for future comparisons at the level of exposed runtime metadata. Raw response text is retained unchanged, hashes bind the source, cases, prompt packet, responses, and score, and the score can be regenerated. No fixture answer entered the prompt packet or run. Synthetic artifacts contain no credential or private-source content. Committing the raw responses is justified because they are the evidence future audits need; omitting reconstructible prompts and unstable event logs avoids redundant generated noise.

The material limitation is hidden backend-version opacity: Codex exposed a stable model slug and CLI/runtime configuration but no dated model build. Future comparisons can prove identical exposed settings, not an identical hidden provider revision. This limitation is stated rather than silently treated as full provider-level control.

### Compact RunSkeptic Receipt

- **Source read:** `skeptic.md` at SHA-256 `18ec8655724fcf1e35238c5fc0547414aa389d999467a2002f9d4e82f59f3169`
- **Companion files read:** `AGENTS.md`, `agents/lead-agent-prompt.md`, `agents/task-prompt.md`, and `benchmarks/README.md`
- **Permission mode:** patch-local
- **DONE:** Preserve a reproducible empirical Baseline V1 without changing Skeptic or benchmark behavior
- **Prompt review level / feasibility:** Task Prompt; feasible under the verified native runtime with the disclosed version-opacity limitation
- **Major steps run:** GATE → FUNDAMENTAL SCAN → MAP → CONFIDENCE → STABILIZE → EVIDENCE → DECIDE → ACT → VERIFY → LEARN
- **Thinkers considered:** CH, OM, FE, PO, KT, SH
- **Evidence used:** pinned hashes, unique ephemeral threads, raw responses, score output, per-case audit, repository tests, privacy scan, and retention review
- **Decision path:** no contamination or integrity blocker → retain responses, metadata, score, and audit → omit reconstructible prompts and unstable event logs → PASS with limitations
- **Verification performed:** hash, schema, case-ID, response-preservation, score, scope, secret-pattern, and full-suite checks
- **Unresolved conflicts / unknowns:** hidden model build identity and actual provider cost are not exposed; substring scoring remains directional
- **Final output category:** HANDLED
