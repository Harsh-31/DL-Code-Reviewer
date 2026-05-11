import json
from skills.loader import load_skill


def make_adversarial_node(llm):
    def adversarial_review(state: dict) -> dict:
        skill_context = load_skill(state["language"])
        prior_issues = len(state.get("syntax_issues", []))

        prompt = f"""You are an adversarial code reviewer for {state["language"]} code.
Your job is to challenge assumptions using first-principles thinking.

DOMAIN GUIDELINES:
{skill_context}

PRIOR FINDINGS: {prior_issues} syntax/lint issues were already found.

Ask tough questions like:
- Why was this design choice made over the obvious alternative?
- What edge cases or boundary inputs are not handled?
- What happens under race conditions, overflow, or concurrent access?
- Is this the most efficient / safest implementation?
- What implicit assumptions does this code make that could break?

Code:
```{state["language"]}
{state["code"]}
```

Return ONLY a valid JSON array (no markdown). Each item must have:
  "question" : the adversarial question or observation,
  "concern"  : what risk or failure mode this points to,
  "priority" : "high" | "medium" | "low"

Aim for 3–5 items. Be specific to the code, not generic.
"""
        response = llm.invoke(prompt)
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        try:
            questions = json.loads(raw)
        except json.JSONDecodeError:
            questions = [{
                "question": raw,
                "concern": "Could not parse structured output.",
                "priority": "medium"
            }]

        return {"adversarial_questions": questions}

    return adversarial_review
