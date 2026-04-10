"""Analysis route: POST /analyze — calls local Ollama for insights + chart."""

from fastapi import APIRouter, HTTPException

from api.models import AnalyzeInput, AnalyzeResponse
from src.ollama_client import generate_insights

router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("", response_model=AnalyzeResponse, summary="Generate LLM insights and chart for a prediction")
def analyze(body: AnalyzeInput):
    record = body.model_dump(exclude={"predicted_salary_usd"})
    try:
        result = generate_insights(record, body.predicted_salary_usd)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama unavailable: {e}")
    return AnalyzeResponse(**result)
