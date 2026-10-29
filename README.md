# AgriAI — Decision Support for Indian Farmers

AgriAI is an agriculture decision-support application designed to help farmers:

- Estimate expected crop yield for a particular field
- Understand the major factors affecting expected yield  
- Receive practical, farmer-friendly crop recommendations
- Compare the Government of India's MSP reference with nearby/local mandi prices
- Estimate potential net realization after transportation/other costs
- Forecast market prices when enough historical data exists
- Identify potentially better markets for selling the harvested crop
- Present all results in simple language

## Architecture

```
React Frontend (mobile-first, en/hi)
        │
        ▼
   FastAPI REST API  (/api/v1)
        │
   ┌────┴────┬──────────┐
   │         │          │
   ▼         ▼          ▼
SQLite (dev) / PostgreSQL (production)     ML        Market/Data
           Inference  Adapters
              │
   ┌──────────┴──────────┐
   ▼                     ▼
Yield Model          Price Model
```

## Quick Start

1. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

2. **Train the ML models using synthetic data (recommended for first run)**
   ```bash
   python scripts/train_with_synthetic_data.py
   ```
   Options:
   ```bash
   python scripts/train_with_synthetic_data.py --yield-only        # Train only crop yield model
   python scripts/train_with_synthetic_data.py --price-only        # Train only market price model
   python scripts/train_with_synthetic_data.py --samples 5000      # More training samples
   python scripts/train_with_synthetic_data.py --price-days 1095   # 3 years of price history
   ```

   Or train using the original scripts (requires real data in the database):
   ```bash
   python -m ml.crop_yield.train_yield
   python -m ml.market_price.train_price
   ```

3. **Run the backend**
   ```bash
   python scripts/run_backend.sh
   ```

4. **Run the frontend**
   ```bash
   python scripts/run_frontend.sh
   ```

## Key Features

- **Yield Prediction**: Predict crop yield (tonnes/hectare) with confidence intervals and feature importance.
- **Market Comparison**: Compare mandi prices with MSP reference minus transport/other costs.
- **Recommendations**: Rank selling markets based on net price, freshness, quality.
- **Price Forecast**: Predict future market prices when sufficient historical data exists.
- **ML Model Training**: Start with regression baselines, evaluate with MAE/RMSE/R², track metrics.
- **Data Provenance**: Every external record retains source, retrieval timestamp, validation status.

## ML Models

### 🌾 Crop Yield Model (`models/yield_model.pkl`)

Predicts crop yield in tonnes/hectare for a given field and crop.

| Model | Train R² | Val R² | Val MAE | Val MAPE |
|---|---|---|---|---|
| Ridge | 0.969 | 0.963 | 1.479 t/ha | 40.7% |
| **RandomForest** ✅ | **0.995** | **0.979** | **0.978 t/ha** | **14.8%** |
| GradientBoosting | 0.999 | 0.976 | 1.029 t/ha | 14.3% |

**Training data:** 3,000 synthetic samples — 20 crops, 19 Indian states, all agro-climatic zones<br>
**Features:** Soil pH, NPK nutrients, rainfall, temperature, irrigation type, soil type, sowing month, year trend, NPK ratios, soil quality score<br>
**Split:** 80/20 chronological (time-aware, no future leakage)

### 💰 Market Price Model (`models/price_model.pkl`)

Forecasts market prices (₹/quintal) for the next 7 days per commodity-market pair.

| Coverage | Detail |
|---|---|
| **Commodities** | wheat, rice, maize, cotton, soybean, groundnut, mustard, onion, potato, tomato, chilli, chickpea, turmeric |
| **Markets** | 17 APMC markets across Punjab, UP, Maharashtra, Gujarat, Rajasthan, Andhra Pradesh, Telangana |
| **Forecast horizon** | 7 days |
| **Features** | Lag prices (1,3,7,14,30 days), rolling mean/std/min/max, arrivals, seasonal cyclical encoding |

**Per-series** model trained for each commodity-market combination.
**Split:** Chronological — last 7 days held out for evaluation.

> ⚠️ Both models are currently trained on **synthetic data**. Replace with real field observations (Agmarknet / data.gov.in) before production deployment.



- **Government crop data**: data.gov.in
- **MSP**: Department of Agriculture & Farmers Welfare
- **Mandi prices**: Agmarknet
- **Weather**: reliable weather API
- **Soil**: farmer tests + public data where permitted

## Project Structure

- `backend/` — FastAPI API, services, routers
- `ml/` — Model training, inference, validation
- `frontend/` — React UI with i18n
- `database/` — SQLAlchemy models, Alembic migrations
- `docs/` — Architecture, data sources, deployment
- `scripts/` — initialization, data ingestion, migration, **synthetic data training** (`train_with_synthetic_data.py`)
- `tests/` — API, models, market calculations

## Deploy to Vercel

The repository is configured as a Vercel Services project with a FastAPI API
and a Vite frontend on the same domain. See [Vercel deployment instructions](docs/DEPLOYMENT.md)
for the required PostgreSQL connection, migrations, and model-artifact setup.

## Safety & Honesty Rules

- Never fabricate real data, MSP values, or live prices.
- Never claim guaranteed yield, profit, or future prices.
- Never leak future data into ML training.
- Always present real data as "estimated" or "predicted".
- Display "MSP Reference" (not "Guaranteed Price").

## License

Built for demonstration and learning. Feel free to explore, extend, and share.

---

*Developed by Anthropic's Claude Code as a portfolio-quality ML project for Indian agriculture.*

## Development Workflow

**Stage 1** – Analysis (complete)
**Stage 2** – Foundation (current)
**Stage 3** – Data Engineering
**Stage 4** – Yield ML
**Stage 5** – Market ML
**Stage 6** – Database + API
**Stage 7** – Frontend
**Stage 8** – Full Integration
**Stage 9** – Testing + Security
**Stage 10** – Deployment
**Stage 11** – Final Audit

This repository contains Stage 2 foundation work. Continue with `proceed with Stage 3` to proceed.