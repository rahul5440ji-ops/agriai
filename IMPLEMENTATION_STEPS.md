# AgriAI — Implementation Steps for Remaining Work

## Current Status: ~50% Complete

Stages 1 (Analysis) and 2 (Foundation) are done. Stages 3-11 remain.

---

## STAGE 3 — DATA ENGINEERING (NOT STARTED)

### Task 3.1: Create data directory structure
```
data/
├── raw/           # Raw downloaded datasets
├── processed/     # Cleaned datasets
├── schemas/       # Dataset schemas
└── provenance/    # Provenance logs
```

### Task 3.2: Build data ingestion scripts
Create ingestion adapters for:
- data.gov.in (crop production data)
- Agmarknet (market prices)
- MSP notifications
- Weather API

### Task 3.3: Data validation
Build validation for:
- Missing values
- Duplicate records
- Impossible dates
- Impossible prices
- Invalid soil pH (0-14)
- Invalid nutrient ranges
- Negative production
- Inconsistent units
- Stale data

### Task 3.4: Unit normalization
Normalize: kg, quintal, tonne, hectare, acre

### Task 3.5: Provenance tracking
Every record must retain:
- source
- source record ID
- retrieval timestamp
- observation date
- geographic level
- unit
- crop
- validation status

### Task 3.6: Dataset versioning
Create versioned datasets in `data/processed/`

---

## STAGE 4 — YIELD ML (PARTIAL)

### Task 4.1: Run EDA
Analyze crop production data distributions, correlations, missing values.

### Task 4.2: Train the yield model
```bash
python -m ml.crop_yield.train_yield
```

### Task 4.3: Evaluate by crop and region
Add evaluation breakdowns by crop type and geographic region.

### Task 4.4: Feature importance
Extract and document top features affecting yield predictions.

### Task 4.5: Save model artifact
Verify `models/yield_model.pkl` is created.

---

## STAGE 5 — MARKET ML (PARTIAL)

### Task 5.1: Train the price model
```bash
python -m ml.market_price.train_price
```

### Task 5.2: Verify no future leakage
Run validation to ensure no future data in training features.

### Task 5.3: Test forecast service
Verify price forecasts work for commodity-market combinations.

### Task 5.4: Save model artifact
Verify `models/price_model.pkl` is created.

---

## STAGE 6 — DATABASE + API (PARTIAL)

### Task 6.1: Implement market comparison endpoint
```bash
GET /api/v1/markets/compare
```
Compare MSP reference with local mandi prices.

### Task 6.2: Implement market recommendation endpoint
```bash
POST /api/v1/markets/recommend
```
Rank markets by net price, distance, data freshness, quality.

### Task 6.3: Add recommendation scoring logic
Scoring based on:
- Estimated net price
- Distance
- Market data freshness
- Data quality
- Forecast confidence

---

## STAGE 7 — FRONTEND (PARTIAL)

### Task 7.1: Add missing screens
- "Add Field" screen
- "Crop & Season" screen

### Task 7.2: Fix remaining UI issues
- Navigation translations
- Layout styling
- Mobile responsiveness

### Task 7.3: Connect all screens to backend
- Wire up API calls
- Handle loading/error states
- Display real data from backend

### Task 7.4: Test complete user journey
Farmer → Farm → Soil → Yield → Market → Recommendation

---

## STAGE 8 — FULL INTEGRATION (NOT STARTED)

### Task 8.1: End-to-end test
Test: Frontend → FastAPI → Database → ML → Response → Frontend

### Task 8.2: Fix integration issues
Resolve any data flow or compatibility problems.

---

## STAGE 9 — TESTING + SECURITY (PARTIAL)

### Task 9.1: Add ML tests
- Preprocessing tests
- Feature transformation tests
- Inference tests
- Missing value handling
- Model loading tests
- No future leakage tests

### Task 9.2: Add market calculation tests
```python
net_price = market_price - transport_cost - other_costs
```

### Task 9.3: Add frontend tests
- Form validation
- API errors
- Empty states
- Loading states
- Stale data
- Mobile layout

### Task 9.4: Security audit
- Environment secrets
- Authentication
- Authorization
- SQL injection
- CORS
- Rate limiting
- PII
- Dependency vulnerabilities

---

## STAGE 10 — DEPLOYMENT (NOT STARTED)

### Task 10.1: Frontend deployment
- Build for production
- Deploy to hosting (Vercel/Netlify)

### Task 10.2: Backend deployment
- Deploy to Render
- Configure environment variables
- Set up health checks

### Task 10.3: Database deployment
- Set up managed PostgreSQL
- Configure migrations

### Task 10.4: Documentation
- Deployment instructions
- Database migration instructions
- Environment variables
- Build commands
- Start commands
- Rollback notes

---

## STAGE 11 — FINAL AUDIT (NOT STARTED)

### Task 11.1: Review all requirements
Check every item in CLAUDE.md sections 6-22.

### Task 11.2: Classify remaining issues
- CRITICAL
- HIGH
- MEDIUM
- LOW

### Task 11.3: Fix critical/high issues
Resolve any blocking problems before declaring production-ready.

---

## Quick Reference: Commands to Run

```bash
# Start backend
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

# Start frontend
python -m uvicorn backend.app

# Initialize database
python scripts/init_db.py

# Run migrations
alembic upgrade head

# Train yield model
python -m ml.crop_yield.train_yield

# Train price model
python -m ml.market_price.train_price

# Run tests
python -m pytest tests/ -v
```