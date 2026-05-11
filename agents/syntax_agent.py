import json
from skills.loader import load_skill


def make_syntax_node(llm):
    def syntax_check(state: dict) -> dict:
        skill_context = load_skill(state["language"])

        prompt = f"""You are a strict syntax and lint checker for {state["language"]} code.

DOMAIN GUIDELINES:
{skill_context}

Analyze the code below for:
- Syntax errors
- Style violations
- Common pitfalls specific to {state["language"]}
- Unused or undriven signals/variables
- Type mismatches

Code:
```{state["language"]}
{state["code"]}
```

Return ONLY a valid JSON array (no markdown, no extra text). Each item must have:
  "line"       : line number (0 if general),
  "severity"   : "error" | "warning" | "info",
  "message"    : short description of the issue,
  "suggestion" : how to fix it
"""
        response = llm.invoke(prompt)
        raw = response.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        try:
            issues = json.loads(raw)
        except json.JSONDecodeError:
            issues = [{
                "line": 0, "severity": "info",
                "message": "Could not parse structured output.",
                "suggestion": raw
            }]

        return {"syntax_issues": issues}

    return syntax_check
