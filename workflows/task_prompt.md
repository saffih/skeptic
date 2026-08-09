# Task Prompt

This file is the complete and only authority for the Task Prompt (TP) workflow.
Together with `MUST_READ_FIRST.md` it is everything needed to run TP. TP does
not defer to a generic Lead role, a Planner role, a Validator role, a Boundary
role, or a separate return contract; where TP needs such a rule, the rule is
stated here.

TP exists for one practical reason: to protect the controlling context and make
development reliable by performing every piece of substantive thinking in a
fresh bounded invocation.

## Invocation

`TP: <task>` is the Task Prompt invocation syntax. The text after `TP:`
is the governing user task input, and it activates this workflow. The
top-level invocation that receives it becomes the TP controller, and this
file is that controller's Lead contract.

A well-formed task input states objective, scope, constraints, success
criteria, permitted actions, and — when relevant — prohibited actions. TP runs
on whatever text it is given and never rewrites that text.

## Roles

TP has exactly two kinds of participant.

**The TP controller** is the top-level invocation. It is domain-blind: it holds
control state and performs mechanics. It decides nothing whose correctness
depends on what the mission means.

**Bounded semantic invocations** are fresh children:

- **TP Brain** — the standing semantic role that understands the mission and
  states what to do next;
- **work blocks** — bounded children that perform the work Brain defines.

TP has no Planner role and no Validator role. No RunSkeptic review, reviewer,
qualifier, planning, or validation stage is mandatory. Brain specifies such a
stage as an ordinary work block only when the mission actually requires it, or
when governing authority independently requires it.

Delegation is mandatory: every substantive action in TP runs in a bounded
child.

## Controller responsibilities

The controller may do only these things:

1. recognize the invocation as a Task Prompt;
2. persist the exact verbatim task text and the control identity needed to
   resume;
3. load this file and `MUST_READ_FIRST.md`;
4. resolve mechanically known control facts — the persisted-intent reference,
   the run storage reference, a dispatch identifier unique within this task,
   and the absolute repository root path only so far as it is needed to make
   those references receiver-resolvable;
5. dispatch bounded children and record their results;
6. follow continuation that is already deterministically specified;
7. perform mechanical completion once Brain has declared semantic completion;
8. report.

Everything else belongs to a bounded child.

### Persisting exact intent

Before the first dispatch the controller writes the verbatim task text to a
durable host-authorized file and keeps the path. That file, not the
conversation, is what later invocations resolve. The controller never edits,
summarizes, or re-expresses the persisted text.

Run state — persisted intent, control state, and block results — goes in the
host's run or scratch directory when one exists; on the Claude Code path that
is the session scratchpad directory the host names in the environment. Fall
back to a repository-local ignored directory only when no host scratch
directory exists. Run state is never written into tracked repository state,
because run artifacts are not repository authority.

### Durable continuation admission

Before its first dispatch, the controller creates a durable controller-authored
continuation record in run storage. The record has a newly generated run
identity, the receiver-resolvable `run_ref`, the receiver-resolvable
`intent_ref`, and a SHA-256 digest of the exact persisted intent bytes. The
record is valid only when those bindings still equal the resumed run storage
and persisted intent; its run identity is never copied into another run.

Its canonical record schema is exactly:

```
CONTINUATION_RECORD
run_id
run_ref
intent_ref
intent_sha256
dispatches[]: dispatch_id, role, requested_route, mapped_model, effort, packet, state, result
role: "TP_BRAIN" | "TP_BLOCK"
packet: exact issued packet field names and values for role
state: ADMITTED | RETURNED | ROUTE_UNAVAILABLE
result: NONE | exact returned TP_RESULT field names and values
entry identity: packet.dispatch_id = dispatch_id
returned identity: result.TP_RESULT.dispatch_id = dispatch_id
```

Its finite and exhaustive entry transitions are exactly:

```
CONTINUATION_TRANSITIONS
ADMITTED (result=NONE) -> RETURNED (structurally valid result and returned identity match)
ADMITTED (result=NONE) -> ROUTE_UNAVAILABLE (result=NONE)
RETURNED -> no transition
ROUTE_UNAVAILABLE -> no transition
```

No other state, transition, entry field, or top-level record field is valid.

The controller appends one mechanical dispatch entry before asking transport to
create a child. That entry preserves verbatim the issued `dispatch_id`, role,
requested route, mapped model, fixed effort, and every packet field/reference
value. Its admission state is initially `ADMITTED`. On an unavailable
transport it records `ROUTE_UNAVAILABLE`; on a structurally valid return it
records `RETURNED` and preserves verbatim every `TP_RESULT` field and reference
value. The record contains no semantic artifact body, summary, interpretation,
or reconstructed value.

On resume, before any semantic dispatch or replay, the controller validates
the exact record format, run and intent bindings, digest, unique dispatch IDs,
finite allowed state transitions, and the structural validity and identity
match of every recorded return. A missing, malformed, identity-mismatched,
substituted, or unresolved `ADMITTED` entry stops the run with a mechanical
`BLOCKED` or `CONFLICT` outcome; the controller neither reconstructs the record
nor retries the admitted child. A returned terminal Brain result remains
terminal. When the latest entry is a fully recorded returned Brain result with
`status=DONE`, `next=<block_ref>`, and `route=LOW|MEDIUM|STRONG`, and no dispatch
for that selected block was admitted, the controller dispatches exactly that
recorded block exactly once using its recorded block reference and route. After
a fully recorded returned work block, or a fully recorded work-block
`ROUTE_UNAVAILABLE`, the controller issues exactly one fresh Brain dispatch at
the recorded current Brain route. It never replays an admitted block and never
opens a block artifact to choose continuation.

### Pre-dispatch prohibition

Before the first TP Brain dispatch the controller's behavior is a closed
positive allowlist, not a general permission bounded by exceptions. The whole
of it is: follow the fixed repository orientation needed to reach this file;
read `MUST_READ_FIRST.md` and this file; persist the exact TP intent;
establish run storage and the mechanical identifiers; resolve the repository
root path only as needed to make references resolvable; construct the exact
`TP_BRAIN` packet defined under "First transition"; invoke Brain.

It performs only steps 1–4 above, and step 3's file reads are themselves closed
to the fixed orientation set: `CLAUDE.md` only if the host requires a manual
bootstrap read, `AGENTS.md` only if not already supplied by the host,
`MUST_READ_FIRST.md`, and this file. Nothing else is permitted before Brain.
No status, log, diff, show, fetch, pull, HEAD, branch, remote, history, or
worktree inspection, no task-specific read or search, no test run, and no
semantic route decision occurs before Brain. Any other read, search, command,
or inspection is a violation of this workflow, including:

- reading a file the task text names;
- grepping or searching for a term the task text uses;
- listing or inspecting history, plans, tests, or prior work;
- sampling a file "to size the task";
- composing a summary, restatement, decomposition, or work-block list from the
  task text;
- any Git command other than resolving the absolute repository root, and even
  that only by running exactly `git rev-parse --show-toplevel`, and only when
  host cwd/path information does not already give it. In particular,
  `status`, `log`, `diff`, `show`, `fetch`, `pull`, `branch`, `remote`, HEAD,
  ancestry, and worktree-state inspection are all prohibited before Brain,
  with no exception for repository-identity purposes. Git safety, status, and
  ancestry checks the mission needs occur after the first Brain dispatch, as
  Brain-defined bounded work, never as bootstrap steps.

Content the controller composed from the task text is controller-authored
decomposition even when no file was read, and it is prohibited for the same
reason reading is. Reading is a violation whether or not it looks cheap: the
failure this rule prevents is the control plane spending its own context on
material that belongs in a bounded child. If the controller believes it cannot
dispatch without knowing something about the mission, that belief is the signal
to dispatch Brain, not to read.

## Transport

A fresh bounded invocation is an actual new native subagent context. TP defines
the abstract operation only:

    launch fresh native subagent(role, route, effort, reference packet)

The host supplies the native capability and applies its route token and effort
metadata. TP does not prescribe a CLI, process, adapter, or provider-specific
transport. The controller passes references only; it never copies substantive
bodies.

For Codex, the host mapping is:

    LOW    = gpt-5.6-luna
    MEDIUM = gpt-5.6-terra
    STRONG = gpt-5.6-sol

Reasoning effort is selected independently from route and model class: TP fixes
the requested effort at `medium` for every Brain and work-block invocation.
This is a separate workflow-fixed invocation value, not something derived from
`LOW`, `MEDIUM`, or `STRONG` and not a field in `TP_BRAIN`, `TP_BLOCK`, or
`TP_RESULT`.

These model names appear only in this host mapping, never in `TP_BRAIN` or
`TP_BLOCK`. Each token maps only to the named model. If that mapped model is
unavailable, the dispatch is `ROUTE_UNAVAILABLE`; the controller never performs
semantic fallback or substitutes another model. In particular, unavailable
`gpt-5.6-luna` is not silently replaced by `gpt-5.6-terra`.

## First transition

The first transition is fixed: the controller dispatches a fresh TP Brain from
the mechanically known references, before any other work.

The initial Brain route is always `MEDIUM`. Brain never starts at `LOW`.

The Brain invocation carries exactly this control packet and nothing else:

```
TP_BRAIN
workflow_ref: <receiver-resolvable reference to workflows/task_prompt.md>
intent_ref: <receiver-resolvable reference to the persisted verbatim TP intent>
run_ref: <receiver-resolvable reference to run storage>
dispatch_id: <mechanically generated identifier unique within this task>
```

Every field is a reference or an identifier the controller can produce without
knowing what the mission means. No task body, authority body, prohibition list,
schema prose, mission summary, expected-result prose, work-block definition,
repository evidence, or other substantive content may be copied into the
invocation. This is the whole packet; there is no optional extra field and no
place for mission-derived framing, guidance, or breakdown.

Brain resolves `workflow_ref` and `intent_ref` itself, and reads its own
authority ("TP Brain"), its boundaries ("Brain boundaries"), and the shape of
its return from `workflow_ref`. None of that is transported to it.

Every later Brain dispatch uses the same workflow, intent, and run references,
with only a new `dispatch_id`; route is invocation metadata, not packet body.

If no authorized Brain role or reference can be established, the controller
stops with `CONFLICT`; an established role whose requested native route is
unavailable uses the mechanical `BLOCKED` route below.

A supplied draft, plan, or work-block list is Brain input only. Controller
authored, same-runtime, supplied, previously approved, planning-not-required,
or role-name-only control state cannot satisfy this transition, because each of
those routes returns to the control plane the semantic work this transition
exists to keep out of it.

## TP Brain

TP Brain owns everything whose correctness depends on domain meaning:

- **mission understanding** — resolving the persisted verbatim task text into
  what is actually being asked;
- **repository and source discovery** — finding and selecting the files,
  commits, contracts, and other material the mission requires;
- **decomposition** into bounded work blocks;
- **process selection** — choosing the smallest process sufficient for the
  actual mission;
- **work-block preparation** — producing control state complete enough for the
  controller to dispatch mechanically.

Brain resolves its starting references and then independently loads any other
already-authorized source its obligation requires. The deliberately small
bootstrap set is never a reason for the controller to have read more first.

### Brain's supporting subagents

Brain must not absorb the whole mission into its own context. When its working
set would grow materially — broad search, bulk reading, repeated analysis —
Brain dispatches its own bounded children by the same transport, gives each a
narrow obligation, and requires each to write results to a durable file and
return a reference. A MEDIUM Brain may request one fresh STRONG Brain with the
same workflow, intent, and run references; after that escalation Brain cannot
downgrade.

Brain expands its own context only for what it must judge itself. If a
discovery or analysis step can be described well enough to delegate, it is
delegated.

### Brain output

Brain writes its substantive material — mission understanding, discovery
results, decomposition, process selection, and each fully specified work
block — to durable artifacts in run storage. That material never travels
through the controller.

Brain returns one TP result packet exposing exactly one next action and route:

- a receiver-resolvable reference to a single durable work-block artifact; or
- the token `BRAIN_REDISPATCH`; or
- the terminal token `MISSION_COMPLETE`; or
- `BLOCKED` or `CONFLICT`.

Brain never returns an inline work-block list, an ordered set of blocks, an
expanded block definition, or more than one block reference at a time. Handing
the controller several blocks at once would put continuation back into the
control plane, which is the thing this workflow exists to prevent; handing it
one reference keeps continuation in Brain.

Brain returns terminal `BLOCKED` only when it determines that the mission
cannot proceed through any valid authorized and available route or reference.
One unavailable candidate route or failed block is not enough when Brain can
select a valid continuation.

`MISSION_COMPLETE` is the only way a TP run ends successfully, and only Brain
may emit it. It is a semantic judgement about the mission, not an approval of
Brain's own control state: Brain declares that the work the blocks produced
satisfies the persisted intent.

The referenced work-block artifact — not the return, and not the dispatch —
supplies every substantive non-routing value the worker needs and the
controller would otherwise have to invent: block identifier; objective;
admitted references; authority; prohibitions; expected result; the validation
or acceptance gate that applies to that block; and escalation condition. All of
it lives in the artifact. It must not name a requested model, model class,
route token, or reasoning effort: Brain's `TP_RESULT.route` is the single route
and model selection for that block, and TP's workflow-fixed `medium` is its
single effort selection.

The controller never reads that artifact, so it cannot detect an incomplete
one. A block artifact that leaves a semantic field unfilled is incomplete, and
the worker that resolves it returns `BLOCKED`; the controller passes that
result back to Brain rather than filling anything in.

### Brain boundaries

Brain may understand, discover, decompose, and control. It may not alter the
persisted task objective, execute the work blocks it defines, or integrate or
publish changes. It may not declare `MISSION_COMPLETE` on the strength of its
own control state alone — the declaration must rest on returned block results.
It does not
define, redefine, or redesign STT. Do not append transcripts, raw logs,
correction chains, or repeated task text to control state. If no authorized
Brain route exists, return `CONFLICT`.

## Work blocks

The bounded work block is TP's unit of execution. The controller dispatches the
single block Brain referenced, over the transport above, carrying exactly this
control packet and nothing else:

```
TP_BLOCK
workflow_ref: <receiver-resolvable reference to workflows/task_prompt.md>
block_ref: <receiver-resolvable reference to the durable work-block artifact>
run_ref: <receiver-resolvable reference to run storage>
dispatch_id: <mechanically generated identifier unique within this task>
```

The worker independently reads `workflow_ref` and `block_ref`. The substantive
objective, sources, constraints, expected result, validation requirements,
authority, and prohibitions live in `block_ref`; they are not copied through
the controller and are not restated in the dispatch. Route and model selection
do not live there: Brain returns the route once in `TP_RESULT.route`, and the
controller applies that token as invocation metadata. The controller does not
select, gate, reorder, or second-guess Brain's process, and it holds no block
queue.

Each block is dispatched for execution exactly once. Repeating a block requires
new Brain control state, so that retried work is a deliberate semantic
decision rather than a control-plane reflex.

Substantial objectives, sources, and results move by receiver-resolvable
reference. A block writes its substantive output to a durable file and returns
the path; the controller never carries a substantive body through itself to
hand to the next block.

For trivial read-only work or one specified deterministic command, a bounded
child still performs the action outside the controller's context; no
trivial-work exception skips bounded-child dispatch itself. For such work a
bounded child may use the smallest control packet and omit unnecessary
ceremony — the dispatch packet above is already minimal, so what narrows is
what `block_ref` must contain, never the Brain-first requirement.

Deterministic checks are work blocks like any other; the controller does not run
them in its own context. Brain sequences them as blocks, and — like every other
block — before it declares the mission complete.

### TP result packet

Every bounded child — Brain or work block — returns exactly this structure and
nothing else:

```
TP_RESULT
dispatch_id: <the identifier the controller issued>
status: DONE | BLOCKED | CONFLICT
result_ref: <receiver-resolvable reference to the durable artifact, or NONE>
next: <block_ref> | BRAIN_REDISPATCH | MISSION_COMPLETE | NONE
route: LOW | MEDIUM | STRONG | NONE
```

This is TP's only runtime return shape. `route` is the sole mechanically
returned routing field. A work-block selection is `DONE` with
`next=<block_ref>` and
`route=LOW|MEDIUM|STRONG`; a stronger Brain request is `DONE` with
`next=BRAIN_REDISPATCH` and `route=STRONG`; completion is `DONE` with
`next=MISSION_COMPLETE` and `route=NONE`; blocked, conflict, and work-block
returns use `next=NONE` and `route=NONE`.

`next` carries a single block reference, `BRAIN_REDISPATCH`, or
`MISSION_COMPLETE` only from Brain. From a work block it is always `NONE`: a
work block does not decide continuation.

The controller validates this structure mechanically: exactly the required
fields are present, `dispatch_id` matches the one it issued, `status` and
`route` use the vocabulary, `next` uses its vocabulary, references resolve,
and the declared status/next/route combination is one of the combinations
above. Structural validity proves nothing about correctness — that judgment
belongs to a bounded child.

## Continuation

Continuation is never deterministic beyond one step. After every work block,
whatever its status, the controller dispatches a fresh Brain and lets Brain
decide the next block or the terminal state. There is no case in which the
controller advances to a following block on its own, because it was never given
one.

After a work block, the fresh Brain re-dispatch retains the current Brain route
(`MEDIUM` initially, `STRONG` after escalation); it never uses the work-block
route. For `BRAIN_REDISPATCH`, the
controller launches the same Brain role with the same workflow, intent, and run
references, a new `dispatch_id`, and `route=STRONG`. No semantic summary is
transferred; STRONG becomes the current Brain route and Brain cannot downgrade.
The block result reaches Brain by
reference, not through the packet: the controller records the return verbatim
in the durable continuation record in run storage, and Brain resolves that
record under `run_ref`. Appending is transcription, not authorship — the
controller adds no account, summary, or judgement of its own. Brain then issues
replacement control state, which supersedes the prior control state rather than
amending it.

This deliberately favors a simple domain-blind controller over reducing the
number of Brain invocations. The controller holds no plan, no block queue, and
no notion of progress; it holds only the current dispatch and the reference it
was handed.

The controller never inspects a substantive result to decide what happens next.

For every dispatch, the controller records the requested route token, its
mechanically mapped model, and the workflow-fixed `medium` effort in the run
ledger. This is mechanical transcription of routing metadata, not a semantic
choice. Actual model and effort are recorded as observed only when the native
host exposes them; when actual routing is hidden, the report uses
`ACTUAL_ROUTING_UNKNOWN`.

When a Brain dispatch itself returns `BLOCKED` or `CONFLICT`, there is no
further semantic authority to consult: the controller stops and reports the
blocker with its references. It does not retry Brain against the same state, and
it does not take over the judgement Brain declined to make.

## Completion

Semantic completion is Brain's decision: TP is finished when Brain returns
`MISSION_COMPLETE`. Mechanical completion is the controller's: recording final
statuses and references, and reporting. That is the whole of it.

`MISSION_COMPLETE` is strictly terminal. Whatever the mission actually
requires — tests, review, qualification, Git safety checks, publication, remote
verification, or anything else — occurs as Brain-selected work blocks before
Brain returns it. Once Brain has returned `MISSION_COMPLETE`, no further block
may be dispatched, and no test, review, acceptance gate, check, or publication
may run. The controller performs only deterministic terminal recording and user
reporting.

The lifecycle is therefore: Brain → required block → Brain → ... → final
required block → Brain → `MISSION_COMPLETE` → record and report only.

A check the controller wanted to run after `MISSION_COMPLETE` is a check Brain
should have sequenced as a block before it. Holding work back past the terminal
token would return mission-completing judgement to the control plane, which is
the failure this workflow exists to prevent.

The final transition of every TP run is therefore a Brain dispatch — which
follows from continuation rather than being a special case, since a Brain
dispatch follows every block. The controller dispatches the same `TP_BRAIN`
packet, Brain resolves the ledger and the durable result references under
`run_ref`, and the controller follows what comes back. It does
not open a block's output to judge whether the mission is done, and it does not
declare completion on its own. Reading a produced artifact to check the work is
exactly the inspection this workflow forbids, and it is forbidden at the end of
a run for the same reason it is forbidden at the start.

The report states the objective reference, control identity, dispatches,
statuses, artifact references, validation evidence, observable routing and
context status, deviations, and blockers. Hidden runtime facts are reported as
`UNKNOWN`.

## When fresh invocation is impossible

If a Brain invocation cannot be created because native transport or its
requested mapped model is unavailable, the controller records
`ROUTE_UNAVAILABLE` and a mechanical `BLOCKED` outcome with `next=NONE` and
`route=NONE`, then reports the terminal blocker: no Brain semantic authority is
available to choose a continuation.

If a work-block invocation cannot be created for the same reason, the
controller records `ROUTE_UNAVAILABLE` and that same mechanical `BLOCKED` shape
for the block dispatch in the durable continuation record, then launches a
fresh Brain at the current Brain route. The fresh Brain, not the controller, decides whether
another valid route can continue the mission or terminal `BLOCKED` is required.

In neither case is a semantic child synthesized for the failed dispatch, and no
fallback model is substituted.

It never falls back to performing the semantic work itself. A context or
transport failure is a failure to admit the work, not permission to move the
work into the control plane. Legitimate responses are: preserve completed
durable artifacts, reduce the bootstrap, or have a bounded semantic invocation
decompose the obligation into genuinely smaller work. If none is possible, stop
with an explicit blocker.

The same applies to an unavailable mandatory reference: stop with `CONFLICT`
rather than reconstructing the missing material in the controller.

## Routing

Brain selects `LOW`, `MEDIUM`, or `STRONG` semantically for each bounded work
block. The controller applies the returned route token mechanically and never
opens substantive references to choose it. Brain `LOW` is invalid; the initial
Brain is `MEDIUM`. A MEDIUM Brain may return `DONE` with
`next=BRAIN_REDISPATCH` and `route=STRONG`; the controller then launches the
same Brain role with unchanged workflow, intent, and run references and only a
new `dispatch_id`. STRONG is then current and no downgrade is permitted.

Routing does not bypass authorization owned by
`agents/model_routing_policy.md`. When that policy requires a stop before an
unapproved premium route, Brain writes the required
`MODEL_ESCALATION_CHECKPOINT` into a durable blocker artifact and returns
`BLOCKED` with that artifact as `result_ref` and `route=NONE`. The controller
reports the reference and stops; it does not author, open, interpret, or
discharge the checkpoint, and silence is not authorization. No premium dispatch
occurs before the required authorization.

The controller never performs semantic fallback. A missing native route is
reported as `ROUTE_UNAVAILABLE` and `BLOCKED` with `route=NONE`. Route is
invocation metadata only and never enters `TP_BRAIN` or `TP_BLOCK`. No CLI or
Claude/Sonnet-specific transport is required or prescribed.

## Relationship to other systems

TP is the practical default development workflow and can develop anything in
this repository. STT is a separate system with its own runtime and authorities;
TP neither defines nor redesigns it, and TP terminology does not establish STT
contracts. Where a mission warrants STT, STT is invoked under its own authority
unchanged.
