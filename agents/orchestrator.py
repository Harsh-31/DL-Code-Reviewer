from langgraph.graph import StateGraph, END
from typing import TypedDict, List


class ReviewState(TypedDict):
    code: str
    language: str
    file_path: str
    syntax_issues: List[dict]
    adversarial_questions: List[dict]
    explanation: str
    remediation: List[dict]
    quality_score: int
    executive_summary: str
    revised_code: str
    final_report: str


def create_review_graph(llm):
    from agents.syntax_agent import make_syntax_node
    from agents.adversarial_agent import make_adversarial_node
    from agents.explainer_agent import make_explainer_node
    from agents.remediation_agent import make_remediation_node

    graph = StateGraph(ReviewState)

    graph.add_node("syntax_check",       make_syntax_node(llm))
    graph.add_node("adversarial_review", make_adversarial_node(llm))
    graph.add_node("rubber_duck_explain",make_explainer_node(llm))
    graph.add_node("remediation",        make_remediation_node(llm))

    graph.set_entry_point("syntax_check")
    graph.add_edge("syntax_check",        "adversarial_review")
    graph.add_edge("adversarial_review",  "rubber_duck_explain")
    graph.add_edge("rubber_duck_explain", "remediation")
    graph.add_edge("remediation",         END)

    return graph.compile()
