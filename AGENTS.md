# Skeptic — Public Agent Guide

This file is an entrypoint map for users and agents consuming this repository. It does not install tools, grant permissions, select a hidden model, or replace the authoritative Skeptic runtime.

## Which file to read

- **`RunSkeptic`**, including ordinary Skeptic review: read the current [`skeptic.md`](skeptic.md) from this branch. The runtime alone owns its invocation contract, completeness, evidence, Thinker lenses, decisions, permissions, verification and receipts. Bare `RunSkeptic` defaults to COMPLETE assurance and read-only permission.
- **`Skeptic Grill: <goal>`** or **`Decision Frontier: <goal>`**: read **both** [`decision-frontier.md`](decision-frontier.md) and [`skeptic.md`](skeptic.md) from this same branch. Grill is an optional, explicitly invoked dependency-aware decision and questioning profile, not a change to the core runtime. Default permission is read-only. A question *about* Grill does not invoke it.
- **`InnoSkeptic` / Innovative Skeptic**: use the current `skeptic.md` to develop and compare materially different candidates. Grill may use this method as its current contract requires.
- **`Razor`**: use the current `skeptic.md` for its bounded, read-only entrypoint.
- **Experimental or comparison modes**, if files are available in the selected branch, must use their explicit local contract. No branch switch, independent review, or review method is activated merely by seeing a name here.

## Important boundaries

1. **Source:** Load the actual current files for every invocation. Do not replace an inaccessible source with memory or a different branch; disclose the limitation instead.
2. **Authority:** `skeptic.md` remains the sole core review runtime. Grill cannot weaken its assurance, permission, evidence, action, or completion requirements. A formal review requires the real governed invocation; the profile's mention of one is not execution evidence.
3. **Independence:** Same-context reasoning is not independent review. If an independent review is required but unavailable, keep that obligation unresolved.
4. **Proportionality:** Grill selects current-stage questions, keeps blocked/deferred decisions honest, and need not impose a persistent graph, registry, scorecard, or extra step for every ordinary action.
5. **Installation:** Repository files and this guide do not create persistent assistant instructions or automatic activation. Explicitly invoke the intended capability and read the named sources.
6. **Qualification:** Distribution of an optional profile does not itself demonstrate behavioral effectiveness or authorize an external action.

For a normal review, **`skeptic.md` alone is sufficient**. Load the additional Grill profile only when Grill is explicitly requested.
