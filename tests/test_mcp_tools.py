import pytest
from mcp_server.server import predict_heart_disease, PredictInput

def test_predict_tool_schema():
    payload = PredictInput(
        Age=50, Sex="M", ChestPainType="ATA", RestingBP=120,
        Cholesterol=200, FastingBS=0, RestingECG="Normal",
        MaxHR=150, ExerciseAngina="N", Oldpeak=1.0, ST_Slope="Up",
    )
    # Only schema validation here; actual model load requires the artifact.
    assert payload.Age == 50

def test_predict_tool_requires_artifact():
    with pytest.raises(Exception):
        predict_heart_disease(PredictInput(
            Age=50, Sex="M", ChestPainType="ATA", RestingBP=120,
            Cholesterol=200, FastingBS=0, RestingECG="Normal",
            MaxHR=150, ExerciseAngina="N", Oldpeak=1.0, ST_Slope="Up",
        ))