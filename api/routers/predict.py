from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from heartsense.predict import predict_single
from api.deps import log_prediction 

router = APIRouter(tags=["predict"])

class PatientIn(BaseModel):
    # Hardcore Pydantic validation
    Age: int = Field(ge=1, le=120, description="Age must be between 1 and 120")
    Sex: str = Field(pattern="^[MF]$", description="Sex must be M or F")
    ChestPainType: str = Field(pattern="^(ATA|NAP|ASY|TA)$")
    RestingBP: int = Field(ge=50, le=250, description="Resting BP must be between 50 and 250")
    Cholesterol: int = Field(ge=50, le=700, description="Cholesterol must be between 50 and 700")
    FastingBS: int = Field(ge=0, le=1, description="Fasting BS must be 0 or 1")
    RestingECG: str = Field(pattern="^(Normal|ST|LVH)$")
    MaxHR: int = Field(ge=40, le=250, description="Max HR must be between 40 and 250")
    ExerciseAngina: str = Field(pattern="^[YN]$", description="Exercise Angina must be Y or N")
    Oldpeak: float = Field(ge=-5.0, le=10.0, description="Oldpeak must be between -5.0 and 10.0")
    ST_Slope: str = Field(pattern="^(Up|Flat|Down)$")

@router.post("/predict")
def predict(payload: PatientIn):
    try:
        # model_dump() automatically converts the validated Pydantic object to a dict
        res = predict_single(payload.model_dump())
        
        # Save to SQLite database so Analytics and Dashboard update
        log_prediction(res["prediction"], res["probabilities"][0], res["probabilities"][1])
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))