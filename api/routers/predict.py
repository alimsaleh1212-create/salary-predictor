"""Prediction routes: POST /predict and POST /predict/batch."""

import pandas as pd
from fastapi import APIRouter, HTTPException

from api.models import BatchInput, BatchPrediction, SalaryInput, SalaryPrediction
from api.predictor import predict
from src.preprocessing import (
    ALLOWED_COMPANY_LOCATIONS,
    ALLOWED_EMPLOYEE_RESIDENCE,
    transform,
)

router = APIRouter(prefix="/predict", tags=["predictions"])


def _validate_locations(records: list[SalaryInput]) -> None:
    errors = []
    for i, r in enumerate(records):
        if r.employee_residence not in ALLOWED_EMPLOYEE_RESIDENCE:
            errors.append(
                f"Row {i}: employee_residence '{r.employee_residence}' is not in allowed list."
            )
        if r.company_location not in ALLOWED_COMPANY_LOCATIONS:
            errors.append(
                f"Row {i}: company_location '{r.company_location}' is not in allowed list."
            )
    if errors:
        raise HTTPException(status_code=422, detail=errors)


def _records_to_df(records: list[SalaryInput]) -> pd.DataFrame:
    return pd.DataFrame([r.model_dump() for r in records])


@router.post("", response_model=SalaryPrediction, summary="Predict salary for a single record")
def predict_single(body: SalaryInput):
    _validate_locations([body])
    features = transform(_records_to_df([body]))
    result = predict(features)
    return SalaryPrediction(predicted_salary_usd=result[0])


@router.post("/batch", response_model=BatchPrediction, summary="Predict salary for multiple records")
def predict_batch(body: BatchInput):
    _validate_locations(body.records)
    features = transform(_records_to_df(body.records))
    results = predict(features)
    return BatchPrediction(
        predictions=[SalaryPrediction(predicted_salary_usd=v) for v in results]
    )
