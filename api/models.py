"""Pydantic schemas for /predict and /analyze endpoints."""

from typing import Annotated, Literal
from pydantic import BaseModel, Field, field_validator


ExperienceLevel = Literal["EN", "MI", "SE", "EX"]
EmploymentType = Literal["FT", "PT", "CT", "FL"]
CompanySize = Literal["S", "M", "L"]
RemoteRatio = Literal[0, 50, 100]


class SalaryInput(BaseModel):
    work_year: Annotated[int, Field(ge=2020, le=2030)]
    experience_level: ExperienceLevel
    employment_type: EmploymentType
    job_title: str = Field(min_length=1, max_length=200)
    employee_residence: str = Field(min_length=2, max_length=2)
    remote_ratio: RemoteRatio
    company_location: str = Field(min_length=2, max_length=2)
    company_size: CompanySize

    @field_validator("employee_residence", "company_location")
    @classmethod
    def must_be_uppercase(cls, v: str) -> str:
        return v.upper()


class SalaryPrediction(BaseModel):
    predicted_salary_usd: float


class BatchInput(BaseModel):
    records: list[SalaryInput] = Field(min_length=1)


class BatchPrediction(BaseModel):
    predictions: list[SalaryPrediction]


# ── Analyze schemas ───────────────────────────────────────────────────────────

class AnalyzeInput(BaseModel):
    """Input record + predicted salary → LLM insights + chart."""
    work_year: Annotated[int, Field(ge=2020, le=2030)]
    experience_level: ExperienceLevel
    employment_type: EmploymentType
    job_title: str = Field(min_length=1, max_length=200)
    employee_residence: str = Field(min_length=2, max_length=2)
    remote_ratio: RemoteRatio
    company_location: str = Field(min_length=2, max_length=2)
    company_size: CompanySize
    predicted_salary_usd: float = Field(gt=0)

    @field_validator("employee_residence", "company_location")
    @classmethod
    def must_be_uppercase(cls, v: str) -> str:
        return v.upper()


class AnalyzeResponse(BaseModel):
    manager_insights: str
    employee_insights: str
    chart_base64: str
