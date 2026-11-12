from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from heartsense.predict import predict_single
from api.deps import log_prediction  # Add this line

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
        res = predict_single(payload.model_dump())
        # Save to SQLite database so Analytics and Dashboard update
        log_prediction(res["prediction"], res["probabilities"][0], res["probabilities"][1])
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))