"""FastAPI application entry point.

Registers all routers — business logic lives in api/routers/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from api.routers import analyze, predict

app = FastAPI(
    title="Salary Prediction API",
    description="Predict data science salaries and generate LLM-powered insights.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(predict.router)
app.include_router(analyze.router)
