"""LangGraph supervisor over MCP tools with bounded execution."""
from typing import TypedDict, Annotated, List, Literal
from operator import add

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from heartsense.llm_client import get_llm
from heartsense.agents.mcp_client import get_mcp_tools

class AgentState(TypedDict):
    question: str
    route: Literal["predict", "rag", "analytics", "chat"]
    tool_input: dict
    tool_output: dict
    answer: str

SUPERVISOR_PROMPT = """You are a router. Given a user question, reply ONLY with one word:
- predict    → user asks about their own heart disease risk or a prediction
- rag        → user asks about medical knowledge, prevention, cholesterol, BP
- analytics  → user asks for stats or counts of past predictions
- chat       → anything else"""

def supervisor(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0.0)
    msg = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=state["question"]),
    ]
    route = llm.invoke(msg).content.strip().lower()
    if route not in {"predict", "rag", "analytics", "chat"}:
        route = "chat"
    return {**state, "route": route}

async def tool_runner(state: AgentState) -> AgentState:
    tools = await get_mcp_tools()
    tool_map = {t.name: t for t in tools}
    route_to_tool = {
        "predict": "predict_heart_disease",
        "rag": "search_medical_knowledge",
        "analytics": "get_prediction_analytics",
    }
    if state["route"] == "chat":
        llm = get_llm()
        answer = llm.invoke([HumanMessage(content=state["question"])]).content
        return {**state, "answer": answer}

    tool_name = route_to_tool[state["route"]]
    tool = tool_map.get(tool_name)
    if tool is None:
        return {**state, "answer": "Tool not available right now."}

    try:
        result = await tool.ainvoke(state.get("tool_input") or {"query": state["question"]})
    except Exception as e:
        return {**state, "answer": f"Tool failed: {e}"}

    return {**state, "tool_output": result if isinstance(result, dict) else {"result": result}}

def summarize(state: AgentState) -> AgentState:
    if state.get("answer"):
        return state
    llm = get_llm(temperature=0.2)
    prompt = f"""User question: {state['question']}
Tool output: {state['tool_output']}
Give a short, safe answer. Do not diagnose or prescribe."""
    answer = llm.invoke([HumanMessage(content=prompt)]).content
    return {**state, "answer": answer}

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("supervisor", supervisor)
    g.add_node("tool_runner", tool_runner)
    g.add_node("summarize", summarize)

    g.set_entry_point("supervisor")
    g.add_edge("supervisor", "tool_runner")
    g.add_edge("tool_runner", "summarize")
    g.add_edge("summarize", END)
    return g.compile()

_graph = None
def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph