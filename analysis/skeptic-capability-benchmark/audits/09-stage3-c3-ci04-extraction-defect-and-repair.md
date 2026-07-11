# C3 Stage 3 CI04 Extraction Defect And Repair Audit

- Task ID: `STAGE_3_C3_CI04_EXTRACTION_REPAIR_AND_CORRECTED_REPORT_PACKET_001`
- Branch: `benchmark/skeptic-capability-stage2-2026-07-04`
- Input commit: `6ad8a604fc6a1ada908985b862f1442266e8e3bb`
- CI04 run: `analysis/skeptic-capability-benchmark/runs/C3-current-main-plus-loop-and-code-extension/CI04/run-1.md`
- CI04 run SHA-256: `677bfcbeb52a6b465deb715af1788049dce654aa71b5d2b56ffc43ec7d85289d`
- Response header: `raw candidate response: bytes=1118 sha256=f027e9b9435d0c8e6fa2092188c6757b33fcd815137dabd590ce19b9d7e795c8`
- Extracted bytes: `1118`
- Extracted SHA-256: `f027e9b9435d0c8e6fa2092188c6757b33fcd815137dabd590ce19b9d7e795c8`
- Extraction round trip: PASS

## Observed Defect

- Scorer received wrong CI04 payload: OBSERVED
- Adjudicator received the same wrong CI04 payload: OBSERVED
- Original arithmetic was internally correct over the wrong score ledger: OBSERVED
- Exact old packet-builder implementation: UNKNOWN
- The original ledger and adjudication describe only byte-count/hash metadata and do not evidence use of the verified response body.
- The original deterministic verifier passed because it checked fixture uniqueness, category/score mapping, adjudication application, and arithmetic over the supplied ledger; it did not verify CI04 scoring-payload extraction against the run-record body hash.
- The original adjudication did not repair the defect because it received the same malformed metadata-only CI04 representation.
- Stage 4 remained blocked because the published Stage 3 result contained a CI04 judgment derived from malformed scoring input.

## Affected Scope

- Metadata-bearing response-header count: `1`
- Affected fixture: `CI04`
- Affected scope: CI04-only
- Other fixture results frozen: `35`
- Frozen 35-row SHA-256: `bcce3ea0e3b0ea7a93fbbf55b0c7d8b0c9bdf0a31498be11727b93697539f802`
- Other fixture results changed: no

## Fresh Repair

- Fresh scorer context: `019f52e0-a6be-7072-80cb-4f5cb8afc653`
- Fresh adjudicator context: `019f52e1-b67e-7d11-a1a9-063c951555dc`
- Clean-room isolation: PASS
- Corrected reconciliation: PASS
- Corrected aggregate: `61` of `72`
- Original five artifacts modified: no
- Holdout content read: no
- Candidate comparison performed: no

## Original Stage 3 Artifact Manifest

- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-fresh-packet-003/00-official-scoring-ledger.md`: bytes=`25508`; SHA-256=`ee378d3947439dcc0b00dd39d397c5e2c7fde9a65eb3a32d5a7aec70bd022106`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-fresh-packet-003/01-adjudication.md`: bytes=`23689`; SHA-256=`e34bf5095cd0f37724a4088ab224aab3f3de6f3797f3863fde901ecc82d6cf62`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-fresh-packet-003/02-deterministic-verification.md`: bytes=`15580`; SHA-256=`1ade42f65536b4d1b6dc69d17452a48664f7245caee1b798e010ac58ccc0c2fb`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-fresh-packet-003/03-runskeptic-gate.md`: bytes=`4427`; SHA-256=`d0186be6aee262b44dfb68c2c13c63705e90e772d813f727ceda361ec63aa63c`
- `analysis/skeptic-capability-benchmark/reports/08-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring.md`: bytes=`22449`; SHA-256=`d29f02192c5af7531b194375e56e5d1fa26d8384a79a5156f68846f2e69f10bd`

## Repair Receipt Manifest

- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-ci04-repair-001/00-extraction-proof.md`: `ceec6d03c804f9a7900d89ed7443794f13030f9b28679153713e0ec1a08f66f7`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-ci04-repair-001/01-ci04-rescore.md`: `16a6d57f4a737258fc1ba8c57e29c8f24f22c7eeada084805e1fe921d743e7f4`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-ci04-repair-001/02-ci04-adjudication.md`: `47606a32689cf664b1048b18f74ac8f63f9b48fea9e611c21bb2dd9c5fde728a`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-ci04-repair-001/03-corrected-reconciliation.md`: `d246e37929f90130d878e79153e55bb42b4d075ab140e23282a07be4541951d8`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-ci04-repair-001/04-runskeptic-gate.md`: `206cdafa3ca296f600fb2a50691baac6d42cbf07d5ac54a84f26625f00324081`

## Disposition

- Original report: preserved as immutable historical evidence and superseded for Stage 3 conclusions
- Corrected report: `analysis/skeptic-capability-benchmark/reports/09-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring-corrected.md`
- Correction-execution verdict: PASS
- Visible candidate comparison allowed after commit, push, and remote verification: yes
- Next authorized task: `STAGE_4_VISIBLE_CANDIDATE_COMPARISON_REMOTE_VERIFIED_PACKET_001`
