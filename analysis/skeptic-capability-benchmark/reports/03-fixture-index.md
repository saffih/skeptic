# Fixture Index

## Counts

- Visible fixtures: 36
- Holdout fixtures: 4
- Total fixtures: 40
- Negative controls: 8 / 40 = 20.0%
- Real-history or reduced OSS-style fixtures: 14 / 40 = 35.0%

## Group Coverage

| Group | Fixture IDs | Count |
|---|---|---:|
| Prompt guard | `PG01`-`PG06` | 6 |
| Repo/procedure boundary | `RB01`-`RB06` | 6 |
| Code/test/integration | `CI01`-`CI08` | 8 |
| Domain questions | `DQ01`-`DQ04` | 4 |
| Worker/context protection | `WK01`-`WK07` | 7 |
| Loop collection | `LP01`-`LP05` | 5 |
| Holdout | `HO01`-`HO04` | 4 |

## Capability Coverage

| Capability | Representative fixtures |
|---|---|
| `PERM` | `PG01`, `PG02`, `PG06`, `RB01`, `RB03`, `WK01`, `HO03` |
| `FIXAUTH` | `PG01`, `RB01`, `RB02`, `RB03` |
| `SRC` | `PG04`, `RB04`, `WK06`, `LP03`, `HO01` |
| `EVID` | `PG03`, `PG04`, `RB06`, `WK02`, `LP02`, `HO04` |
| `CONTRA` | `PG02`, `CI03`, `WK03` |
| `WEAK` | `PG03`, `RB05`, `CI01`, `CI02`, `WK04` |
| `SILENT` | `RB05`, `RB06`, `CI06`, `CI07`, `LP04` |
| `DOMAIN` | `DQ01`, `DQ02`, `DQ03`, `DQ04`, `HO01` |
| `CODE` | `CI01`-`CI08`, `DQ01`, `DQ03`, `HO02` |
| `SPOT` | `HO02` |
| `WORKER` | `WK01`-`WK07`, `HO04` |
| `LOOP` | `LP01`-`LP05` |
| `NOISE` | `PG05`, `PG06`, `CI08`, `DQ02`, `WK05`, `LP01`, `LP05`, `HO03` |
| `ACTIONABLE` | `PG05`, `RB02`, `CI04`, `CI05`, `DQ04` |

## Negative Controls

- `PG05`
- `PG06`
- `CI08`
- `DQ02`
- `WK07`
- `LP05`
- `HO03`
- `HO04`

## Real-History / OSS-Style Fixtures

- Skeptic history: `RB04`, `DQ01`, `HO01`
- Reduced OSS-style/code/security snippets: `RB06`, `CI01`, `CI02`, `CI03`, `CI04`, `CI05`, `CI06`, `CI07`, `CI08`, `DQ04`, `HO02`
- QuixBugs source family: `CI06` (`breadth_first_search`, `python_programs/breadth_first_search.py`)
- BugsInPy-reduced source family: `CI04` (`youtube-dl` bug `1`, reduced from `test/test_utils.py` / `youtube_dl/utils.py`)

## Explicit Source-Family Coverage

| Source family | Fixture IDs | Evidence |
|---|---|---|
| `SKEPTIC-HISTORY` | `RB04`, `DQ01`, `HO01` | SHA/path references in each fixture. |
| `QUIXBUGS` | `CI06` | QuixBugs `breadth_first_search`; source reference `https://raw.githubusercontent.com/jkoppel/QuixBugs/master/python_programs/breadth_first_search.py`. |
| `BUGSINPY-REDUCED` | `CI04` | BugsInPy `youtube-dl` bug `1`; source reference `https://raw.githubusercontent.com/soarsmu/BugsInPy/master/projects/youtube-dl/bugs/1/bug.info`; reduced from fixed `test/test_utils.py` edge-case tests. |
| `OWASP-WSTG-MICRO` | `HO02` | Reduced OWASP/NIST-inspired path traversal fixture. |
| `SYNTHETIC-WORKER` | `WK01`-`WK07`, `HO04` | Synthetic bounded-receipt and context-protection artifacts. |
| `SYNTHETIC-LOOP` | `LP01`-`LP05` | Synthetic loop collection artifacts. |
| `SYNTHETIC-PROMPT-PROCEDURE` | `PG01`-`PG06`, `RB01`-`RB03`, `RB05`, `DQ02`, `DQ03`, `HO03` | Synthetic prompt/procedure artifacts. |

## Fixture Quality Gate

Status: `PASS`

Validation:

- Every fixture includes concrete artifact text.
- Every fixture tests one or two named capabilities.
- Every fixture includes expected good finding, dangerous miss, false positive risk, scoring notes, and evidence field.
- Fixture count is at least 35.
- Negative controls are at least 20%.
- Real-history or reduced OSS-style fixtures are at least 30%.
- Holdout fixtures are separated under `holdout/`.
- Fixtures are small enough to inspect fully.
- Required explicit source-family coverage includes `QUIXBUGS` and `BUGSINPY-REDUCED`.
- Fixtures do not require benchmark execution or candidate scoring in this task.

If later review finds fewer than 35 valid fixtures, fewer than 20% negative controls, fewer than 30% real-history / reduced OSS-style fixtures, biased fixtures, or inconsistent scoring expectations, benchmark status must become:

`CONFLICT - benchmark execution forbidden`
