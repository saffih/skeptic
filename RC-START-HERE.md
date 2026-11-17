# Skeptic V8 - public experimental RC

**Status (2026-11-17):** Hartal and public stable `main` remain V7 (blob `3021be4622a3edef42fc22593a099ba35eb42191`). Experimental V8 is sourced from Hartal branch `work/skeptic-v8-dmr-rc-20261117` and distributed only on public `RC` after explicit readback. V8 is a candidate, not a replacement for stable V7 or an independently qualified improvement.

## Source and preserved controls

- **V8 RC runtime:** `skeptic.md`, retaining V7's existing ATTACK/DMR controls and adding one conditional recurrence-sufficiency question inside activated DMR. No change to activation, permission, assurance, action or receipt semantics.
- **Frozen stable V7 control:** `releases/skeptic-v7-previous.md` on the Hartal candidate branch, exported as `RC/skeptic-v7.md`, exact V7 blob `3021be4622a3edef42fc22593a099ba35eb42191`.
- **Frozen V6 control:** `releases/skeptic-v6-previous.md` in Hartal, exported as public `RC/skeptic-v6.md`. The exact predecessor Git blob is `548869b5dc71f94ba8a0d6b7cfcecc147ac6214e`.
- **Historical V5:** `releases/skeptic-v5-previous.md` in Hartal, exported as public `RC/skeptic-v5.md`; it remains historical, not the default V7 comparison arm.
- **Compatibility:** `skeptic-rc.md` is an older V6 snapshot, not the active RC source, publication source, or an independent reviewer.
- **Optional profile:** `decision-frontier-rc.md` is published as `decision-frontier.md`. It is not activated by ordinary RunSkeptic.
- **Optional comparison:** `runskeptic-dual.md` binds frozen stable V7 against candidate V8 RC and requires genuinely isolated semantic invocations. Neither sharing a context nor duplicating source files creates independent evidence.

## Public RC

[Public RC branch](https://github.com/saffih/skeptic/tree/RC) carries experimental V8 as `skeptic.md`, frozen stable V7 as `skeptic-v7.md`, historical V6/V5 controls, the optional Dual contract, Decision Frontier profile and [RC install instructions](https://github.com/saffih/skeptic/blob/RC/run-skeptic-rc-install.md).

For ordinary `RunSkeptic`, use exactly the current `RC/skeptic.md` if this branch has been selected. `RunSkeptic RC` is a compatibility alias for that same runtime. `RunSkeptic Dual` must be explicitly invoked and compares V8 RC against frozen V7, without claiming independent runs by default.

The branch alone does not install a user preference, select a model, grant permissions, schedule runs, or log experimental outcomes. Git refs move; bind the actual commit and blob at use.

## Evidence, risks, and limits

V8 was reviewed in repeated **same-context semantic** challenges of its conditional wording and negative controls. These are not independent model-arm tests; behavioral effect and false-positive rate remain **UNKNOWN / NOT_RUN**. The single semantic addition aims to test recurrence sufficiency when an already-activated DMR has evidence of a material recurring pattern. Preserve legitimate one-off corrections and no-change conclusions; do not invent systemic causes or mandatory causal depth. Independent oracle-withheld V7/V8 behavioral comparisons have not run. Distribution is not behavioral qualification.

## Attribution and authority

Decision Frontier acknowledges the ideas (not implementation or skill text) of [Matt Pocock's Grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md), under the referenced upstream [MIT License](https://github.com/mattpocock/skills/blob/main/LICENSE).

Hartal `main` remains the stable V7 source of truth; this V8 experiment is sourced from its explicit Hartal work branch and copied to public `RC` only. `repo/publication-rules.md` governs selected-file sync. Public stable `main` remains V7 and is not overwritten by RC.
