"""
Local Ollama integration for generating salary insights + chart.

Returns a dict with:
  manager_insights  - str
  employee_insights - str
  chart_base64      - base64-encoded PNG string
"""

import base64
import io
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ollama


# Read at call time so .env changes are picked up without restarting the server
def _get_model() -> str:
    return os.environ.get("OLLAMA_MODEL", "gemma4:e2b")

_PROMPT_TEMPLATE = """You are a compensation data analyst. A salary prediction model returned the following result:

Job Title: {job_title}
Experience Level: {experience_level}
Employment Type: {employment_type}
Remote Ratio: {remote_ratio}%
Company Size: {company_size}
Company Location: {company_location}
Employee Residence: {employee_residence}
Work Year: {work_year}
Predicted Salary (USD): ${predicted_salary:,.0f}

Provide two short sections (3-4 bullet points each):

MANAGER INSIGHTS:
- Actionable recommendations to reduce or optimise salary costs for this role.

EMPLOYEE INSIGHTS:
- Actionable recommendations for the employee to increase their salary.

Be specific and practical. Do not repeat the input data verbatim."""


def _parse_insights(text: str) -> tuple[str, str]:
    """Split the LLM response into manager and employee sections."""
    manager = ""
    employee = ""

    m_match = re.search(
        r"MANAGER INSIGHTS[:\s]*(.*?)(?=EMPLOYEE INSIGHTS|$)", text, re.DOTALL | re.IGNORECASE
    )
    e_match = re.search(
        r"EMPLOYEE INSIGHTS[:\s]*(.*?)$", text, re.DOTALL | re.IGNORECASE
    )

    if m_match:
        manager = m_match.group(1).strip()
    if e_match:
        employee = e_match.group(1).strip()

    # Fallback: if parsing failed just split in half
    if not manager and not employee:
        lines = text.strip().splitlines()
        mid = len(lines) // 2
        manager = "\n".join(lines[:mid]).strip()
        employee = "\n".join(lines[mid:]).strip()

    return manager, employee


def _build_chart(record: dict, predicted_salary: float) -> str:
    """
    Generate a bar chart comparing key salary factors and return as base64 PNG.
    """
    exp_labels = {"EN": "Entry", "MI": "Mid", "SE": "Senior", "EX": "Executive"}
    size_labels = {"S": "Small", "M": "Medium", "L": "Large"}
    remote_labels = {0: "On-site", 50: "Hybrid", 100: "Remote"}

    categories = [
        exp_labels.get(record["experience_level"], record["experience_level"]),
        size_labels.get(record["company_size"], record["company_size"]),
        remote_labels.get(int(record["remote_ratio"]), str(record["remote_ratio"])),
    ]
    # Rough reference benchmarks per category for visual context
    benchmarks = {
        "Entry": 65_000,  "Mid": 95_000, "Senior": 140_000, "Executive": 180_000,
        "Small": 90_000,  "Medium": 120_000, "Large": 145_000,
        "On-site": 100_000, "Hybrid": 115_000, "Remote": 125_000,
    }
    bar_values = [benchmarks.get(c, 100_000) for c in categories]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(categories, bar_values, color=["#4C72B0", "#55A868", "#C44E52"], alpha=0.7)
    ax.axhline(predicted_salary, color="orange", linewidth=2, linestyle="--",
               label=f"Predicted: ${predicted_salary:,.0f}")
    ax.set_ylabel("Salary (USD)")
    ax.set_title(f"Salary Benchmarks vs Prediction\n{record['job_title']}")
    ax.legend()
    for bar, val in zip(bars, bar_values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 2000,
                f"${val:,.0f}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def generate_insights(record: dict, predicted_salary: float) -> dict:
    """
    Call local Ollama to generate insights and produce a chart.

    Args:
        record: raw input dict (same fields as SalaryInput)
        predicted_salary: float, predicted salary in USD

    Returns:
        {manager_insights, employee_insights, chart_base64}
    """
    prompt = _PROMPT_TEMPLATE.format(
        job_title=record.get("job_title", "N/A"),
        experience_level=record.get("experience_level", "N/A"),
        employment_type=record.get("employment_type", "N/A"),
        remote_ratio=record.get("remote_ratio", 0),
        company_size=record.get("company_size", "N/A"),
        company_location=record.get("company_location", "N/A"),
        employee_residence=record.get("employee_residence", "N/A"),
        work_year=record.get("work_year", "N/A"),
        predicted_salary=predicted_salary,
    )

    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    client = ollama.Client(host=base_url)
    response = client.chat(
        model=_get_model(),
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.message.content

    manager, employee = _parse_insights(text)
    chart_b64 = _build_chart(record, predicted_salary)

    return {
        "manager_insights": manager,
        "employee_insights": employee,
        "chart_base64": chart_b64,
    }
