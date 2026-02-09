# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (Python/FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Add OPENAI_API_KEY
python main.py                    # Starts at http://localhost:8000, docs at /docs
```

### Frontend (Next.js)
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev                       # Starts at http://localhost:3000
npm run build                     # Production build
npm run lint
```

## Architecture

Full-stack AI financial analysis platform: **Next.js frontend → FastAPI REST API → LangChain agent → SQLite**.

### Backend (`backend/`)

- **`main.py`** — FastAPI app with 7 REST endpoints (upload, datasets CRUD, analysis, chat, health). CORS allows `localhost:3000`.
- **`database.py`** — SQLAlchemy ORM with three tables: `datasets` (file metadata), `financial_records` (normalized line items by period), `chat_history` (per-dataset conversations).
- **`services/data_pipeline.py`** — Parses uploaded CSV/Excel files. Auto-detects **wide format** (line items as rows, periods as columns) vs **long format** (period/category/line_item/amount columns). Normalizes into `financial_records`.
- **`services/financial_analysis.py`** — Four analysis engines: ratio computation (profitability/liquidity/leverage), trend analysis (period-over-period with direction classification), z-score anomaly detection (±1.5 std dev threshold), and period comparison. Uses `_build_item_map()` to fuzzy-match financial line item names.
- **`agent/finance_agent.py`** — Creates a LangChain `AgentExecutor` with `create_tool_calling_agent`. Uses ChatOpenAI (gpt-4o-mini, temp=0). System prompt enforces data-driven responses. Max 8 iterations. Maintains chat history as LangChain message objects.
- **`agent/tools.py`** — Six `@tool`-decorated functions bound to a specific dataset via closure: `query_financial_data`, `calculate_financial_ratios`, `analyze_trends`, `detect_anomalies`, `compare_periods`, `get_data_summary`. Tools are created fresh per request with `create_tools(db, dataset_id)`.

### Frontend (`frontend/src/`)

- **`app/page.tsx`** — Main page managing sidebar (dataset list), tab switching (dashboard/chat), and upload modal state. All client-side state via React hooks.
- **`components/Dashboard.tsx`** — Fetches `/api/datasets/{id}/analysis` and renders stat cards + FinancialCharts.
- **`components/ChatInterface.tsx`** — Chat UI with suggested prompts, shows which agent tools were used per response.
- **`components/FinancialCharts.tsx`** — Recharts bar/line charts for period totals, trends, period comparison; ratio cards; anomaly alert cards.
- **`components/FileUpload.tsx`** — Drag-and-drop with format validation (csv/xlsx/xls).
- **`lib/api.ts`** — Generic `fetchApi<T>()` wrapper; `uploadFile()` uses FormData.
- **`types/index.ts`** — TypeScript interfaces matching backend Pydantic schemas.

### Data Flow

Upload file → `data_pipeline` parses & normalizes → stored in SQLite → Dashboard calls analysis service for ratios/trends/anomalies → Chat sends user message to LangChain agent which autonomously selects tools → agent returns response with tool citations.

## Environment Variables

Backend `.env`: `OPENAI_API_KEY` (required), `OPENAI_MODEL` (default: gpt-4o-mini), `DATABASE_URL` (default: sqlite:///./finance_data.db)

Frontend `.env.local`: `NEXT_PUBLIC_API_URL` (default: http://localhost:8000)

## Sample Data

`data/sample_financials.csv` contains 8 quarters of income statement, balance sheet, and cash flow data in wide format for testing.
