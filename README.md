# AI Finance Agent

An AI-powered financial analysis platform that combines autonomous LangChain agents with a modern full-stack architecture. Upload financial data and interact with an intelligent agent that can compute ratios, detect trends, identify anomalies, and answer complex financial questions.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Next.js Frontend                    │
│          (React, TypeScript, Recharts)               │
├─────────────────────────────────────────────────────┤
│                  REST API (FastAPI)                   │
├──────────┬──────────────────┬────────────────────────┤
│  Data    │   Financial      │   LangChain Agent      │
│ Pipeline │   Analysis       │  ┌──────────────────┐  │
│ (Pandas) │   Service        │  │ Tools:           │  │
│          │  - Ratios        │  │ - query_data     │  │
│          │  - Trends        │  │ - calc_ratios    │  │
│          │  - Anomalies     │  │ - trends         │  │
│          │  - Comparison    │  │ - anomalies      │  │
│          │                  │  │ - compare        │  │
│          │                  │  │ - summary        │  │
├──────────┴──────────────────┴──┴──────────────────┴──┤
│                SQLite Database                        │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer           | Technology                          |
|-----------------|-------------------------------------|
| Frontend        | Next.js 15, React 19, TypeScript    |
| UI / Charts     | Tailwind CSS, Recharts, Lucide      |
| Backend API     | Python, FastAPI, Pydantic           |
| AI Agent        | LangChain, OpenAI GPT-4o-mini      |
| Data Processing | Pandas, NumPy                       |
| Database        | SQLite + SQLAlchemy                 |

## Features

- **File Upload & Auto-Parsing** — Upload CSV/Excel financial statements; auto-detects wide and long formats
- **Financial Ratio Engine** — Computes profitability, liquidity, and leverage ratios automatically
- **Trend Analysis** — Period-over-period trend detection with directional classification
- **Anomaly Detection** — Statistical z-score-based anomaly identification with severity levels
- **Period Comparison** — Side-by-side comparison of any two periods
- **AI Agent Chat** — Natural language Q&A powered by a LangChain agent with 6 specialized tools
- **Interactive Dashboard** — Charts, ratio cards, and anomaly alerts built with Recharts

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
python main.py
```

The API will start at http://localhost:8000. Docs at http://localhost:8000/docs.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local

npm run dev
```

Open http://localhost:3000 in your browser.

### Try It Out

1. Click **Upload Data** and upload `data/sample_financials.csv`
2. Explore the **Dashboard** with auto-generated charts and ratios
3. Switch to **AI Agent Chat** and ask:
   - "What is the gross margin trend over the last 8 quarters?"
   - "Are there any anomalies in operating expenses?"
   - "Compare Q4 2023 vs Q3 2024 and recommend areas for improvement"

## API Endpoints

| Method | Endpoint                              | Description                     |
|--------|---------------------------------------|---------------------------------|
| POST   | `/api/upload`                         | Upload a financial data file    |
| GET    | `/api/datasets`                       | List all datasets               |
| GET    | `/api/datasets/{id}`                  | Get dataset details + preview   |
| GET    | `/api/datasets/{id}/analysis`         | Full financial analysis         |
| POST   | `/api/chat`                           | Chat with the AI agent          |
| GET    | `/api/datasets/{id}/chat-history`     | Get conversation history        |
| GET    | `/api/health`                         | Health check                    |

## Agent Tools

The LangChain agent has access to these specialized tools:

| Tool                       | Purpose                                              |
|----------------------------|------------------------------------------------------|
| `query_financial_data`     | Query and filter data by period, category, line item |
| `calculate_financial_ratios` | Compute profitability, liquidity, leverage ratios  |
| `analyze_trends`           | Period-over-period trend analysis                    |
| `detect_anomalies`         | Statistical anomaly detection                        |
| `compare_periods`          | Side-by-side period comparison                       |
| `get_data_summary`         | High-level dataset overview                          |

## Project Structure

```
ai-finance-agent/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # SQLAlchemy models + DB setup
│   ├── agent/
│   │   ├── finance_agent.py    # LangChain agent orchestration
│   │   └── tools.py            # Agent tool definitions
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   └── services/
│       ├── data_pipeline.py    # File parsing + data ingestion
│       └── financial_analysis.py # Ratio, trend, anomaly engines
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx        # Main page with sidebar + routing
│       │   └── layout.tsx      # Root layout
│       ├── components/
│       │   ├── ChatInterface.tsx    # AI chat with suggested prompts
│       │   ├── Dashboard.tsx        # Analysis dashboard
│       │   ├── FileUpload.tsx       # Drag-and-drop upload
│       │   └── FinancialCharts.tsx  # Recharts visualizations
│       ├── lib/api.ts          # API client
│       └── types/index.ts      # TypeScript interfaces
└── data/
    └── sample_financials.csv   # Sample dataset
```
