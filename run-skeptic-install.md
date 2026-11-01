# Install RunSkeptic

Paste the instruction below once into your assistant.

```text
Install this as a persistent global/cross-chat instruction wherever your environment supports persistent memory:

Whenever I say RunSkeptic, read and execute the current public Skeptic:

https://github.com/saffih/skeptic/blob/main/skeptic.md

For every invocation, read the current skeptic.md rather than relying on memory, a summary, or an older version.

A cached copy may be used only when it can be established as current. Use its Git blob SHA when available, but lack of a SHA alone must not block RunSkeptic if the current source itself can be accessed and read.

The current skeptic.md always overrides this stored instruction.

A bare RunSkeptic is read-only unless I explicitly authorize changes.

If persistent global/cross-chat memory is available, store this binding there now so RunSkeptic works in future sessions without reinstalling it. Store the binding, not a copy of Skeptic.

If persistent memory is unavailable, keep this binding active for the current conversation/session and tell me that it will not persist to future sessions.

If you cannot access and read the current skeptic.md for an invocation, say so and do not claim RunSkeptic compliance.
```

## Optional Skeptic Grill

To use the separate decision-frontier questioning profile, request `Skeptic Grill: <goal>` (or `Decision Frontier: <goal>`). An assistant must freshly read **both** the current public [Skeptic runtime](https://github.com/saffih/skeptic/blob/main/skeptic.md) and the [optional Grill profile](https://github.com/saffih/skeptic/blob/main/decision-frontier.md) for that invocation; normal RunSkeptic assurance, authorization and action boundaries remain in force. Grill is read-only by default, is not automatically activated, and has not been behaviorally qualified merely by publication.

If you want a persistent shortcut in an assistant that supports such instructions, provide this separate binding (do not assume installing RunSkeptic automatically installs Grill):

```text
When I explicitly say "Skeptic Grill: <goal>" or "Decision Frontier: <goal>", freshly read both:
https://github.com/saffih/skeptic/blob/main/skeptic.md
https://github.com/saffih/skeptic/blob/main/decision-frontier.md
Follow the profile under the runtime's full existing assurance, permissions and source-freshness rules. Default to read-only; do not claim formal or independent review that was not executed. An incidental mention does not invoke Grill. If either file is inaccessible, disclose that and do not claim Grill compliance.
```

Installing or storing this binding depends on the receiving assistant's supported settings and capabilities; repository publication alone does not install it.
