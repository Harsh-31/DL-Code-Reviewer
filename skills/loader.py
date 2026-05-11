import os

_SKILL_DIR = os.path.dirname(__file__)

_LANGUAGE_SKILL_MAP = {
    "verilog":        "verilog.md",
    "systemverilog":  "verilog.md",
    "sv":             "verilog.md",
    "sql":            "sql.md",
    "cuda":           "cuda.md",
    "cu":             "cuda.md",
    "vhdl":           "vhdl.md",
    "assembly":       "assembly.md",
    "asm":            "assembly.md",
    "matlab":         "sql.md",   # fallback to generic for now
}


def load_skill(language: str) -> str:
    """Load the domain-specific review guidelines for a language."""
    lang = language.lower().strip()
    filename = _LANGUAGE_SKILL_MAP.get(lang)

    if not filename:
        return f"Apply general best practices for {language} code review."

    filepath = os.path.join(_SKILL_DIR, filename)
    if not os.path.exists(filepath):
        return f"Apply general best practices for {language} code review."

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
