"""
Inference-time preprocessing: converts raw CSV fields to model-ready features.

Mirrors the logic in notebooks/02_Data_Cleaning_and_Feature_Engineering.ipynb
so that the FastAPI endpoint can serve predictions on new records.
"""

import pandas as pd

# ── Allowed values (derived from training data) ──────────────────────────────

ALLOWED_EXPERIENCE_LEVELS = {"EN", "MI", "SE", "EX"}
ALLOWED_EMPLOYMENT_TYPES = {"FT", "PT", "CT", "FL"}
ALLOWED_REMOTE_RATIOS = {0, 50, 100}
ALLOWED_COMPANY_SIZES = {"S", "M", "L"}

ALLOWED_EMPLOYEE_RESIDENCE = {
    "AE", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CN",
    "CO", "CZ", "DE", "DK", "DZ", "EE", "ES", "FR", "GB", "GR", "HK", "HN",
    "HR", "HU", "IE", "IN", "IQ", "IR", "IT", "JE", "JP", "KE", "LU", "MD",
    "MT", "MX", "MY", "NG", "NL", "NZ", "PH", "PK", "PL", "PR", "PT", "RO",
    "RS", "RU", "SG", "SI", "TN", "TR", "UA", "US", "VN",
}

ALLOWED_COMPANY_LOCATIONS = {
    "AE", "AS", "AT", "AU", "BE", "BR", "CA", "CH", "CL", "CN", "CO", "CZ",
    "DE", "DK", "DZ", "EE", "ES", "FR", "GB", "GR", "HN", "HR", "HU", "IE",
    "IL", "IN", "IQ", "IR", "IT", "JP", "KE", "LU", "MD", "MT", "MX", "MY",
    "NG", "NL", "NZ", "PK", "PL", "PT", "RO", "RU", "SG", "SI", "TR", "UA",
    "US", "VN",
}

REQUIRED_COLUMNS = [
    "work_year",
    "experience_level",
    "employment_type",
    "job_title",
    "employee_residence",
    "remote_ratio",
    "company_location",
    "company_size",
]

# ── Job title grouping (same logic as notebook 02) ────────────────────────────

def _group_job_title(title: str) -> str:
    t = str(title).lower()
    if "data scientist" in t:
        return "Data Scientist"
    if "data engineer" in t or "big data" in t or "etl" in t:
        return "Data Engineer"
    if (
        "data analyst" in t
        or "bi data" in t
        or "business data" in t
        or "analytics" in t
    ):
        return "Data Analyst"
    if any(x in t for x in ["machine learning", "ml engineer", "mle"]):
        return "ML Engineer"
    if any(x in t for x in ["director", "head", "principal", "lead"]):
        return "Lead/Director"
    return "Other"


_EXP_ORDER = {"EN": 0, "MI": 1, "SE": 2, "EX": 3}
_SIZE_ORDER = {"S": 0, "M": 1, "L": 2}

# ── Core transform ────────────────────────────────────────────────────────────

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform a DataFrame of raw records into model-ready features.

    Input columns: work_year, experience_level, employment_type, job_title,
                   employee_residence, remote_ratio, company_location, company_size

    Output columns (matching training features):
        employment_type, job_category, work_year, remote_ratio,
        experience_level_enc, company_size_enc, is_us_company, is_us_residence
    """
    out = pd.DataFrame()
    out["employment_type"] = df["employment_type"].astype(str)
    out["job_category"] = df["job_title"].apply(_group_job_title)
    out["work_year"] = df["work_year"].astype(int)
    out["remote_ratio"] = df["remote_ratio"].astype(int)
    out["experience_level_enc"] = df["experience_level"].map(_EXP_ORDER).astype(int)
    out["company_size_enc"] = df["company_size"].map(_SIZE_ORDER).astype(int)
    out["is_us_company"] = (df["company_location"] == "US").astype(int)
    out["is_us_residence"] = (df["employee_residence"] == "US").astype(int)
    return out
