from pydantic import BaseModel
from datetime import datetime


class DatasetResponse(BaseModel):
    id: int
    name: str
    filename: str
    uploaded_at: datetime
    row_count: int
    columns: list[str]
    description: str | None = None


class ChatRequest(BaseModel):
    dataset_id: int
    message: str


class ChatResponse(BaseModel):
    response: str
    tools_used: list[str] = []


class AnalysisResponse(BaseModel):
    dataset_id: int
    dataset_name: str
    summary: dict
    ratios: dict
    trends: list[dict]
    anomalies: list[dict]
    period_comparison: dict


class UploadResponse(BaseModel):
    dataset_id: int
    name: str
    row_count: int
    columns: list[str]
    preview: list[dict]
