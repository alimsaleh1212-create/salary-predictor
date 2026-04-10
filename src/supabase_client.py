"""Supabase read/write helpers."""

import os
from supabase import create_client, Client

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _client = create_client(url, key)
    return _client


def insert_prediction(record: dict) -> None:
    """Insert a single prediction + insights row into salary_predictions."""
    _get_client().table("salary_predictions").insert(record).execute()


def fetch_all_predictions() -> list[dict]:
    """Return all rows from salary_predictions ordered newest first."""
    resp = (
        _get_client()
        .table("salary_predictions")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []
