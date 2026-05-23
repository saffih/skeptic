"""Question sets extracted from skeptic.md and skeptic-questions.md."""

# --- Universal Questions (skeptic.md section 2) ---
UNIVERSAL = {
    "UQ1": "What is this?",
    "UQ2": "What is it for?",
    "UQ3": "What depends on it, and what does it depend on?",
    "UQ4": "What must always be true?",
    "UQ5": "What breaks it?",
    "UQ6": "How do we know it works?",
}

# --- Charlie Munger (CH) - Systems, Dependencies, Failure ---
CH = {
    "CH1": "What depends on this?",
    "CH2": "What does this constrain?",
    "CH3": "What breaks downstream?",
    "CH4": "Is failure bounded?",
    "CH5": "Who bears failure cost?",
    "CH6": "What must/must not stay connected?",
    "CH7": "Is coupling necessary or accidental?",
    "CH8": "What would guarantee failure if unchanged?",
}

# --- Occam's Razor (OM) - Necessity, Simplicity, Boundaries ---
OM = {
    "OM1": "Remove this: what breaks?",
    "OM2": "Is this necessary?",
    "OM3": "What is missing?",
    "OM4": "Can this be simpler?",
    "OM5": "Is complexity justified?",
    "OM6": "Does this anticipate a need that does not yet exist?",
    "OM7": "Are concerns mixed?",
    "OM8": "Is the boundary clear?",
    "OM9": "What should move in or out?",
}

# --- Richard Feynman (FE) - Honesty, Explanation, Reality ---
FE = {
    "FE1": "Is this true now?",
    "FE2": "Can it be explained simply?",
    "FE3": "Does each non-obvious choice explain why?",
    "FE4": "When was it last verified?",
    "FE5": "Do tests prove behavior, not implementation?",
    "FE6": "Was the test ever red?",
}

# --- Karl Popper (PO) - Falsification, Contradiction, Unsafe Change ---
PO = {
    "PO1": "What would prove this wrong?",
    "PO2": "What would make this unsafe?",
    "PO3": "What fails silently?",
    "PO4": "What has no test or monitor?",
    "PO5": "Do rules or assumptions contradict?",
    "PO6": "Can failure be detected before damage spreads?",
}

# --- Immanuel Kant (KT) - Universalizability ---
KT = {
    "KT1": "Would I want this pattern everywhere, by every contributor?",
    "KT2": "If not, should it be removed, narrowed, replaced, or bounded?",
}

# --- Saffi (SH) - Sharp Trade-off Heuristics ---
SH = {
    "SH1": "What are the real forces/sides, and what middle is trying to combine them?",
    "SH2": "Is the middle creating real friction?",
    "SH3": "Is the middle a real integration, or just a compromise that keeps both costs?",
    "SH4": "Should Side A or Side B dominate as default?",
    "SH5": "What narrow exception protects the other side?",
    "SH6": "If no side should dominate and the middle is not valid, what conflict must be explicit?",
}

# --- Structural Checks (skeptic.md section 4) ---
STRUCTURAL = {
    "ST1": "role and ownership",
    "ST2": "boundaries and concern split",
    "ST3": "interfaces, required links, forbidden links, implicit links, contracts",
    "ST4": "necessary vs accidental coupling",
    "ST5": "source of truth and competing copies",
    "ST6": "data/control flow, update timing, consumers",
    "ST7": "reversibility, retry safety, and failure signal",
}

# --- Domain Questions (skeptic-questions.md) ---

# Security
SEC = {
    "SEC1": "PII in shared or public files?",
    "SEC2": "Subprocess or command from unsanitized user input?",
    "SEC3": "File read/written without permission check?",
    "SEC4": "Test-data vs real-data boundary enforced?",
    "SEC5": "Error messages expose internal paths or stack traces?",
    "SEC6": "Authentication check that can be bypassed?",
    "SEC7": "Symlinks validated before following?",
    "SEC8": "Secrets suppression that can be circumvented?",
}

# Complexity
CPX = {
    "CPX1": "Independent concerns tangled in one function?",
    "CPX2": "Code that should be data (lookup table, config, enum)?",
    "CPX3": "State implicit and scattered vs explicit and managed?",
    "CPX4": "Simple (few independent parts), or just familiar?",
    "CPX5": "How many things must you hold in your head to understand this?",
}

# Reliability
REL = {
    "REL1": "No monitoring — how would you know this is silently broken?",
    "REL2": "What fails at 10x scale?",
    "REL3": "What external dependency could break this without any code change?",
    "REL4": "Bus factor — who knows this, and what if they leave?",
    "REL5": "Single source of truth for each important datum?",
    "REL6": "Who owns this part or datum, and who is allowed to change it?",
    "REL7": "Is ownership/current responsibility clear enough to operate safely?",
}

# Data
DAT = {
    "DAT1": "Every external call (subprocess, network, DB) timed out?",
    "DAT2": "Race condition? Locks minimal and correct?",
    "DAT3": "What happens when disk is full or filesystem is read-only?",
    "DAT4": "Encoding explicit (UTF-8) or assumed?",
    "DAT5": "Where is this data authored?",
    "DAT6": "How often is it updated relative to reality?",
    "DAT7": "Who consumes it, and is consistency preserved over time?",
}

# Architecture
ARC = {
    "ARC1": "Implicit dependency that would surprise a new contributor?",
    "ARC2": "Circular dependency between modules?",
    "ARC3": "Data flow traceable from input to output?",
    "ARC4": "Interfaces/contracts explicit and correct?",
    "ARC5": "Relationship exists but is not written down?",
    "ARC6": "Connection missing, accidental, or misplaced?",
}

# Craft
CFT = {
    "CFT1": "Test names describe behavior, not implementation?",
    "CFT2": "Error message tells you HOW to fix it?",
    "CFT3": "Test mocks so much it only tests the mock?",
}

# Aggregate all domain questions
DOMAINS = {**SEC, **CPX, **REL, **DAT, **ARC, **CFT}

# --- Pre-built question set configurations ---

QUESTION_SETS = {
    "full_skeptic": {
        "description": "All questions from skeptic.md + skeptic-questions.md",
        "questions": {
            **UNIVERSAL, **CH, **OM, **FE, **PO, **KT, **SH,
            **STRUCTURAL, **DOMAINS,
        },
    },
    "universal_only": {
        "description": "Universal Questions only",
        "questions": UNIVERSAL,
    },
    "ch_only": {
        "description": "Charlie Munger questions only",
        "questions": CH,
    },
    "om_only": {
        "description": "Occam's Razor questions only",
        "questions": OM,
    },
    "fe_only": {
        "description": "Richard Feynman questions only",
        "questions": FE,
    },
    "po_only": {
        "description": "Karl Popper questions only",
        "questions": PO,
    },
    "kt_only": {
        "description": "Immanuel Kant questions only",
        "questions": KT,
    },
    "sh_only": {
        "description": "Saffi questions only",
        "questions": SH,
    },
    "ch_po": {
        "description": "Charlie Munger + Karl Popper",
        "questions": {**CH, **PO},
    },
    "ch_om": {
        "description": "Charlie Munger + Occam's Razor",
        "questions": {**CH, **OM},
    },
    "om_fe": {
        "description": "Occam's Razor + Richard Feynman",
        "questions": {**OM, **FE},
    },
    "po_fe": {
        "description": "Karl Popper + Richard Feynman",
        "questions": {**PO, **FE},
    },
    "ch_po_om": {
        "description": "Charlie Munger + Karl Popper + Occam's Razor",
        "questions": {**CH, **PO, **OM},
    },
    "razor": {
        "description": "Razor minimal set: OM remove, KT universalize, PO falsify, CH invert",
        "questions": {
            "OM1": OM["OM1"],   # Remove this: what breaks?
            "KT1": KT["KT1"],  # Would I want this pattern everywhere, by every contributor?
            "PO1": PO["PO1"],   # What would prove this wrong?
            "CH8": CH["CH8"],   # What would guarantee failure if unchanged?
        },
    },
    "structural_only": {
        "description": "Structural Checks only",
        "questions": STRUCTURAL,
    },
    "domains_only": {
        "description": "All domain questions (SEC, CPX, REL, DAT, ARC, CFT)",
        "questions": DOMAINS,
    },
    "thinkers_all": {
        "description": "All thinker questions without structural/domain",
        "questions": {**UNIVERSAL, **CH, **OM, **FE, **PO, **KT, **SH},
    },
}
