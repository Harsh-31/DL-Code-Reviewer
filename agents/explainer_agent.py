def make_explainer_node(llm):
    def rubber_duck_explain(state: dict) -> dict:
        prompt = f"""You are a Rubber Duck Debugger.

Explain this {state["language"]} code out loud, as if you're a rubber duck thinking step by step.
Focus on what the code ACTUALLY does — not what it's supposed to do.
Highlight any surprising, non-obvious, or potentially dangerous behaviors.

Rules:
- Use plain English, no jargon
- Walk through it line-by-line or block-by-block
- Flag anything that "smells wrong" even if it's not a formal error
- Keep it concise: 3–5 short paragraphs

Code:
```{state["language"]}
{state["code"]}
```
"""
        response = llm.invoke(prompt)
        return {"explanation": response.content.strip()}

    return rubber_duck_explain
