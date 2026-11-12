from typing import TypedDict, Literal
from heartsense.agents.mcp_client import get_mcp_session
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from heartsense.llm_client import get_llm
import os
from heartsense.config import settings

# Explicitly set environment variables for LangSmith
if settings.langsmith_tracing and settings.langsmith_api_key:
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    # If you are in the EU/APAC region, also set:
    # os.environ["LANGSMITH_ENDPOINT"] = "https://eu.api.smith.langchain.com"

class AgentState(TypedDict):
    question: str
    route: Literal["predict", "rag", "analytics", "chat"]
    tool_input: dict
    tool_output: dict
    answer: str

# UPDATED: Explicitly telling the router to send model accuracy/MLflow to analytics
SUPERVISOR_PROMPT = """You are a router. Given a user question, reply ONLY with one word:
- predict    → user asks about their own heart disease risk or a prediction
- rag        → user asks about medical knowledge, prevention, cholesterol, BP
- analytics  → user asks for stats, counts of past predictions, model accuracy, MLflow metrics, or system performance
- chat       → anything else (greetings, general questions)"""

def supervisor(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0.0)
    msg = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=state["question"]),
    ]
    response = llm.invoke(msg).content
    
    # Handle if the LLM returns a list of blocks (newer LangChain behavior)
    if isinstance(response, list):
        response = response[0].get("text", "")
        
    route = str(response).strip().lower()
    if route not in {"predict", "rag", "analytics", "chat"}:
        route = "chat"
    return {**state, "route": route}

# Tool Runner Function
async def tool_runner(state: AgentState) -> AgentState:
    if state["route"] == "chat":
        llm = get_llm(temperature=0.0)
        # UPDATED: If it routes to chat but asks about MLflow, politely decline and point to the UI
        system_prompt = "You are HeartSense AI, a specialized cardiovascular health assistant. Never claim to be ChatGPT or an OpenAI model. Keep answers brief and focused on heart health. If asked about model accuracy or MLflow, state that you don't have direct access to that in this chat, but advise the user to check the 'Model Monitoring' tab in the dashboard."
        res = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["question"])
        ]).content
        if isinstance(res, list): res = res[0].get("text", "")
        return {**state, "answer": str(res)}

    try:
        async with get_mcp_session() as tools:
            tool_map = {t.name: t for t in tools}
            route_to_tool = {
                "predict": "predict_heart_disease",
                "rag": "search_medical_knowledge",
                "analytics": "get_prediction_analytics",
            }
            tool_name = route_to_tool[state["route"]]
            tool = tool_map.get(tool_name)
            
            if tool is None:
                return {**state, "answer": f"The tool '{tool_name}' is not available right now."}

            result = await tool.ainvoke(state.get("tool_input") or {"query": state["question"]})
            
            # Store as string so the LLM can read it easily
            return {**state, "tool_output": str(result)}
            
    except Exception as e:
        return {**state, "answer": f"Could not connect to the MCP server. Error: {e}"}

def summarize(state: AgentState) -> AgentState:
    if state.get("answer"):
        return state
    # UPDATED: Temperature 0.0 to prevent hallucination during summarization
    llm = get_llm(temperature=0.0) 
    prompt = f"""User question: {state['question']}
Tool output: {state['tool_output']}
Give a short, accurate answer based ONLY on the tool output above. 
Do not invent information. Do not diagnose or prescribe."""
    
    response = llm.invoke([HumanMessage(content=prompt)]).content
    if isinstance(response, list): response = response[0].get("text", "")
    return {**state, "answer": str(response)}

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