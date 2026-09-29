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
