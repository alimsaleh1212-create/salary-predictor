"""
Deployed Streamlit Dashboard — reads exclusively from Supabase.

Displays historical predictions, LLM insights, charts, and model metrics.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import base64
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from src.supabase_client import fetch_all_predictions

load_dotenv()

# ── Model metrics (fixed from training) ──────────────────────────────────────
MODEL_METRICS = {
    "Test MAE": "$27,687",
    "Test RMSE": "$39,819",
    "Test R²": "0.5863",
    "Algorithm": "Random Forest Regressor",
    "Train/Test Split": "80 / 20",
    "Cross-Validation": "5-fold",
}

st.set_page_config(
    page_title="Salary Prediction Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Data Science Salary Prediction Dashboard")
st.markdown("Historical predictions, AI insights, and model performance — powered by Supabase.")

# ── Model Metrics ─────────────────────────────────────────────────────────────
st.subheader("🤖 Model Performance")
metric_cols = st.columns(len(MODEL_METRICS))
for col, (label, value) in zip(metric_cols, MODEL_METRICS.items()):
    col.metric(label, value)

st.divider()

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading predictions from Supabase…"):
    try:
        rows = fetch_all_predictions()
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        st.stop()

if not rows:
    st.info("No predictions yet. Upload a CSV using the local UI to populate this dashboard.")
    st.stop()

df = pd.DataFrame(rows)

# ── Summary stats ─────────────────────────────────────────────────────────────
st.subheader("📈 Summary")
s_cols = st.columns(4)
s_cols[0].metric("Total Predictions", len(df))
s_cols[1].metric("Avg Predicted Salary",
                  f"${df['predicted_salary_usd'].mean():,.0f}")
s_cols[2].metric("Highest Prediction",
                  f"${df['predicted_salary_usd'].max():,.0f}")
s_cols[3].metric("Lowest Prediction",
                  f"${df['predicted_salary_usd'].min():,.0f}")

st.divider()

# ── Comparative Visualizations ────────────────────────────────────────────────
st.subheader("📊 Salary Distributions")

vis_cols = st.columns(2)

with vis_cols[0]:
    # Salary distribution histogram
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(df["predicted_salary_usd"], bins=20, color="#4C72B0", edgecolor="white")
    ax.set_xlabel("Predicted Salary (USD)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Predicted Salaries")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with vis_cols[1]:
    # Avg salary by experience level
    if "experience_level" in df.columns:
        exp_order = ["EN", "MI", "SE", "EX"]
        exp_labels = {"EN": "Entry", "MI": "Mid", "SE": "Senior", "EX": "Executive"}
        exp_df = (
            df.groupby("experience_level")["predicted_salary_usd"]
            .mean()
            .reindex([e for e in exp_order if e in df["experience_level"].values])
        )
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        bars = ax2.bar(
            [exp_labels.get(e, e) for e in exp_df.index],
            exp_df.values,
            color=["#55A868", "#4C72B0", "#C44E52", "#8172B2"],
        )
        ax2.set_ylabel("Avg Predicted Salary (USD)")
        ax2.set_title("Avg Salary by Experience Level")
        for bar in bars:
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1000,
                f"${bar.get_height():,.0f}",
                ha="center", va="bottom", fontsize=8,
            )
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

st.divider()

# ── Predictions table ─────────────────────────────────────────────────────────
st.subheader("📋 All Predictions")

display_cols = [
    "created_at", "job_title", "experience_level", "employment_type",
    "company_location", "remote_ratio", "company_size", "predicted_salary_usd",
]
available_cols = [c for c in display_cols if c in df.columns]
st.dataframe(
    df[available_cols].rename(columns={"predicted_salary_usd": "predicted_salary_usd ($)"}),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ── Individual record insights ────────────────────────────────────────────────
st.subheader("🔍 Individual Record Insights")

# Pick a record to inspect
record_labels = [
    f"{i+1}. {row.get('job_title','?')} — {row.get('experience_level','?')} — ${row.get('predicted_salary_usd',0):,.0f}"
    for i, row in enumerate(rows)
]
selected_idx = st.selectbox("Select a prediction to inspect:", range(len(rows)),
                             format_func=lambda i: record_labels[i])

selected = rows[selected_idx]
left, right = st.columns([1, 1])

with left:
    st.markdown(f"### {selected.get('job_title', 'N/A')}")
    details = {
        "Experience": selected.get("experience_level"),
        "Employment": selected.get("employment_type"),
        "Remote": f"{selected.get('remote_ratio')}%",
        "Company Size": selected.get("company_size"),
        "Company Location": selected.get("company_location"),
        "Employee Residence": selected.get("employee_residence"),
        "Work Year": selected.get("work_year"),
    }
    for k, v in details.items():
        st.markdown(f"**{k}:** {v}")
    st.metric("Predicted Salary", f"${selected.get('predicted_salary_usd', 0):,.0f}")

    if selected.get("manager_insights"):
        st.markdown("#### 👔 Manager Insights")
        st.markdown(selected["manager_insights"])

    if selected.get("employee_insights"):
        st.markdown("#### 🙋 Employee Insights")
        st.markdown(selected["employee_insights"])

with right:
    chart_b64 = selected.get("chart_base64")
    if chart_b64:
        try:
            img = Image.open(BytesIO(base64.b64decode(chart_b64)))
            st.image(img, use_container_width=True)
        except Exception:
            st.info("Chart unavailable for this record.")
    else:
        st.info("No chart stored for this record.")
