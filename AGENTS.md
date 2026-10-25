# Skeptic RC — Agent entry map

This is the RC-only agent-navigation source for `saffih/skeptic@RC:AGENTS.md`, owned by Hartal `projects/skeptic/public-agents-rc.md`. It identifies terms and routes; it does not install a method, override permission, or adopt RC as stable. Relative links below resolve in public `saffih/skeptic@RC`.

## Terminology and entrypoints

- **Skeptic / `RunSkeptic`:** Evidence-grounded adversarial review. On RC, [`skeptic.md`](skeptic.md) is experimental V6 and [`skeptic-v5.md`](skeptic-v5.md) is stable V5. Bare `RunSkeptic` follows its existing governing selection; reading this file never silently switches it.
- **`RunSkeptic RC`:** Explicit V6-only review. Freshly read [`skeptic.md`](skeptic.md) when invoked.
- **InnoSkeptic / Innovative Skeptic:** V6 mode for generating and challenging materially distinct alternatives without forcing a winner. Governed by [`skeptic.md`](skeptic.md).
- **Skeptic Grill / Decision Frontier RC:** Optional V6 profile for discovering stage-necessary decisions, obligations, dependencies and alternatives; resolving supported matters before asking an owner; and showing proportional trade-offs. Formal trigger: `Skeptic Grill: <goal>` (alias `Decision Frontier RC: <goal>`). On invocation freshly read **both** [`skeptic.md`](skeptic.md) and [`decision-frontier.md`](decision-frontier.md), using normal V6 assurance, evidence, authority and action rules; default permission is read-only. A mere mention or question about the term is navigation, not a formal invocation.
- **Decision frontier:** Current-stage unresolved decisions ready after their prerequisites, not every imaginable future question. Material blocked or deferred matters stay visible when relevant. Defined by [`decision-frontier.md`](decision-frontier.md).
- **Decision View / attributes considered:** Adaptive human presentation of the decision, supported recommendation or decisive unknown, relevant attributes, material gap/dependency and next step. Use concise prose, Gain / Cost / Gap options, or an attribute-impact comparison only when useful; no compulsory matrix, scores or context-free checkmarks. Defined by [`decision-frontier.md`](decision-frontier.md).
- **`RunSkeptic Dual`:** Controlled V5/V6 comparison under [`runskeptic-dual.md`](runskeptic-dual.md); requires genuinely separate invocations. Without independent arms, report `NOT_RUN`, not a fabricated comparison.

## Release and authority boundaries

[`RC-START-HERE.md`](RC-START-HERE.md) is the RC orientation and [`run-skeptic-rc-install.md`](run-skeptic-rc-install.md) explains opt-in selection. Public `main` remains stable V5. This file is navigation only: it grants no publication, mutation, action or promotion authority, and does not replace the exact governing files.