# AgriAI Architecture

## Overview

AgriAI is a decision-support application for Indian farmers. It combines real
machine-learning pipelines (crop yield prediction and market price
forecasting), a Government MSP reference comparison, and a mobile-first UI.

```
React Frontend (mobile-first, en/hi)
        │
        ▼
   FastAPI REST API  (/api/v1)
        │
   ┌────┴────┬──────────┐
   │         │          │
   ▼         ▼          ▼
SQLite     ML        Market/Data
           Inference  Adapters
              │
   ┌──────────┴──────────┐
   ▼                     ▼
Yield Model          Price Model
```

## Layers

### 1. Data plane (`data/`, `scripts/`)
- Ingestion adapters for data.gov.in, Agmarknet, MSP notifications, weather.
- Every record retains provenance: source, source record ID, retrieval
  timestamp, observation date, geographic level, unit, crop, validation
  status.
- Synthetic data is permitted only for dev/test and must be clearly labelled.

### 2. ML plane (`ml/`)
- `ml/yield/` — Model A (crop yield, regression).
- `ml/price/` — Model B (market price, forecasting).
- Training code lives ONLY in `ml/`. It never runs inside FastAPI request
  handlers. Inference artifacts are loaded once at startup via
  `backend/ml/inference.py`.

### 3. Backend plane (`backend/`)
- FastAPI app with Pydantic schemas, SQLAlchemy models, Alembic migrations.
- Routers: health, farms, yield, markets, price.
- Services orchestrate validation → ML inference → advisory rules.

### 4. Frontend plane (`frontend/`)
- React + Vite + Tailwind + Recharts, mobile-first.
- i18n via `src/i18n/` (en, hi), extensible for more languages.
- No hardcoded predictions, prices, or MSP values.

## Key rules
- Never fabricate data, MSP, prices, or ML metrics.
- Never claim guaranteed yield, profit, or future prices.
- Never leak future data into ML training.
- Never mix training and inference.
- Never expose secrets, filesystem paths, or stack traces.