from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from heartsense.predict import predict_single

router = APIRouter(tags=["predict"])

class PatientIn(BaseModel):
    Age: int = Field(ge=1, le=120)
    Sex: str = Field(pattern="^[MF]$")
    ChestPainType: str = Field(pattern="^(ATA|NAP|ASY|TA)$")
    RestingBP: int = Field(ge=50, le=250)
    Cholesterol: int = Field(ge=50, le=700)
    FastingBS: int = Field(ge=0, le=1)
    RestingECG: str = Field(pattern="^(Normal|ST|LVH)$")
    MaxHR: int = Field(ge=40, le=250)
    ExerciseAngina: str = Field(pattern="^[YN]$")
    Oldpeak: float = Field(ge=-5.0, le=10.0)
    ST_Slope: str = Field(pattern="^(Up|Flat|Down)$")

@router.post("/predict")
def predict(payload: PatientIn):
    try:
        return predict_single(payload.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))