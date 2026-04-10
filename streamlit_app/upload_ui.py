"""
Local Streamlit UI — CSV Upload & Batch Prediction Pipeline.

Flow:
  Upload CSV → Validate → POST /predict (FastAPI) → POST /analyze (FastAPI → Ollama) → Store in Supabase
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import base64
import os
import uuid
from io import BytesIO

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from src.preprocessing import (
    ALLOWED_COMPANY_LOCATIONS,
    ALLOWED_COMPANY_SIZES,
    ALLOWED_EMPLOYEE_RESIDENCE,
    ALLOWED_EMPLOYMENT_TYPES,
    ALLOWED_EXPERIENCE_LEVELS,
    ALLOWED_REMOTE_RATIOS,
    REQUIRED_COLUMNS,
)
from src.supabase_client import insert_prediction

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
MIN_RECORDS = 1

st.set_page_config(
    page_title="Salary Predictor — Upload & Analyze",
    page_icon="💼",
    layout="wide",
)


# ── Validation ────────────────────────────────────────────────────────────────

def validate_csv(df: pd.DataFrame) -> list[str]:
    """
    Strict validation. Returns a list of error strings (empty = valid).
    Any error means the entire batch is rejected.
    """
    errors: list[str] = []

    # 1. Required columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
        return errors  # can't continue without columns

    # 2. Minimum rows
    if len(df) < MIN_RECORDS:
        errors.append(f"CSV must contain at least {MIN_RECORDS} records. Found {len(df)}.")

    # 3. No NaN / empty cells in required columns
    nan_counts = df[REQUIRED_COLUMNS].isnull().sum()
    nan_cols = nan_counts[nan_counts > 0]
    if not nan_cols.empty:
        errors.append(
            f"Missing values found in columns: {nan_cols.to_dict()}. "
            "All rows must be complete."
        )

    if errors:
        return errors  # skip value checks if NaN present

    # 4. Categorical value checks
    bad_exp = df[~df["experience_level"].isin(ALLOWED_EXPERIENCE_LEVELS)]
    if not bad_exp.empty:
        errors.append(
            f"Invalid experience_level values in rows {bad_exp.index.tolist()}: "
            f"{bad_exp['experience_level'].unique().tolist()}. "
            f"Allowed: {sorted(ALLOWED_EXPERIENCE_LEVELS)}"
        )

    bad_emp = df[~df["employment_type"].isin(ALLOWED_EMPLOYMENT_TYPES)]
    if not bad_emp.empty:
        errors.append(
            f"Invalid employment_type values in rows {bad_emp.index.tolist()}: "
            f"{bad_emp['employment_type'].unique().tolist()}. "
            f"Allowed: {sorted(ALLOWED_EMPLOYMENT_TYPES)}"
        )

    bad_remote = df[~df["remote_ratio"].isin(ALLOWED_REMOTE_RATIOS)]
    if not bad_remote.empty:
        errors.append(
            f"Invalid remote_ratio values in rows {bad_remote.index.tolist()}: "
            f"{bad_remote['remote_ratio'].unique().tolist()}. "
            f"Allowed: {sorted(ALLOWED_REMOTE_RATIOS)}"
        )

    bad_size = df[~df["company_size"].isin(ALLOWED_COMPANY_SIZES)]
    if not bad_size.empty:
        errors.append(
            f"Invalid company_size values in rows {bad_size.index.tolist()}: "
            f"{bad_size['company_size'].unique().tolist()}. "
            f"Allowed: {sorted(ALLOWED_COMPANY_SIZES)}"
        )

    bad_res = df[~df["employee_residence"].isin(ALLOWED_EMPLOYEE_RESIDENCE)]
    if not bad_res.empty:
        errors.append(
            f"Invalid employee_residence codes in rows {bad_res.index.tolist()}: "
            f"{bad_res['employee_residence'].unique().tolist()}."
        )

    bad_loc = df[~df["company_location"].isin(ALLOWED_COMPANY_LOCATIONS)]
    if not bad_loc.empty:
        errors.append(
            f"Invalid company_location codes in rows {bad_loc.index.tolist()}: "
            f"{bad_loc['company_location'].unique().tolist()}."
        )

    return errors


# ── API helpers ───────────────────────────────────────────────────────────────

def _base_payload(record: dict) -> dict:
    return {
        "work_year": int(record["work_year"]),
        "experience_level": record["experience_level"],
        "employment_type": record["employment_type"],
        "job_title": record["job_title"],
        "employee_residence": record["employee_residence"],
        "remote_ratio": int(record["remote_ratio"]),
        "company_location": record["company_location"],
        "company_size": record["company_size"],
    }


def call_predict_api(record: dict) -> float:
    resp = requests.post(f"{API_BASE_URL}/predict", json=_base_payload(record), timeout=30)
    resp.raise_for_status()
    return resp.json()["predicted_salary_usd"]


def call_analyze_api(record: dict, predicted_salary: float) -> dict:
    payload = {**_base_payload(record), "predicted_salary_usd": predicted_salary}
    resp = requests.post(f"{API_BASE_URL}/analyze", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()  # {manager_insights, employee_insights, chart_base64}


# ── UI ────────────────────────────────────────────────────────────────────────

st.title("💼 Data Science Salary Predictor")
st.markdown(
    "Upload a CSV of data science roles to predict salaries, generate AI insights, "
    "and store results to the dashboard."
)

with st.expander("📋 CSV Format Requirements", expanded=False):
    st.markdown(
        f"""
**Required columns** (exact names, case-sensitive):
`{", ".join(REQUIRED_COLUMNS)}`

**Validation rules:**
- At least **1 record** required
- No missing/empty values in any required column
- `experience_level`: `EN`, `MI`, `SE`, `EX`
- `employment_type`: `FT`, `PT`, `CT`, `FL`
- `remote_ratio`: `0`, `50`, `100`
- `company_size`: `S`, `M`, `L`
- `employee_residence` / `company_location`: 2-letter ISO country codes

**Download the demo file** from `demo_samples/new_records.csv` to get started.
"""
    )

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        st.stop()

    st.write(f"**Rows detected:** {len(df)}")
    st.dataframe(df.head(5), use_container_width=True)

    errors = validate_csv(df)
    if errors:
        st.error("**CSV validation failed. Fix the following errors before proceeding:**")
        for err in errors:
            st.markdown(f"- {err}")
        st.stop()

    st.success(f"✅ Validation passed — {len(df)} records ready.")

    if st.button("🚀 Predict & Analyze", type="primary"):
        batch_id = str(uuid.uuid4())
        success_count = 0
        fail_count = 0
        results = []

        progress = st.progress(0, text="Processing records…")
        status_box = st.empty()

        for i, row in df.iterrows():
            pct = int((i + 1) / len(df) * 100)  # type: ignore[operator]
            progress.progress(pct, text=f"Record {i + 1}/{len(df)}")  # type: ignore[operator]
            record = row.to_dict()

            try:
                # Step 1: Predict
                predicted_salary = call_predict_api(record)

                # Step 2: LLM insights + chart (via FastAPI → Ollama)
                insights = call_analyze_api(record, predicted_salary)

                # Step 3: Store in Supabase
                db_row = {
                    "batch_id": batch_id,
                    "work_year": int(record["work_year"]),
                    "experience_level": str(record["experience_level"]),
                    "employment_type": str(record["employment_type"]),
                    "job_title": str(record["job_title"]),
                    "employee_residence": str(record["employee_residence"]),
                    "remote_ratio": int(record["remote_ratio"]),
                    "company_location": str(record["company_location"]),
                    "company_size": str(record["company_size"]),
                    "predicted_salary_usd": predicted_salary,
                    "manager_insights": insights["manager_insights"],
                    "employee_insights": insights["employee_insights"],
                    "chart_base64": insights["chart_base64"],
                }
                insert_prediction(db_row)
                results.append({"record": record, "predicted_salary": predicted_salary,
                                 "insights": insights})
                success_count += 1

            except Exception as e:
                fail_count += 1
                status_box.warning(f"Row {i}: failed — {e}")

        progress.empty()

        st.success(f"✅ Done! {success_count} succeeded, {fail_count} failed.")

        if results:
            st.subheader("Sample Results (first 3 records)")
            for r in results[:3]:
                with st.container():
                    cols = st.columns([1, 1])
                    with cols[0]:
                        st.markdown(f"**{r['record']['job_title']}** — "
                                    f"{r['record']['experience_level']} | "
                                    f"{r['record']['company_location']}")
                        st.metric("Predicted Salary", f"${r['predicted_salary']:,.0f}")
                        st.markdown("**Manager Insights**")
                        st.markdown(r["insights"]["manager_insights"])
                        st.markdown("**Employee Insights**")
                        st.markdown(r["insights"]["employee_insights"])
                    with cols[1]:
                        if r["insights"]["chart_base64"]:
                            img = Image.open(
                                BytesIO(base64.b64decode(r["insights"]["chart_base64"]))
                            )
                            st.image(img, use_container_width=True)
                    st.divider()
