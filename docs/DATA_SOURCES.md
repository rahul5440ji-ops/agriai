# Data Sources

All external data must come from real, legally usable, public or official
sources. Synthetic data is permitted ONLY for development/testing and must be
clearly labelled.

## Required datasets

### 1. Crop production / yield
- Source: data.gov.in (Ministry of Agriculture & Farmers Welfare)
- Fields: state, district, crop, season, year, area, production, yield
- Use: training Model A (yield prediction)
- Provenance: source, record ID, retrieval timestamp, observation date,
  geographic level, unit, crop, validation status

### 2. MSP notifications
- Source: Department of Agriculture & Farmers Welfare official notifications
- Fields: crop, marketing season, year, MSP ₹/quintal
- Use: MSP reference display (never a guaranteed price)
- Provenance: source, year, marketing season, verified_at

### 3. Mandi prices
- Source: Agmarknet (or another authorized/legal market-data provider)
- Fields: date, state, district, market, commodity, variety, grade,
  min/max/modal price, arrivals, unit
- Use: Model B training, market comparison, recommendations
- Provenance: source, market, date, unit, retrieved_at

### 4. Weather
- Source: reliable weather API with appropriate terms
- Fields: temperature, rainfall (historical + forecast)
- Use: features where valid; optional
- Provenance: source, retrieval timestamp, observation date

### 5. Soil
- Primary: farmer-entered soil-test values
- Fallback: public/government soil data where permitted
- Use: Model A features, advisory

## Provenance contract

Every external record must retain:
- source
- source record ID
- retrieval timestamp
- date of observation
- geographic level
- unit
- crop
- validation status

Never silently turn unknown or stale data into "live" data.
Never fabricate current market prices.
Never fabricate MSP values.
Never invent dataset rows to make ML metrics look good.

## Unit conventions

Be especially careful with: kilogram, quintal, tonne, hectare, acre.
Never mix units silently. Normalize at ingestion time.