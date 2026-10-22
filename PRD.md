# AgriAI Product Requirements Document (PRD)

## 1. Product Summary
AgriAI is a farmer-focused decision support system for Indian agriculture. The system is intended to help farmers estimate crop yield, understand yield drivers, compare market prices to MSP reference values, assess potential net realization after transport and other costs, and receive simple, actionable selling recommendations.

The current repository is a strong prototype / MVP foundation, but it is not yet a complete production-ready product. The project has architecture, scaffolding, backend routes, database models, and some frontend screens in place, but several core product areas remain incomplete or unvalidated.

---

## 2. Executive Assessment

### Overall completion estimate
- Current state: approximately 50-60% complete as an implementation foundation
- Production readiness: roughly 10-20%
- Useful demo readiness: roughly 60-70%

### Why this estimate
The codebase includes:
- Well-structured backend and frontend architecture
- Core data models and API routes
- ML training/inference scaffolding
- Example screens and navigation
- A small automated test set

However, the project still lacks the deeper engineering required for a real user-facing product:
- real dataset ingestion and validation
- reliable model training and evaluation pipeline
- full end-to-end data flow
- realistic market recommendations
- complete frontend user journey
- deployment configuration
- security and production hardening

---

## 3. What Has Already Been Done

### 3.1 Architecture and project foundation
Completed / mostly complete:
- FastAPI backend initialized with app-level configuration
- CORS and structured error handling added
- SQLAlchemy database layer created
- Core models for users, farms, soil tests, crops, farm cycles, predictions, MSP, market prices, and recommendations
- Frontend React + Vite setup
- Routing and multiple screens added
- i18n structure for English/Hindi present
- README and implementation-plan documents created

Evidence:
- `backend/app.py`
- `backend/database.py`
- `backend/models.py`
- `frontend/src/index.jsx`
- `README.md`
- `IMPLEMENTATION_STEPS.md`

### 3.2 Backend API foundation
Completed / mostly complete:
- Health endpoint
- Farm creation and retrieval
- Soil test creation
- Yield prediction endpoint structure
- Market compare and market recommendation endpoint structure
- MSP reference lookup endpoint

Evidence:
- `backend/routers/health.py`
- `backend/routers/farms.py`
- `backend/routers/yield_pred.py`
- `backend/routers/markets.py`

### 3.3 ML foundation
Partial but present:
- Crop yield training scripts and feature engineering modules
- Market price training scripts and feature modules
- Baseline inference model support
- Model artifact files exist

Evidence:
- `ml/crop_yield/`
- `ml/market_price/`
- `models/yield_model.pkl`
- `models/yield_baseline_model.pkl`

### 3.4 Frontend UI foundation
Partial but present:
- Home screen
- Dashboard, MyFarm, Soil, Yield Prediction, Advisory, Market Advisor, Market Comparison, Price Forecast, History, Settings screens
- App-level layout and navigation

Evidence:
- `frontend/src/screens/`
- `frontend/src/components/Layout.jsx`

### 3.5 Initial testing and validation
Partial but present:
- Health endpoint test exists
- Market calculation logic tests exist
- SQLite-based test configuration is set up

Evidence:
- `tests/test_health.py`
- `tests/test_market_calc.py`
- `tests/conftest.py`

---

## 4. What Is Still Left to Do

## 4.1 Data engineering (largely not done)
This is a major remaining workstream. The project currently has a design, but not a real pipeline for usable agricultural data.

Required work:
- Create and populate `data/raw/`, `data/processed/`, `data/schemas/`, `data/provenance/`
- Build ingestion adapters for government data, market prices, MSP records, weather, and soil data
- Clean and normalize units (kg, quintal, tonne, hectare, acre)
- Validate missing values, duplicates, out-of-range values, stale dates, invalid units, and impossible combinations
- Retain provenance metadata: source, source record ID, retrieval timestamp, geographic metadata, crop, unit, validation status
- Version datasets and maintain reproducibility

Priority: Critical

### Status
- 0-10% complete

---

## 4.2 Yield ML (partially complete)
The project includes model training code and a model artifact, but there is no evidence of a complete, validated, end-to-end ML workflow.

Required work:
- Run proper EDA on crop production data
- Train and evaluate models by crop and region
- Check for feature leakage and invalid assumptions
- Validate model error metrics (MAE, RMSE, R2)
- Save model artifact and version metadata in the registry
- Expose reliable predictions from actual model outputs

Priority: High

### Status
- 25-35% complete

---

## 4.3 Market / price ML (partially complete)
Market prediction logic exists in modules, but real data-backed forecast validation is not yet complete.

Required work:
- Train/validate price model using real market time series
- Verify no future leakage in features
- Validate commodity/market forecast logic
- Add confidence scoring and thresholds
- Persist model versioning and dataset metadata

Priority: High

### Status
- 20-30% complete

---

## 4.4 Database and data integrity (partial)
The schema is a strong start, but several operational concerns remain.

Required work:
- Add database migrations (Alembic is present but not fully integrated in a clear workflow)
- Seed reference data for crops and MSP values
- Validate all relationships and constraints
- Ensure production-safe DB initialization and migration behavior
- Handle null and stale data cleanly

Priority: High

### Status
- 50-60% complete in schema design, lower in real operational robustness

---

## 4.5 API completeness and reliability (partial)
The API layer is present and organized, but needs deeper validation and hardening.

Required work:
- Implement consistent DTO validation across all routes
- Ensure all endpoints handle missing data gracefully
- Add pagination and filtering where needed
- Add centralized error taxonomy and logging
- Add input sanitization for all user-driven requests
- Add rate limiting and request guardrails if exposed publicly

Priority: High

### Status
- 60-70% complete structurally, lower in production robustness

---

## 4.6 Frontend completion (partial)
The frontend has screens and structure, but not a fully working complete user flow.

Required work:
- Finish missing field and crop/season data entry flows
- Connect real API calls to every screen
- Handle loading, empty state, and error states consistently
- Fix styling and translation inconsistencies
- Make mobile UX better for field/farmers
- Validate the entire flow: farmer -> farm -> soil -> yield -> market -> recommendation

Priority: High

### Status
- 50-60% complete in UI scaffolding, lower in real functionality

---

## 4.7 Integration testing (not complete)
The project has smoke tests, but not a real E2E or full product workflow validation.

Required work:
- Test farm creation + soil test + yield prediction flow
- Test market comparison and recommendation flows
- Test invalid inputs and edge cases
- Validate ML inference with realistic data
- Test the full frontend-to-backend-to-database passage

Priority: High

### Status
- 20-30% complete

---

## 4.8 Security and production hardening (not started)
This is a major blocker for any public deployment.

Required work:
- Review secrets management and environment configuration
- Define auth/authorization model if multi-user access is required
- Review SQL injection exposure patterns
- Review CORS and origin hardening
- Add rate limiting and abuse protection
- Review dependency vulnerabilities
- Ensure no sensitive data is exposed in logs or errors

Priority: Critical

### Status
- 0% complete

---

## 4.9 Deployment and operational readiness (not started)
The project is not yet deployable in a clean production environment.

Required work:
- Frontend deployment configuration
- Backend deployment configuration
- Managed database setup
- Environment variable documentation
- Health checks and monitoring
- Rollback strategy
- Release process and documentation

Priority: High

### Status
- 0% complete

---

## 5. Functional Requirements to Complete

### Core user flows
1. Farmer creates a farm profile
2. Farmer adds soil test data
3. Farmer adds crop and season details
4. System predicts yield
5. System explains primary factors affecting yield
6. System compares mandi price to MSP reference
7. System estimates net realization after costs
8. System recommends best selling markets
9. System shows forecast when enough data exists
10. System stores result history and explains uncertainty

### Business requirements
- Show price comparisons in simple, understandable language
- Display MSP reference as a reference point, not a guaranteed price
- Clearly indicate when estimates are based on limited data
- Avoid making misleading or guaranteed claims about profits or future price movement
- Use transparent scoring and explain factors in a farmer-friendly way

### Product quality requirements
- Mobile-first UI
- Offline-friendly fallback behavior is optional but useful
- Non-technical explanations where needed
- Confidence + disclaimer messaging on all predictive outputs

---

## 6. Non-Functional Requirements

### Reliability
- API should fail gracefully with clear structured errors
- Model absence should return actionable error messages
- Server must not expose stack traces in production

### Performance
- API responses for standard queries should be reasonable for a mobile-first product
- Model inference should be fast enough for a small user base
- Frontend should show loading/error states for all async operations

### Security
- No secrets in repo or logs
- Clearly defined environment configuration
- Input validation on all user-driven data
- Least-privilege DB access if scaling beyond local development

### Maintainability
- Clear service boundaries between routers, services, data models, and ML modules
- Versioned models and datasets
- Test coverage for core logic and integration flows

---

## 7. Proposed next delivery milestones

### Milestone 1 — Product foundation completion
- Finalize architecture and clean repo structure
- Confirm environment config and startup commands
- Validate local backend + frontend startup

### Milestone 2 — Data pipeline completion
- Build ingestion and validation pipeline
- Seed crop/MSP data
- Create processed datasets and provenance logs

### Milestone 3 — Model reliability
- Train and validate yield model
- Train and validate price forecast model
- Publish model registry and version metadata

### Milestone 4 — Full product workflow
- Complete farm -> soil -> yield -> market flow
- Connect all frontend screens to real APIs
- Verify end-to-end user journey

### Milestone 5 — Hardening and release readiness
- Security audit
- Performance review
- Deployment pipeline
- Documentation and production runbook

---

## 8. Definition of Done
The project is done when all of the following are true:
- real data pipeline is working and validated
- ML model training is automated and reproducible
- yield predictions are reliable and explained
- market comparison recommendations are transparent and trusted
- frontend is complete and functional on real data
- tests cover critical flows
- deployment and environment config are documented and secure
- the application can be run locally and in a hosted environment

---

## 9. Recommended immediate task order
1. Fix environment and startup validation
2. Create real data ingestion + validation pipeline
3. Seed reference data for crops and MSP
4. Train and verify yield model
5. Train and verify market price forecast model
6. Complete the core farm-to-market journey
7. Finish frontend API wiring and UX polish
8. Build integration tests
9. Run security review and harden deployment
10. Prepare production release package

---

## 10. Final product recommendation
This repository is best treated as an advanced MVP / prototype foundation rather than a finished product. It has a good conceptual base and enough implementation structure to proceed quickly, but it still requires serious engineering work in the areas of data quality, model validation, integration, and product hardening before it can be considered a reliable real-world agriculture solution.

The next step should be to complete the remaining product backlog in the order above and then validate the app against a real end-to-end farmer flow before any deployment decision is made.
