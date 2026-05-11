import json
import re


def make_remediation_node(llm):
    def remediation(state: dict) -> dict:
        syntax_str     = json.dumps(state["syntax_issues"],        indent=2)
        adversarial_str = json.dumps(state["adversarial_questions"], indent=2)
        explanation     = state["explanation"]

        prompt = f"""You are a senior engineer providing final remediation for {state["language"]} code.

--- SYNTAX ISSUES ---
{syntax_str}

--- ADVERSARIAL CONCERNS ---
{adversarial_str}

--- RUBBER DUCK WALKTHROUGH ---
{explanation}

--- ORIGINAL CODE ---
```{state["language"]}
{state["code"]}
```

Produce a JSON object with these exact keys:
  "fixes": array of objects, each with:
      "fix"          : description of the fix,
      "priority"     : "high" | "medium" | "low",
      "code_snippet" : short corrected code snippet (or "" if N/A)
  "quality_score"   : integer 0–100 (100 = production ready)
  "executive_summary": one paragraph plain-English summary for a non-expert
  "revised_code"    : full corrected version of the code

Return ONLY valid JSON. No markdown fences, no preamble.
"""
        response = llm.invoke(prompt)
        raw = response.content.strip()

        # Strip markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0]

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Last resort: try to extract JSON object
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    data = {}
            else:
                data = {}

        fixes             = data.get("fixes", [])
        quality_score     = int(data.get("quality_score", 50))
        executive_summary = data.get("executive_summary", response.content)
        revised_code      = data.get("revised_code", state["code"])

        # Build markdown report
        high   = [f for f in fixes if f.get("priority") == "high"]
        medium = [f for f in fixes if f.get("priority") == "medium"]
        low    = [f for f in fixes if f.get("priority") == "low"]

        final_report = f"""# DSL Code Review Report

**Language:** {state["language"]}
**File:** {state["file_path"]}
**Quality Score:** {quality_score}/100

---

## Executive Summary
{executive_summary}

---

## Findings Summary
| Category | Count |
|---|---|
| Syntax / Lint Issues | {len(state["syntax_issues"])} |
| Adversarial Concerns | {len(state["adversarial_questions"])} |
| High Priority Fixes | {len(high)} |
| Medium Priority Fixes | {len(medium)} |
| Low Priority Fixes | {len(low)} |

---

## Recommended Fixes

{"".join(f"### 🔴 {f['fix']}" + (f"\n```\n{f['code_snippet']}\n```" if f.get("code_snippet") else "") + "\n\n" for f in high)}
{"".join(f"### 🟡 {f['fix']}" + (f"\n```\n{f['code_snippet']}\n```" if f.get("code_snippet") else "") + "\n\n" for f in medium)}
{"".join(f"### 🟢 {f['fix']}" + (f"\n```\n{f['code_snippet']}\n```" if f.get("code_snippet") else "") + "\n\n" for f in low)}
"""

        return {
            "remediation":       fixes,
            "quality_score":     quality_score,
            "executive_summary": executive_summary,
            "revised_code":      revised_code,
            "final_report":      final_report,
        }

    return remediation
