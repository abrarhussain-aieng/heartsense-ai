from fastapi import APIRouter, HTTPException
from api.schemas import AssistantRequest, AssistantResponse
from heartsense.agents.graph import get_graph
from heartsense.guardrails.rails import check_input

router = APIRouter(tags=["assistant"])

@router.post("/assistant", response_model=AssistantResponse)
async def assistant(req: AssistantRequest):
    gate = await check_input(req.question)
    if not gate["allowed"]:
        return AssistantResponse(answer=gate["message"], route="guardrail")

    try:
        graph = get_graph()
        result = await graph.ainvoke({"question": req.question})
        return AssistantResponse(
            answer=result.get("answer", ""),
            route=result.get("route"),
            sources=[],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))