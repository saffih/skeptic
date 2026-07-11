# Stage 1.5 Design Fix Notes

## Scope

This note records benchmark-design fixes made after the Stage 1.5 design review returned `CONFLICT`.

No benchmark evaluations were run. No historical formats were scored. No source files were edited.

## Conflict Fixes

- Added explicit `QUIXBUGS` fixture coverage by relabeling/reducing `CI06` to QuixBugs `breadth_first_search`.
- Added explicit `BUGSINPY-REDUCED` fixture coverage by relabeling/reducing `CI04` to BugsInPy `youtube-dl` bug `1`.
- Updated `03-fixture-index.md` with explicit source-family coverage.
- Updated `04-scoring-rubric.md` to require raw outputs before scoring and to forbid tone/fluency/confidence/persuasiveness/format-polish scoring.
- Updated `00-benchmark-charter.md` to separate Skeptic-format quality, local-agent execution quality, worker/sub-agent workflow quality, and scoring/judge reliability.
- Updated `02-candidate-definitions.md` with candidate file SHA-256 hashes.

## Source Evidence

| Fixture | Source family | Evidence |
|---|---|---|
| `CI06` | `QUIXBUGS` | QuixBugs `python_programs/breadth_first_search.py`; source reference `https://raw.githubusercontent.com/jkoppel/QuixBugs/master/python_programs/breadth_first_search.py`. |
| `CI04` | `BUGSINPY-REDUCED` | BugsInPy `projects/youtube-dl/bugs/1/bug.info` records buggy commit `99036a1298089068dcf80c0985bfcc3f8c24f281`, fixed commit `1cc47c667419e0eadc0a6989256ab7b276852adf`, and test file `test/test_utils.py`; source reference `https://raw.githubusercontent.com/soarsmu/BugsInPy/master/projects/youtube-dl/bugs/1/bug.info`. |

## Candidate Hashes

Computed with `find analysis/skeptic-capability-benchmark/candidates -type f -print0 | xargs -0 shasum -a 256`.

| Candidate file | SHA-256 |
|---|---|
| `analysis/skeptic-capability-benchmark/candidates/C0-current-main/definition.md` | `bb5a68b3d5aabfcfe875161bf266a2a1078968cefdc23f8c9e6fd6904c09dd6f` |
| `analysis/skeptic-capability-benchmark/candidates/C1-current-main-plus-loop-collect/definition.md` | `3e6b77186277d6a4abf257c5f64e6c5940c2432bb771d82a468029adc2b70aaf` |
| `analysis/skeptic-capability-benchmark/candidates/C2-current-main-plus-code-skeptic-domain-extension/definition.md` | `122874f4a8a9383a045afa913ee255cf97081c07268f3e08a75b85036aebe85c` |
| `analysis/skeptic-capability-benchmark/candidates/C3-current-main-plus-loop-and-code-extension/definition.md` | `9567e6cc9266131bd36fabb4638b4a9fc0c50092aecb853ff8bb31f1f4535c0c` |

## Remaining Required Check

Re-run Stage 1.5 benchmark design review before execution. The existing audit file still records the earlier `CONFLICT` and should not be treated as cleared until a fresh review verifies these fixes.
