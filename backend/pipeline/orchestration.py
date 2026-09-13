from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

try:
    from backend.pipeline.automation_blueprint import generate_automation_blueprint
    from backend.pipeline.redesign import generate_redesign
    from backend.pipeline.schemas import Workflow
except ModuleNotFoundError:
    from pipeline.automation_blueprint import generate_automation_blueprint
    from pipeline.redesign import generate_redesign
    from pipeline.schemas import Workflow


class _GraphState(TypedDict):
    workflow: Workflow
    index: int


def run_orchestration(workflow: Workflow) -> Workflow:
    """Route scored steps through Phase 3 generators using a LangGraph graph."""
    def dispatch(state: _GraphState):
        return state

    def route(state: _GraphState) -> Literal["automate", "redesign", "leave_as_is", "done"]:
        if state["index"] >= len(state["workflow"].scores):
            return "done"
        return state["workflow"].scores[state["index"]].verdict

    def automate(state: _GraphState):
        workflow = state["workflow"]
        score = workflow.scores[state["index"]]
        step = next(item for item in workflow.steps if item.step_id == score.step_id)
        output = generate_automation_blueprint(step, score)
        return {"workflow": workflow.model_copy(update={"automation_blueprints": [*workflow.automation_blueprints, output]}), "index": state["index"] + 1}

    def redesign(state: _GraphState):
        workflow = state["workflow"]
        score = workflow.scores[state["index"]]
        step = next(item for item in workflow.steps if item.step_id == score.step_id)
        output = generate_redesign(step, score)
        return {"workflow": workflow.model_copy(update={"redesign_proposals": [*workflow.redesign_proposals, output]}), "index": state["index"] + 1}

    def skip(state: _GraphState):
        return {"index": state["index"] + 1}

    graph = StateGraph(_GraphState)
    graph.add_node("dispatch", dispatch)
    graph.add_node("automate", automate)
    graph.add_node("redesign", redesign)
    graph.add_node("skip", skip)
    graph.add_edge(START, "dispatch")
    graph.add_conditional_edges("dispatch", route, {"automate": "automate", "redesign": "redesign", "leave_as_is": "skip", "done": END})
    graph.add_edge("automate", "dispatch")
    graph.add_edge("redesign", "dispatch")
    graph.add_edge("skip", "dispatch")
    result = graph.compile().invoke({"workflow": workflow, "index": 0})
    return result["workflow"]
