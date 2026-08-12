# WELL mechanical checker

`capabilities/well_check/well_check.py` is the repository's single standard
entry point for deterministic mechanical checking of a WELL-governed Markdown
design document. The repository has no shared Python environment convention,
so bootstrap the capability-local environment once from the repository root:

    python3 -m venv capabilities/well_check/.venv
    capabilities/well_check/.venv/bin/python -m pip install -r capabilities/well_check/requirements.txt

Run the standard CLI with that environment:

    capabilities/well_check/.venv/bin/python capabilities/well_check/well_check.py path/to/document.md

Run its focused tests with the same interpreter:

    capabilities/well_check/.venv/bin/python -m unittest tests.capabilities.well_check.test_well_check

It writes a canonical JSON receipt to standard output and a concise diagnostic
for every violation to standard error. Its status is `PASS`, `FAIL`, or
`REVIEW`: `REVIEW` is a deterministic unresolved structural classification,
not semantic acceptance. Exit status is zero only for `PASS`, one for `FAIL`,
and two for `REVIEW`.

The checker implements only mechanically applicable WELL rules. `WELL-S001`
requires the literal lower-case word `because` in each structurally classified
prose sentence. `WELL-N001` validates canonical definition names,
`WELL-N002` rejects duplicate canonical definitions, and `WELL-N003` rejects
non-exact references to recognized canonical definitions. A backticked
identifier is not a canonical reference merely because it resembles a
lowercase kebab-case name; a definition in the same artifact establishes the
mechanically recognizable canonical name. Structural syntax excluded by
WELL is listed in `exemptions`; a construct the checker cannot classify is a
fail-closed `WELL-U001` `REVIEW` result requiring manual review. A known
mechanical violation takes precedence over `REVIEW` and returns `FAIL`.

WELL names block formulas but does not define a machine grammar for them. A
paragraph delimited by standalone `$$` markers is therefore reported as the
manual-review `possible-block-formula` case, rather than accepted as formula
syntax or evaluated as prose. This sentinel does not define a formula grammar
or change WELL's mechanical PASS/FAIL scope.

The capability uses the sole Markdown AST/token pipeline in `well_check.py`.
Its exact parser dependencies (including the parser's transitive `mdurl`)
are pinned in `capabilities/well_check/requirements.txt`:
`markdown-it-py` parses CommonMark plus repository table syntax, and its
front-matter plugin identifies YAML metadata as WELL structural syntax. It is
not a semantic design or warrant checker.
