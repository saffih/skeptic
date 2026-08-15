# Model Routing Calibration

This note records provisional empirical calibration for Capability Admission,
because the observations are useful routing evidence but are not normative
policy.

## Ownership and question

The normative model routing policy remains the single owner of route
selection, model-class selection, reasoning effort, escalation, and Capability
Admission, because this note does not override that policy.

Capability Admission asks whether a role can safely own its next semantic
judgment, because self-confidence is not an observable or falsifiable ground
for capability.

The question is not whether a model feels capable in general, because the
relevant obligation is the exact judgment this role must own next.

## Distinguishable paths

Calibration distinguishes the following outcomes, because retrieval,
decomposition, blocking, downstream routing, and self-escalation solve
different problems:

- **Retrieve:** authorized evidence is needed before judgment, because unread
  evidence is not a model-capability gap.
- **Decompose:** the working set or coupling needs safe decomposition under
  Context Rules, because sizing must not weaken completeness, freshness, or
  independence.
- **Block:** authority is missing or contradictory, or no permitted feasible
  path exists, because a stronger model cannot manufacture authority or
  feasibility.
- **Stronger downstream worker:** a bounded downstream judgment needs greater
  capability, because that need does not itself require stronger Brain
  capability.
- **Self-escalate:** the current role cannot safely own its own next judgment,
  because the least expensive stronger authorized route should then be
  considered.

Failure visibility matters, because semantic mistakes that can silently
survive later checks need a greater safety margin than errors that are exposed
before downstream use.

## Provisional profile

The following profile is provisional and non-normative, because provider/model
mappings are empirical and replaceable and model, pricing, and product
behavior can change over time.

| Brain level | Current empirical route | Status and use |
| --- | --- | --- |
| 1 / NORMAL | GPT-5.6 Luna / medium reasoning | Current best-supported default Brain, because repeated observations covered ordinary routing judgments. |
| 2 / INTERMEDIATE | GPT-5.6 Luna / high reasoning | Candidate intermediate route, because it generally matched or slightly improved GPT-5.6 Luna / medium but is not fully established; GPT-5.6 Terra / medium remains the challenger. |
| 3 / FRONTIER | GPT-5.6 Sol / medium reasoning | Protected route for consequential architecture, hard conflicting-evidence synthesis, or final semantic judgment with low failure visibility, because those obligations need greater safety margin. |

There are at most three Brain levels, and they are not a mandatory staircase,
because a normal Brain may route a downstream frontier review directly to Sol.

GPT-5.6 Luna / low is useful for bounded low-ambiguity workers but is not supported as
the unrestricted default Brain, because current evidence does not establish
that safety margin.

GPT-5.6 Terra / low has no provisional Brain placement, because manual calibration did
not demonstrate a routing advantage.

## Current observations

GPT-5.6 Luna / low performed many bounded routing judgments correctly but produced at
least one material authority-versus-evidence confusion, because successful
bounded calls do not establish safe unrestricted admission.

GPT-5.6 Luna / medium repeatedly produced strong mission designs across retrieval,
decomposition, stale evidence, authority blockers, coupling, and stronger
downstream review, because those were the observed calibration obligations.

GPT-5.6 Luna / high generally matched or slightly improved GPT-5.6 Luna / medium operationally,
but current evidence has not demonstrated enough repeatable additional safety
value to make it the default, because a single apparent improvement is not
qualification.

One matched UI observation showed approximately 29K context used for GPT-5.6
Luna / medium and 33K for GPT-5.6 Luna / high on the same calibration task, because the
observation records context use rather than billing proof.

GPT-5.6 Terra / low produced routing and self-state problems in manual tests and
currently has no demonstrated place in the Brain ladder, because those tests
did not show a reliable admission advantage.

GPT-5.6 Terra / medium remains unqualified and is the challenger for the
intermediate slot, because the current evidence does not yet establish its
repeatable safety performance.

The Luna / high versus Terra / medium intermediate-slot question remains
unresolved, because neither candidate has yet earned a fully qualified
intermediate placement.

## Measurement method

Prefer blind realistic mission-design trials over simple capability questions,
because realistic obligations expose unsafe routing that self-report can hide.

A calibration should test whether a candidate can distinguish the following
outcomes, because the six-way distinction makes unsafe routing falsifiable:

- **A.** I can safely own this judgment, because the candidate must identify
  observable grounds.
- **B.** I need authorized evidence first, because retrieval is distinct from
  capability escalation.
- **C.** I need safe decomposition first, because working-set fit is distinct
  from semantic strength.
- **D.** A downstream judgment should use stronger capability, but my Brain need
  not escalate, because routing is obligation-specific.
- **E.** I cannot safely own this judgment, so my Brain must escalate, because
  current-role capability is the admission question.
- **F.** No model capability solves this because authority or feasibility is
  missing, because escalation cannot create either one.

For capability-level qualification, freeze the rubric before reading results,
use fresh sessions, and compare the same obligations across candidate routes,
because post hoc criteria and stale context can bias the comparison.

Heavily penalize unsafe under-escalation and distinguish safety failures from
unnecessary-cost defects, because silent semantic failure is not equivalent to
using more capacity than necessary.

Record actual usage when observable, prefer the cheaper candidate when safety
performance is materially equivalent, and pay for stronger capability when it
measurably reduces silent semantic failure, because cost is subordinate to
reliable completion but remains a routing objective.

Current pricing should be re-observed rather than encoded as permanent fact,
because model, product, and pricing behavior changes over time.

A single successful trial is corroboration, not qualification, because
qualification requires repeatable evidence under a frozen rubric.

## TP implementation limitation

The current TP schema exposes only abstract `LOW | MEDIUM | STRONG`, because
that is the existing route vocabulary.

`next: BRAIN` currently requires `STRONG`, because the current TP contract does
not express a separate intermediate Brain continuation.

The provisional three-level concrete Brain profile is therefore not yet a
mechanically expressible normal-to-intermediate-to-frontier continuation
contract, because silently reinterpreting the existing fields would change TP
semantics.

Changing that limitation requires a separate bounded design/runtime task after
the calibration is accepted, because this note does not redesign TP runtime or
`TP_RESULT`.

This note does not override the normative model routing policy, because empirical
observations must not become portable normative model requirements.
