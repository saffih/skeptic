# Task

## Metadata

- Task ID:
- Title:
- Owner:
- Prompt mode: `OTP` (recommended) or `TP` (compatibility mode)
- Requested Body route:
- Requested Brain route:
- Maximum authorized route:
- Escalation policy:
- Observed routing:
- Status:

## OTP economy contract

Complete this section when `Prompt mode` is `OTP`. TP tasks may leave it empty and retain the existing workflow.

- Planning mode: `DETERMINISTIC`, `PLAN_ONCE`, or `ESCALATED`
- Maximum Brain invocations:
- Additional agents allowed:
- Authoritative inputs:
- Repository scan policy:
- Additional file discovery policy:
- Benchmark limit:
- QuickCompare limit:
- Skeptic review limit:
- Retry policy:
- Stop policy:

## Objective

## Context

## Constraints

## Authoritative input files

## Evidence files

## Required outputs

## Validation

## Success criteria

## Prohibited actions

## Usage rules

- File paths are authoritative.
- Large content remains in referenced files.
- Summaries are optional navigation aids and do not replace authoritative files.
- Missing evidence remains explicit.
- Unknown facts must not be converted into assumptions.
- For OTP, the economy contract is part of authorization: the Body must reject an otherwise executable plan that exceeds it.
- OTP is additive; selecting TP preserves the existing Task Prompt behavior.
