# Model Selection Policy

Model selection has independent dimensions:

- provider;
- model or model tier;
- reasoning effort;
- optional speed mode.

The task records the requested route. The receipt records requested and observed values separately. Use `UNKNOWN` when the runtime does not expose a value.

## Default operating policy

Use the cheapest route reasonably capable of the assigned role. Escalate only after observed insufficiency or when the task explicitly authorizes a stronger route.

Current experiment defaults:

- OpenAI Body: GPT-5.6 Luna, MEDIUM effort.
- OpenAI Brain: GPT-5.6 Sol, LOW effort.
- Claude Body candidate: Claude Haiku 4.5, MEDIUM effort.
- Claude Brain candidate: Claude Sonnet 5, MEDIUM effort.

Stronger planning or review candidates:

- GPT-5.6 Sol, MEDIUM or HIGH effort;
- Claude Opus 4.8, MEDIUM or HIGH effort.

Claude Fable 5 and maximum effort levels require explicit authorization.

## Safety and cost rules

1. Model tier and effort are separate choices.
2. A higher effort setting has no fixed universal cost multiplier; it may consume more reasoning/output tokens.
3. Do not silently substitute providers or models.
4. Do not silently raise effort or enable a premium speed mode.
5. Do not infer observed routing from the request. Record `UNKNOWN` when unobservable.
6. Product labels not confirmed by official documentation, including any locally displayed label such as `Tara`, remain unresolved identifiers until mapped by evidence.
7. Pricing is time-sensitive and belongs in the auxiliary findings note, not in the normative protocol.
