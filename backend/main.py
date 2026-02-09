"""AI Finance Agent — FastAPI Backend

A REST API that powers an AI-driven financial analysis platform.
Upload financial data and interact with an autonomous LangChain agent
that can compute ratios, analyze trends, detect anomalies, and more.
"""

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import json
import os
import shutil
import tempfile

from database import init_db, get_db, Dataset, ChatHistory
from models.schemas import (
    ChatRequest,
    ChatResponse,
    AnalysisResponse,
    DatasetResponse,
    UploadResponse,
)
from services.data_pipeline import ingest_file, get_dataset_dataframe
from services.financial_analysis import (
    compute_summary,
    compute_ratios,
    compute_trends,
    detect_anomalies,
    compare_periods,
)
from agent.finance_agent import run_agent

load_dotenv()

app = FastAPI(
    title="AI Finance Agent API",
    description="Upload financial data and chat with an AI agent for analysis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    os.makedirs("uploads", exist_ok=True)


# ── Dataset endpoints ──────────────────────────────────────────────


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a CSV or Excel file containing financial data."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        dataset_id, df = ingest_file(db, tmp_path, file.filename)
    finally:
        os.unlink(tmp_path)

    preview = df.head(5).to_dict(orient="records")

    return UploadResponse(
        dataset_id=dataset_id,
        name=file.filename.rsplit(".", 1)[0],
        row_count=len(df),
        columns=df.columns.tolist(),
        preview=preview,
    )


@app.get("/api/datasets")
def list_datasets(db: Session = Depends(get_db)):
    """List all uploaded datasets."""
    datasets = db.query(Dataset).order_by(Dataset.uploaded_at.desc()).all()
    return [
        DatasetResponse(
            id=ds.id,
            name=ds.name,
            filename=ds.filename,
            uploaded_at=ds.uploaded_at,
            row_count=ds.row_count,
            columns=json.loads(ds.columns),
            description=ds.description,
        )
        for ds in datasets
    ]


@app.get("/api/datasets/{dataset_id}")
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get dataset details and a data preview."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = get_dataset_dataframe(db, dataset_id)
    preview = df.head(10).to_dict(orient="records") if not df.empty else []

    return {
        "id": dataset.id,
        "name": dataset.name,
        "filename": dataset.filename,
        "uploaded_at": dataset.uploaded_at,
        "row_count": dataset.row_count,
        "columns": json.loads(dataset.columns),
        "preview": preview,
    }


# ── Analysis endpoints ─────────────────────────────────────────────


@app.get("/api/datasets/{dataset_id}/analysis", response_model=AnalysisResponse)
def get_analysis(dataset_id: int, db: Session = Depends(get_db)):
    """Run a full financial analysis on a dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = get_dataset_dataframe(db, dataset_id)
    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset has no records")

    return AnalysisResponse(
        dataset_id=dataset_id,
        dataset_name=dataset.name,
        summary=compute_summary(df),
        ratios=compute_ratios(df),
        trends=compute_trends(df)[:10],
        anomalies=detect_anomalies(df)[:10],
        period_comparison=compare_periods(df),
    )


# ── Chat endpoints ─────────────────────────────────────────────────


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Chat with the AI financial analysis agent."""
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Load chat history
    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.dataset_id == request.dataset_id)
        .order_by(ChatHistory.timestamp)
        .limit(20)
        .all()
    )
    chat_history = [{"role": h.role, "message": h.message} for h in history]

    # Save user message
    db.add(ChatHistory(dataset_id=request.dataset_id, role="user", message=request.message))
    db.commit()

    # Run agent
    result = await run_agent(db, request.dataset_id, request.message, chat_history)

    # Save assistant response
    db.add(ChatHistory(dataset_id=request.dataset_id, role="assistant", message=result["response"]))
    db.commit()

    return ChatResponse(response=result["response"], tools_used=result["tools_used"])


@app.get("/api/datasets/{dataset_id}/chat-history")
def get_chat_history(dataset_id: int, db: Session = Depends(get_db)):
    """Get chat history for a dataset."""
    messages = (
        db.query(ChatHistory)
        .filter(ChatHistory.dataset_id == dataset_id)
        .order_by(ChatHistory.timestamp)
        .all()
    )
    return [
        {"role": m.role, "message": m.message, "timestamp": m.timestamp}
        for m in messages
    ]


# ── Health ─────────────────────────────────────────────────────────


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ai-finance-agent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
