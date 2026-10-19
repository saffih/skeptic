# Skeptic RC — V6 + independent V5 control

**Status:** Experimental, not behaviorally qualified, not a stable replacement. Canonical Hartal source lives in `projects/skeptic/` on `main`:
- `skeptic.md`: current **V5** baseline.
- `skeptic-rc.md`: complete experimental **V6** runtime (20-line dormant Deep Meta-Review addition).
- `runskeptic-dual.md`: explicit controlled, **independently isolated** V5/V6 comparison protocol; if independent arms unavailable, report `NOT_RUN`, not a fake A/B.
- `decision-frontier-rc.md`: optional Grilling-inspired decision-frontier extension; not part of a V5/V6-only comparison.
- `run-skeptic-rc-install.md`: remote invocation instructions.
- `evidence/v5-v6-dual-ledger.md`: private Hartal evidence source, not an automatic log.

**Public RC view:** [`saffih/skeptic@RC`](https://github.com/saffih/skeptic/tree/RC) carries V6 as `skeptic.md`, baseline V5 as `skeptic-v5.md`, the dual-run protocol, optional Decision Frontier profile and installer. Public `main` remains the stable V5 distribution and should not be changed by RC synchronization.

**Invocation:** `RunSkeptic Dual: <task>` for an explicit comparison; `RunSkeptic RC` for candidate only; `Decision Frontier RC: <task>` for the optional interactive profile. The installer describes how to request dual behavior when calling ordinary `RunSkeptic` in a supporting assistant. Mere repository presence cannot activate a remote user preference or create an isolated runner.

**Evidence:** [Hartal issue #91](https://github.com/saffih/hartal/issues/91). At entrypoint creation, no controlled V5/V6 pairs have been completed and no verified performance gain has been established. V6 observation is not proof of comparative superiority.

**Attribution:** Decision Frontier acknowledges the ideas (not the implementation or skill text) from [Matt Pocock's Grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md), under the referenced upstream [MIT License](https://github.com/mattpocock/skills/blob/main/LICENSE). These RC artifacts remain authored independently for Hartal.

**Authority and promotion:** Hartal `main` owns source, public `RC` is distribution only. Neither dual-run observation nor RC publication promotes V6 or weakens V5's action/permission/evidence rules. Any future semantic migration to canonical `skeptic.md` requires qualified benefit and harm evidence, exact reviewed diff, rollback plan, and explicit owner approval.
