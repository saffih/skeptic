# Task Prompt Design

- **Original author:** Saffi Hartal
- **Copyright:** Copyright (c) 2026 Saffi Hartal

This is the single TP design authority, because TP is small enough that separate Architecture and Software Design artifacts would duplicate meaning without improving realization.

TP adopts the repository Context Rules and Model Routing Policy by reference and conforms to WELL, because those artifacts already own context, routing, and design-writing meaning.

The workflow and implementation realize this design rather than owning competing semantics, because implementation detail must remain downstream of the design it implements.

## Purpose and architecture

TP turns `TP: <mission>` into sequential semantic reasoning and properly sized work until the mission frame is completed or honestly stopped, because reliable progress needs foresight without pretending that every task can be fully planned before evidence exists.

TP is host-neutral and provider-neutral, because native invocation and provider mechanics belong to the host rather than to TP semantics.

```text
TP mission
   |
BOOTSTRAP  mechanical, meaning-blind, stays alive
   |
BRAIN      semantic owner of the current frame
   |\
   | +--> BRAIN       more justified reasoning
   | +--> EXECUTION   one coherent bounded obligation
   | +--> CHILD       same frame rules recursively
   |
CLOSE FRAME
   |-- parent -> fresh parent BRAIN
   `-- NONE   -> terminal
```

Every Brain and Execution is a sibling semantic invocation launched directly by bootstrap, because no semantic worker should own or nest the TP loop.

The three roles have one boundary each, because the smallest robust design separates mechanical continuation, semantic judgment, and bounded work without adding another semantic controller.

| Role | Owns | Must not own |
|---|---|---|
| Bootstrap | run identity, fixed structural validation, dispatch, accepted-transition recording, direct-child lifecycle, same-workspace activity checks | mission meaning, planning, decomposition, semantic route choice, acceptance, task closure |
| Brain | current-frame reasoning, planning, formal RunSkeptic, validation, decomposition, child creation, capability admission, routing, exact Execution prompt, frame closure | bulk execution, provider lifecycle, mechanical replay decisions |
| Execution | one Brain-authored coherent bounded obligation, its tools/work/tests, action-level verification, curated result | frame closure, task-level replanning, parent/child navigation, TP terminal judgment |

## Durable state and restart

Bootstrap creates a minimal durable run before the first semantic invocation, because continuation must not depend on conversation residue.

```text
run/
  mission.md
  authority.md
  progress.jsonl
  artifacts/
    tasks/
    plans/
    handoffs/
    executions/
    evidence/
```

mission.md stores the exact original mission and authority.md binds the exact TP design plus adopted run-stable authority identities, because mission and TP governing semantics must not drift during continuation.

The run-stable authority also carries host-supplied `brain_initial_route` and `skeptic_source_locator_ref`, because bootstrap needs a mechanically supplied first route and Brain needs a stable locator for the authoritative current Skeptic source without rediscovering either from task meaning.

The Skeptic locator is stable but the Skeptic bytes are not frozen, because every formal RunSkeptic invocation must freshly resolve and read the actual current skeptic.md and record the exact source identity it used.

TP requires no separate Skeptic-version watcher or `NEEDS_REVIEW` lifecycle state, because when Brain observes that the current Skeptic source identity differs from the identity recorded by an open plan's review receipt, that plan cannot be relied on for further plan-derived work until it is formally re-reviewed under the current Skeptic source.

A mandatory RunSkeptic cannot be claimed when the current Skeptic source cannot be resolved, because unperformed verification cannot authorize plan adoption or COMPLETE.

`progress.jsonl` is an append-only mechanical ledger and navigation index while substantive semantic state lives in referenced artifacts, because bootstrap needs durable control state without absorbing task meaning.

A worker-written artifact becomes accepted run state only through a mechanically valid returned control object whose required references resolve, because unaccepted worker output has no control authority.

Bootstrap records `DISPATCH_INTENT` before launching a semantic child and records `RETURN` only after a mechanically valid return, because restart must distinguish work never admitted from work whose effects may already exist.

Restart is fixed by the accepted ledger rather than reconstructed from task meaning, because interruption uncertainty is mechanical evidence.

| Last durable state | Restart action |
|---|---|
| accepted terminal Brain return | remain terminal; launch nothing |
| accepted Brain requests EXECUTION; no matching Execution `DISPATCH_INTENT` | admit that exact Execution once |
| accepted Brain requests BRAIN; no matching Brain `DISPATCH_INTENT` | admit that exact Brain once on the recorded route |
| accepted Execution RETURN | launch fresh Brain on recorded `resume_brain_route` with the Execution handoff |
| Execution `DISPATCH_INTENT` without trustworthy RETURN | never replay automatically; surface mechanical UNKNOWN to fresh Brain on recorded `resume_brain_route` |
| Brain `DISPATCH_INTENT` without trustworthy RETURN | preserve last accepted semantic state; re-admit only when recorded route/retry authorization still permits, otherwise expose host/route unavailability |

No restart case infers idempotence, success, or task meaning from absence of a return, because uncertain side effects must not be guessed or duplicated.

## Uniform frames and localized context

The mission is the first ordinary task frame and differs only by having no parent, because a special root workflow would duplicate planning and closure semantics.

Every task frame is immutable semantic scope for one obligation, because its objective, DONE condition, and boundary must not drift as work accumulates.

```text
task_name: <human-readable breadcrumb>
origin_ref: <mission reference or parent semantic decision reference>
parent_task_ref: <parent task frame reference or NONE>
parent_resume_ref: <accepted parent Brain handoff reference or NONE>
objective: <one obligation>
done: <observable completion condition>
scope: <semantic and operational boundary>
entry_context_refs:
- <minimum curated references needed to begin>
```

`origin_ref` preserves traceability, `parent_task_ref` defines ancestry, and `parent_resume_ref` identifies the exact accepted parent state that created the child, because child work must return to its true semantic origin without reconstructing unrelated history.

`task_name` may use `--` only as a readable nesting hint, because semantic ancestry comes from references rather than string parsing.

The creating Brain checks every new frame for concise-complete fidelity to `origin_ref`, because a lossy frame can misdirect every later invocation.

A fresh Brain normally receives the current frame, its latest accepted Brain handoff containing current plan state when one exists, the latest Execution or child result when present, authority, and ledger navigation, because this is the task-sized entrance for localized reasoning without duplicating semantic plan state in mechanical control.

Ancestor frames, mission, and other already-authorized evidence remain reachable by reference but are not loaded by default, because Context Rules require selective depth without restricting receiver evidence authority.

The latest Brain handoff is a context guide rather than evidence authority, because underlying referenced evidence wins whenever the guide and source disagree.

## Brain semantic contract

Every Brain first REASONs on the current frame, because action must follow the present evidence rather than a controller-owned sequence.

```text
Is frame DONE established?
  YES -> completion decision -> formal RunSkeptic -> close only if clean
  NO  -> is a still-valid reviewed plan available?
           YES -> continue it
           NO  -> can a reliable complete plan be established now?
                    YES -> planning decision -> formal RunSkeptic -> adopt only if clean
                    NO  -> name the blocking uncertainty
                           choose only a justified information/progress step
                           or a justified stronger Brain
                           or close BLOCKED/CONFLICT
```

Brain considers materially different credible alternatives when they actually exist and does not manufacture ceremonial alternatives, because fake options spend reasoning without changing the decision.

Brain uses Skeptic reasoning during ordinary REASON to challenge assumptions, compare live alternatives, eliminate unsupported or dominated routes, and seek disconfirmation without calling that activity formal RunSkeptic, because formal RunSkeptic is the source-bound review of an exact persisted plan or completion artifact under the current Skeptic invocation contract.

### Planning

A complete plan is complete for the current frame at that frame's abstraction level, because recursive decomposition should preserve end-to-end foresight without forcing the parent to pre-solve descendants' internal methods.

A parent plan may defer a child method only when that child obligation has explicit objective, DONE, scope, starting context, expected return, and failure path, because vague placeholders can hide an unowned feasibility gap.

A complete plan may include conditional branches, checkpoints, and known future decision points, because reliable planning does not require pretending future evidence is already known.

Brain writes one immutable planning-decision artifact that contains the selected approach, the real alternatives and elimination basis when applicable, the plan, assumptions, risks, verification, and stop conditions, because one review should cover the actual decision rather than separately reviewing ceremonial fragments.

```text
# Planning Decision
task_ref: <current frame>
credible_alternatives:
- <alternative and material tradeoff>
- NONE when no materially different credible alternative exists
selected_approach: <chosen approach>
elimination_basis:
- <why rejected alternatives should not remain live>
plan:
- <step, bounded child obligation, branch, or checkpoint>
assumptions:
- <material assumption or NONE>
risks:
- <material risk or NONE>
verification:
- <how progress and eventual DONE will be established>
stop_conditions:
- <conditions requiring replan, evidence gathering, BLOCKED, or CONFLICT>
```

The already-running Brain formally RunSkeptic-reviews that exact planning decision before adoption, because plan review is semantic judgment owned by Brain rather than another TP role.

Every formal RunSkeptic invocation freshly reads the actual current skeptic.md, the exact artifact under review, and the evidence the current invocation contract requires, because memory or a prior Skeptic read cannot substitute for source-fresh review.

The persisted review receipt is bound to the exact reviewed artifact and records the Skeptic source identity actually used, because a review label must not silently transfer to changed plan meaning.

A plan is adopted only when no unresolved material ACTION, CONFLICT, review-required status, DECOMPOSE path, or blocking unknown prevents execution, because completion of the review task is not the same as approval of the reviewed plan.

A fresh Brain reuses a reviewed plan while its assumptions, authority, scope, selected approach, ordering, validation path, stop conditions, and other parent-level commitments remain valid and no observed current Skeptic source identity conflicts with the identity recorded by its review receipt, because ordinary expected progress should not trigger ceremonial replanning or rereview while known review-authority change must not permit further reliance on stale review evidence.

A child's internal-method refinement does not invalidate the parent plan unless it materially changes a parent-level commitment, because decomposition exists precisely to let a child determine HOW inside a bounded parent obligation.

A material plan revision receives a new immutable plan reference and new formal RunSkeptic review, because review evidence applies to exact plan meaning.

A fixable review finding may cause revision and another review only when the revision is materially changed or better informed, because equivalent repair/review loops add no information.

If no materially improved revision or useful evidence-gathering step is justified, Brain returns CONFLICT, because review must expose a planning dead end rather than create an unbounded repair loop.

### Ambiguity and information value

When a complete plan cannot yet be justified, Brain names the specific blocking uncertainty and chooses a next action only when it can explain why that action should reduce the uncertainty or make bounded material progress, because "do something and see" is not a planning method.

Before an ambiguity-reducing action, Brain records what class of result would change the next decision and afterward evaluates whether the named uncertainty materially decreased, because information gathering has value only when its outcomes can alter reasoning.

An evidence path that failed to reduce the uncertainty is not repeated equivalently unless materially new evidence changes its expected information value, because repeated low-information probes create wandering and cost.

There is no arbitrary numeric retry limit, because another step is justified by new expected information or progress value rather than by a counter.

Before failing fast, Brain distinguishes a genuine task-level dead end from insufficiency of its current semantic route and applies Capability Admission under the Model Routing Policy, because stronger reasoning may resolve a capability gap but cannot manufacture missing authority, evidence, permission, or feasibility.

### Properly sized action and decomposition

When a reviewed plan exists, Brain selects the next action from it; otherwise Brain selects only the best defensible information/progress step, because action size must match current semantic certainty.

The no-complete-plan path cannot hide a complete approach inside Execution, because work that could materially commit or complete the frame should first be expressed as a reviewable plan when reliable planning is already possible.

Brain uses one Execution for the largest coherent feasible bounded unit that shares one objective, scope, authority, and verifiable outcome without requiring task-level replanning or new authority midway, because operational multiplicity is not semantic fragmentation.

Many commands, files, records, sources, implementation changes, and tests may belong to one Execution, because count alone is not a reason to create more semantic frames.

Brain creates a child frame only when a distinct sub-obligation materially benefits from its own localized context, evolving plan, and independently validated DONE, because a child frame should buy semantic value rather than merely rename a step.

Brain requests another Brain rather than Execution when the next required work is semantic reasoning, because Execution must not own task-level judgment.

### Routing

The first Brain uses the host-supplied authorized `brain_initial_route`, because startup needs a route before semantic route ownership exists.

Brain selects every later semantic route under the Model Routing Policy, including the Execution route and `resume_brain_route`, because bootstrap must apply routing mechanically rather than infer task meaning.

A fresh Brain integrating unexpected Execution evidence may request another explicitly routed Brain after ordinary Capability Admission, because routing must adapt to changed semantic difficulty without forcing every return through an unnecessary premium intermediary.

### Closure and upward failure

A frame closes only through Brain as `COMPLETE`, `BLOCKED`, or `CONFLICT`, because bounded execution success, unavailable conditions, and unresolved semantic choice are different outcomes.

Execution `DONE` never closes a frame, because it proves only the bounded Execution obligation.

Before `COMPLETE`, the already-running Brain validates the frame's explicit DONE against referenced evidence, writes a completion-decision artifact, and formally RunSkeptic-reviews that exact artifact, because closure must be independently challenged at the frame that owns DONE.

```text
# Completion Decision
task_ref: <current frame>
done_condition: <frame DONE>
claimed_result: <concise result>
evidence_refs:
- <authoritative evidence>
qualifications_or_unknowns:
- <item or NONE>
plan_ref: <reviewed plan reference or NONE>
closure_request: COMPLETE
```

`COMPLETE` is legal only when DONE remains established and completion review leaves no unresolved material ACTION, CONFLICT, review-required status, DECOMPOSE path, or blocking unknown, because apparent completion must reopen while preserving the finding and evidence when verification finds a hole.

Closure is binary rather than percentage-based, because explicit DONE is more reliable than pseudo-precise progress estimates.

A child closure never terminalizes TP and instead returns a curated result to a fresh parent Brain through its recorded parent references, because the parent may have wider scope, alternate routes, or authority.

The parent independently reevaluates its own frame after a child closes, because child success or failure is evidence for the parent rather than automatic parent outcome.

A root frame follows the same validation and closure rules and terminalizes only because `parent_task_ref = NONE`, because mission closure must not have a second semantic path.

`BLOCKED` is used when a concrete required condition or capability is unavailable and no permitted action inside the frame can establish it, because external absence differs from unresolved semantic choice.

`CONFLICT` is used when no reliable plan or justified next step can be defended, governing alternatives cannot be reconciled, or repeated repair has no new information, because guessing must fail upward rather than become hidden work.

A closing `BLOCKED` or `CONFLICT` handoff carries the useful knowns, unknowns, evidence, alternatives when applicable, missing authority/capability/evidence, and wider-context possibilities, because failure propagation should improve the parent's next decision.

## Semantic artifacts and entrances

Every Brain writes one concise-complete handoff for its current frame, because a fresh successor or resumed parent must continue without reconstructing semantic history.

Brain persists only concise externally useful decision state and references rather than private scratch reasoning, because durable state exists for continuation rather than to preserve hidden cognition.

```text
# Brain Handoff
task_ref: <current frame>
task_state: OPEN | COMPLETE | BLOCKED | CONFLICT
established:
- <still-relevant fact with evidence reference>
open_unknowns:
- <decision-relevant unknown or NONE>
plan_state:
  plan_ref: <reviewed or candidate plan reference or NONE>
  plan_review_ref: <matching review reference or NONE>
  validity: VALID | INVALID | NONE
  progress: <completed items / active branch / next planned item / NONE>
reason_for_next_state:
- <concise externally useful reason>
done_validation:
  satisfied: YES | NO | UNKNOWN
  completion_decision_ref: <reference or NONE>
  completion_review_ref: <matching review reference or NONE>
  evidence_refs:
  - <reference or NONE>
  reason: <concise basis>
result_for_parent:
- <curated closure result when closed, otherwise NONE>
```

A `VALID` plan requires a matching review bound to the exact plan reference and no observed current Skeptic source identity that conflicts with the review receipt; a `COMPLETE` task state requires `done_validation.satisfied: YES` plus matching completion decision and review references, because accepted semantic state must remain traceable to exact review evidence while a known authority change invalidates reliance without adding a separate staleness state.

The planning-decision artifact owns plan meaning while the Brain handoff is the single continuation location for current `plan_ref`, `plan_review_ref`, validity, and progress, because duplicating those plan-state references in mechanical control would add mismatch risk without giving bootstrap a mechanical decision it needs to make.

Bootstrap instantiates a Brain entrance from the current frame and accepted references rather than by restating the whole design, because Context Rules favor a task-sized entrance with authoritative depth reachable by reference.

A resumed Brain resolves current plan state from the accepted prior Brain handoff, because plan state is semantic context for Brain rather than control state for bootstrap.

```text
ROLE: TP BRAIN
AUTHORITY: <authority_ref>
CURRENT_FRAME: <current_task_ref or NONE for first Brain>
PRIOR_HANDOFF: <prior_brain_handoff_ref or NONE>
EXECUTION_RESULT: <execution_result_ref or NONE>
CHILD_RESULT: <child_result_ref or NONE>
PROGRESS: <progress_ref>
MISSION: <mission_ref, required on first Brain and otherwise reachable>
SKEPTIC_SOURCE_LOCATOR: <skeptic_source_locator_ref>
OBLIGATION: apply the Brain semantic contract in this design to the current frame
RETURN: one Brain control object plus the artifacts required by the chosen transition
```

On the first Brain, the ordinary Brain contract creates the mission frame from the exact mission and checks concise-complete fidelity before proceeding, because startup needs one structural anchor without creating a special root reasoning path.

## Execution contract

Brain writes the exact task-specific Execution prompt and bootstrap passes it unchanged, because semantic task preparation belongs to Brain rather than the control plane.

```text
task_ref: <current frame>
objective: <one coherent bounded outcome>
done: <observable Execution completion condition>
allowed_scope: <permitted actions and boundaries>
starting_refs:
- <minimum task-sized references>
instructions: <exact work Brain wants performed>
required_outputs:
- <work product or evidence>
- one curated Execution handoff
verification: <checks for the bounded outcome>
stop_conditions: <conditions requiring NOT_DONE or UNKNOWN rather than guessing or widening scope>
```

Execution stays inside that prompt, may use all tools/commands/scripts/retrieval/research/implementation/tests needed for the bounded obligation, preserves substantial reusable evidence durably, performs the required verification, and does not navigate frames or revise the task-level plan, because Execution owns work but not TP semantics.

Execution returns `DONE` only when its bounded DONE is established, `NOT_DONE` when that condition is established not to be satisfied, and `UNKNOWN` when outcome or effects cannot safely be established, because continuation belongs to the fresh Brain that follows and uncertain effects must remain explicit.

```text
# Execution Handoff
execution_prompt_ref: <reference>
summary: <concise outcome>
material_findings:
- <decision-relevant finding with source reference>
verification:
- <check and observed result>
unknowns_or_qualifications:
- <item or NONE>
outputs_and_evidence:
- <authoritative reference>
side_effects:
- <observed effects or NONE>
```

An Execution handoff may be very short when the result is trivial, because concise completeness should not become reporting ceremony.

## Mechanical control protocol

Brain control contains only fixed continuation fields and references, because bootstrap must apply Brain's semantic decision without interpreting its meaning.

```json
{
  "next": "BRAIN | EXECUTION | TERMINAL",
  "route": "<authorized host-resolvable route token> | NONE",
  "resume_brain_route": "<authorized host-resolvable Brain route token> | NONE",
  "current_task_ref": "<task frame reference>",
  "next_task_ref": "<task frame reference> | NONE",
  "handoff_ref": "<Brain handoff reference>",
  "completion_decision_ref": "<completion-decision reference> | NONE",
  "completion_review_ref": "<completion RunSkeptic receipt reference> | NONE",
  "execution_prompt_ref": "<Brain-authored Execution prompt reference> | NONE",
  "status": "COMPLETE | BLOCKED | CONFLICT | NONE"
}
```

Bootstrap accepts only the listed combinations and rejects every other combination visibly, because a meaning-blind controller must not normalize contradictory semantic intent.

| Transition | `next` | `status` | `route` | `resume_brain_route` | `next_task_ref` | `execution_prompt_ref` |
|---|---|---|---|---|---|---|
| Continue/reason same frame | BRAIN | NONE | required | NONE | current frame | NONE |
| Open child | BRAIN | NONE | required | NONE | new child | NONE |
| Close child COMPLETE | BRAIN | COMPLETE | required | NONE | declared parent | NONE |
| Close child BLOCKED | BRAIN | BLOCKED | required | NONE | declared parent | NONE |
| Close child CONFLICT | BRAIN | CONFLICT | required | NONE | declared parent | NONE |
| Dispatch bounded work | EXECUTION | NONE | required | required | NONE | required |
| Close root COMPLETE | TERMINAL | COMPLETE | NONE | NONE | NONE | NONE |
| Close root BLOCKED | TERMINAL | BLOCKED | NONE | NONE | NONE | NONE |
| Close root CONFLICT | TERMINAL | CONFLICT | NONE | NONE | NONE | NONE |

Unused control fields are `NONE`, COMPLETE rows require both resolvable completion references, and non-COMPLETE rows carry no completion references, because each structural field must have one unambiguous control meaning.

On first-frame creation bootstrap accepts the mission anchor only when `parent_task_ref = NONE`, `parent_resume_ref = NONE`, and `origin_ref` resolves to the exact persisted mission, because startup structure must be trustworthy without semantic inspection.

On child creation bootstrap checks `child.parent_task_ref == current_task_ref` and `child.parent_resume_ref == handoff_ref`, because child return must target the exact parent state that created it.

On child close bootstrap checks `next_task_ref` against the child's recorded `parent_task_ref` and resolves its saved `parent_resume_ref`; on root close bootstrap checks `parent_task_ref = NONE`, because stack navigation is mechanical identity checking rather than semantic reconstruction.

Bootstrap checks only the existence and structural matching of completion references and never infers their semantic sufficiency, because semantic completion remains Brain-owned.

Execution control is limited to bounded outcome plus handoff reference, because Execution cannot choose TP continuation.

```json
{
  "status": "DONE | NOT_DONE | UNKNOWN",
  "handoff_ref": "<Execution handoff reference>"
}
```

After any mechanically accepted Execution return bootstrap launches the next fresh Brain on the recorded `resume_brain_route` with the same current frame and returned Execution handoff, because neither Execution nor bootstrap owns semantic continuation.

Malformed Brain control is a visible host/protocol error and malformed or failed Execution transport becomes mechanical UNKNOWN for a fresh Brain, because protocol defects must not be guessed into semantic outcomes.

## Minimal ledger, usage, and native lifecycle

The ledger stores accepted control boundaries rather than semantic prose, because its purpose is restart and reference navigation.

```json
{"seq":1,"event":"DISPATCH_INTENT","role":"BRAIN","route":"...","task_ref":"..."}
{"seq":1,"event":"RETURN","role":"BRAIN","next":"EXECUTION","route":"...","resume_brain_route":"...","task_ref":"...","handoff_ref":"...","execution_prompt_ref":"..."}
{"seq":2,"event":"DISPATCH_INTENT","role":"EXECUTION","route":"...","resume_brain_route":"...","task_ref":"...","execution_prompt_ref":"..."}
{"seq":2,"event":"RETURN","role":"EXECUTION","task_ref":"...","status":"DONE","handoff_ref":"..."}
```

`seq` is monotonic ordering only and no mutable semantic task registry or controller-owned execution queue is required, because task identity and ancestry live in task references while the latest accepted references reconstruct continuation.

Directly observable route, token, cache, elapsed-time, provider-cost, and similar usage metadata may be recorded while unavailable values remain UNKNOWN or omitted, because diagnostics must not invent hidden runtime facts or control continuation or semantic acceptance.

Formal RunSkeptic counts are derived from persisted review receipts rather than extra semantic invocations, because review frequency and model-call count are different cost dimensions.

One TP run has at most one live TP semantic child at a time while independent different-workspace runs may proceed concurrently, because same-run or same-workspace duplicate semantic workers can race but isolated runs need no machine-wide singleton.

Before semantic launch bootstrap checks collision-relevant activity for the same run or workspace and surfaces uncertain ownership rather than killing it, because process ownership must not be guessed.

TP relies on host-native direct-child ownership, bounded execution, and cancellation rather than adding a provider-specific watchdog, because extra lifecycle machinery requires a demonstrated failure mode.

If the host cannot supply or launch an authorized route or preserve the required native child invariant, it reports host/route unavailability rather than semantic TP failure, because control-plane failure must not masquerade as task judgment.

## Qualification and acceptance

A realization is accepted only when the observations below hold, because implementation must prove the design without reintroducing semantic special cases, controller intelligence, unsafe replay, wandering, or gratuitous fragmentation.

| Area / scenario | Required observation |
|---|---|
| Mission frame | first Brain creates ordinary frame with exact mission origin, parent NONE, resume NONE, then uses ordinary REASON |
| Uniform descendants | child frames use the same frame, REASON, plan, review, closure, and failure rules as mission |
| Local context | fresh Brain continues from task-sized curated state without routinely loading root or unrelated ancestry; additional authorized evidence remains reachable |
| Existing valid plan | fresh Brain continues an unchanged reviewed plan without rerunning plan review while its ordinary plan commitments remain valid and no observed current Skeptic source identity conflicts with its review receipt |
| Skeptic unavailable | mandatory plan/completion review does not proceed or claim compliance |
| Skeptic source change is observed while a plan is open | observed identity mismatch -> unchanged plan cannot support further plan-derived work -> formal re-review under current Skeptic -> no watcher or `NEEDS_REVIEW` state is required |
| Complete plan | exact planning decision is formally RunSkeptic-reviewed by the same Brain before adoption |
| Plan material change | new immutable plan and matching new review are required |
| Hierarchical plan | parent has credible end-to-end path while bounded child determines internal HOW |
| Child-local change | parent plan remains valid when parent commitments remain valid |
| Parent-invalidating child result | affected parent plan is invalidated and replanned/reviewed |
| Alternatives | real alternatives are challenged when present and ceremonial alternatives are not manufactured |
| Ambiguity progress | probe names blocking uncertainty, expected decision value, and result class that would change next decision |
| Ambiguity reassessment | fresh Brain checks whether the uncertainty materially decreased after the result |
| Ambiguity stagnation | equivalent failed evidence path is not repeated without materially new information value |
| Progressive ambiguity | successive informative probes may converge to a complete reviewable plan |
| No defensible continuation | capability gap is distinguished from missing evidence/authority/feasibility, then justified escalation or useful BLOCKED/CONFLICT occurs |
| Large coherent Execution | many mechanical/operational actions remain one Execution when semantic objective/scope/authority/outcome stay coherent |
| Child economy | child appears only when localized semantic context, evolving plan, and independent DONE add material value |
| Child creation | bootstrap verifies exact parent and parent-resume identities |
| Child COMPLETE | child DONE plus completion decision and review return curated result to fresh parent Brain |
| Child BLOCKED/CONFLICT | useful failure reasoning returns upward rather than terminalizing TP |
| Parent completion | parent independently establishes its own DONE and completion review after integrating child/action evidence |
| False completion | missing integration/publication/evidence prevents COMPLETE even when local tests or work pass |
| Mission completion | root uses ordinary completion review then terminalizes only because parent is NONE |
| Malformed COMPLETE | missing/unresolvable completion references are mechanically rejected |
| Contradictory control | unlisted combinations such as COMPLETE plus EXECUTION are visibly rejected |
| Execution NOT_DONE/UNKNOWN | result returns to fresh Brain and does not itself close frame |
| Uncertain Execution | unmatched dispatch is never automatically replayed and becomes mechanical UNKNOWN |
| Restart | accepted ledger prefix and referenced artifacts determine continuation without semantic guessing |
| Deep restart | nested current frame, parent resume, reviewed-plan identity, and uncertain-effect protections survive restart |
| Brain interruption | unreturned Brain does not advance accepted semantic state and retry obeys route/retry authorization |
| Routing | first route is host supplied; later Execution/resume/escalation routes are Brain-owned under routing policy and bootstrap-applied mechanically |
| Same-run activity | duplicate live semantic child is prevented while ownership uncertainty is surfaced rather than killed |
| Concurrent workspaces | independent isolated runs can proceed |
| Cost observability | semantic invocation counts and review counts are derivable; only observed usage facts are recorded |
| Provider neutrality | semantics do not depend on one provider-specific invocation mechanism |

## Realization rule

Existing TP implementation conforms only where it matches this design, because historical implementation detail must not retain design authority after adoption.

Repository workflow and routing authority statements must point to this artifact as TP design authority, because competing canonical ownership would make later change and simplification unsafe.

A realization change that needs new shared TP semantics updates this design first, because implementation must not become accidental design authority.

No separate TP Architecture Description or Software Design Description is required while this artifact remains concise-complete, because one shared design artifact is sufficient for TP's bounded scope.
