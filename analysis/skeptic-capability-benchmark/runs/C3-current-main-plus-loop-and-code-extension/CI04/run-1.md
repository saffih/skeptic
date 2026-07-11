candidate ID: C3-current-main-plus-loop-and-code-extension
fixture ID: CI04
run number: 1
candidate file path: analysis/skeptic-capability-benchmark/candidates/C3-current-main-plus-loop-and-code-extension/definition.md
candidate hash: 9567e6cc9266131bd36fabb4638b4a9fc0c50092aecb853ff8bb31f1f4535c0c
fixture source path or section: analysis/skeptic-capability-benchmark/fixtures/visible-fixtures.md#CI04
packet: 002E
worker/context identifier: 019f5074-ef68-7dd1-909c-5a798e0c322d
worker level: XHIGH
fresh or provably uncontaminated: yes
candidate content supplied: yes
exactly one visible fixture supplied: yes
raw instruction/schema supplied: yes
destination path supplied: yes
prohibited material supplied: no
prior C3 output supplied: no
scoring requested: no
comparison requested: no
context protection required: yes
context protection status: maintained
clean-room required: yes
clean-room status: maintained
lead/orchestrator agent level: XHIGH
execution agent level: XHIGH
exact prompt used: bytes=2943 sha256=c73973fbdd5e03fcad48ed1c740baac061cea940b47e730f434cf7da8b4f5f3e
[CANDIDATE INSTRUCTIONS]
# Candidate C3-current-main-plus-loop-and-code-extension

- Candidate ID: `C3-current-main-plus-loop-and-code-extension`
- Base format: `versions/F5-current-main`
- Candidate text location: this definition only; source files are not edited.
- Intended capability target: combined `LOOP`, `CODE`, `WEAK`, `SILENT`, `SPOT`, `ACTIONABLE`

## Composition Rule

Combine the optional `loop: collect` runtime extension from `C1` with the optional code-specific domain extension from `C2`.

## Minimality Constraint

- `loop: collect` remains optional and runtime-related.
- Code-specific probes remain in the domain-question layer.
- Normal single-pass Skeptic behavior must remain unchanged when neither optional mode is activated.
- Disqualification capabilities must not weaken: `PERM`, `FIXAUTH`, `SRC`, `EVID`, `WORKER`.


[VISIBLE FIXTURE]
## CI04 - BugsInPy-Reduced youtube-dl Filename Edge Case

- Fixture ID: `CI04`
- Source type: OSS-style
- Source family: BUGSINPY-REDUCED
- Source/library/project name: BugsInPy `youtube-dl`, bug 1, reduced from `test/test_utils.py` / `youtube_dl/utils.py`
- Capabilities tested: `CODE`, `ACTIONABLE`
- Negative control: no
- Input artifact: `Reduced buggy edge case: sanitize_filename("\u5927\u58f0\u5e26 - Song", restricted=True) should keep the ASCII title "Song"; sanitize_filename("\u603b\u7edf: Speech", restricted=True) should keep "Speech"; restricted sanitization must also avoid returning an empty string for inputs like "-" or ":".`
- Prompt to apply: `Apply Skeptic to test adequacy and boundary behavior.`
- Expected good finding: Flags that filename sanitization needs representative non-ASCII-prefix and punctuation-only edge cases; a happy-path ASCII-only test cannot prove restricted-mode behavior.
- Dangerous miss: Calls restricted filename sanitization safe because simple ASCII names pass.
- False positive risk: Treating every Unicode transformation as a bug when the restricted-mode contract explicitly allows dropping non-ASCII characters.
- Scoring notes: Strong answer ties the finding to the reduced BugsInPy edge cases and asks for contract-level assertions, not broad rewrite.
- Evidence if real: BugsInPy project `youtube-dl`, bug `1`; `bug.info` records buggy commit `99036a1298089068dcf80c0985bfcc3f8c24f281`, fixed commit `1cc47c667419e0eadc0a6989256ab7b276852adf`, test file `test/test_utils.py`; source reference `https://raw.githubusercontent.com/soarsmu/BugsInPy/master/projects/youtube-dl/bugs/1/bug.info`; reduced from fixed tests in `https://raw.githubusercontent.com/ytdl-org/youtube-dl/1cc47c667419e0eadc0a6989256ab7b276852adf/test/test_utils.py`.



[RAW EXECUTION DIRECTIVE]
Apply the supplied candidate instructions to the supplied visible fixture. Produce only the candidate's raw response to the fixture. Do not score, compare, critique, discuss expected answers, revise against benchmark expectations, or recommend source changes.

raw candidate response: bytes=1118 sha256=f027e9b9435d0c8e6fa2092188c6757b33fcd815137dabd590ce19b9d7e795c8
Skeptic finding: the test set is inadequate for restricted filename boundary behavior.

The risk is not ordinary ASCII names. The boundary is the order and fallback behavior after restricted-mode sanitization drops non-ASCII characters and strips separators. A happy-path ASCII-only test cannot prove that the remaining ASCII title survives when the input begins with non-ASCII text or punctuation.

Representative contract assertions should cover the reduced BugsInPy edge cases:

- `sanitize_filename("大声带 - Song", restricted=True)` keeps the ASCII title `Song`.
- `sanitize_filename("总统: Speech", restricted=True)` keeps the ASCII title `Speech`.
- `sanitize_filename("-", restricted=True)` does not return an empty string.
- `sanitize_filename(":", restricted=True)` does not return an empty string.

Keep the assertion narrow: restricted mode is allowed to drop non-ASCII characters, so this should not require broad Unicode preservation or transliteration. The test should prove that restricted sanitization preserves the surviving ASCII title and has a non-empty fallback for punctuation-only inputs.

execution notes: fresh XHIGH worker used; one visible fixture executed; no scoring requested; no comparison requested; external temporary response used; deterministic wrapper construction used; byte-fidelity writer/parser suite passed
blockers: none
