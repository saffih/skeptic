# Skeptic Domain Registry

Lightweight routing index for Skeptic domain lenses.

The core `skeptic.md` remains authoritative. Domain timing and selection are owned by `skeptic.md`.
The registry contains routing metadata only; selected domain files contain the questions.

Current domains:
- SEC -> domains/security.md: Security / input / credentials / permissions / exposure
- CPX -> domains/complexity.md: Complexity / coupling / state / mental load
- REL -> domains/reliability.md: Reliability / scale / operations / ownership
- DAT -> domains/data.md: Data / I/O / persistence / consistency / timing
- ARC -> domains/architecture.md: Architecture / interfaces / contracts / dependencies
- CFT -> domains/craft.md: Craft / tests / errors / mocks

Rules:
- Use only domains selected or explicitly activated by the core.
- Multiple domains may be selected.
- Do not load all domain files by default.
- Read only the listed files for the selected domain set.
- A missing selected domain file is skipped/UNKNOWN coverage, not evidence that the domain is clean.
- Parallelize only already-selected domains when that reduces repeated scanning or cost.
- Domain files are detection aids; findings return to the core Skeptic flow for stabilization, evidence, decision, action, and verification.

This registry is a compatibility entrypoint for the former monolithic `skeptic-questions.md`; it is not a second runtime contract.

Document Owner: Skeptic Methodology
Review Date: Quarterly
Status: ACTIVE
