from pydantic import BaseModel, Field

class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    context: str | None = None  # <--- ADDED

class AssistantResponse(BaseModel):
    answer: str
    route: str | None = None
    sources: list[dict] = []

class ReportRequest(BaseModel):
    patient_id: str = Field(min_length=1, max_length=64)

class HistoryEntry(BaseModel):
    id: int
    prediction: int
    probabilities: list[float]
    created_at: str