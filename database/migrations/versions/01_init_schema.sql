CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    phone_email VARCHAR(255),
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_phone (phone_email)
);

CREATE TABLE IF NOT EXISTS farms (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    state VARCHAR(64) NOT NULL,
    district VARCHAR(64) NOT NULL,
    village VARCHAR(128),
    area_hectare FLOAT NOT NULL,
    soil_type VARCHAR(64),
    irrigation_type VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_farms_user (user_id),
    INDEX idx_farms_location (state, district)
);

CREATE TABLE IF NOT EXISTS crops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    season VARCHAR(32),
    unit VARCHAR(16) DEFAULT 'tonne'
);

CREATE TABLE IF NOT EXISTS soil_tests (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL,
    ph FLOAT CHECK (ph BETWEEN 0 AND 14),
    nitrogen FLOAT,
    phosphorus FLOAT,
    potassium FLOAT,
    organic_carbon FLOAT CHECK (organic_carbon >= 0),
    test_date DATE,
    source VARCHAR(128),
    FOREIGN KEY (farm_id) REFERENCES farms(id),
    INDEX idx_soiltests_farm (farm_id)
);

CREATE TABLE IF NOT EXISTS farm_cycles (
    id SERIAL PRIMARY KEY,
    farm_id INTEGER NOT NULL,
    crop_id INTEGER NOT NULL,
    sowing_date DATE,
    expected_harvest_date DATE,
    season VARCHAR(32),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_id) REFERENCES farms(id),
    FOREIGN KEY (crop_id) REFERENCES crops(id),
    INDEX idx_cycles_farm (farm_id)
);

CREATE TABLE IF NOT EXISTS yield_predictions (
    id SERIAL PRIMARY KEY,
    farm_cycle_id INTEGER NOT NULL,
    predicted_yield_tph FLOAT NOT NULL,
    lower_bound_tph FLOAT,
    upper_bound_tph FLOAT,
    total_production_t FLOAT,
    model_version VARCHAR(64),
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_cycle_id) REFERENCES farm_cycles(id),
    INDEX idx_yield_farm_cycle (farm_cycle_id)
);

CREATE TABLE IF NOT EXISTS msp_prices (
    id SERIAL PRIMARY KEY,
    crop_id INTEGER NOT NULL,
    marketing_season VARCHAR(32) NOT NULL,
    year INTEGER NOT NULL,
    msp_rs_per_quintal FLOAT CHECK (msp_rs_per_quintal >= 0),
    source VARCHAR(255),
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crop_id) REFERENCES crops(id),
    UNIQUE crop_id_marketing_season_year (crop_id, marketing_season, year)
);

CREATE TABLE IF NOT EXISTS market_prices (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    state VARCHAR(64) NOT NULL,
    district VARCHAR(64) NOT NULL,
    market VARCHAR(128) NOT NULL,
    commodity VARCHAR(128) NOT NULL,
    variety VARCHAR(128),
    grade VARCHAR(64),
    min_price FLOAT,
    max_price FLOAT,
    modal_price FLOAT,
    arrivals FLOAT,
    unit VARCHAR(16),  -- kg, quintal, tonne
    source VARCHAR(128),
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_market_prices_lookup (state, district, commodity, date),
    UNIQUE source_market_commodity_date_variety_grade (source, market, commodity, date, variety, grade)
);

CREATE TABLE IF NOT EXISTS market_recommendations (
    id SERIAL PRIMARY KEY,
    farm_cycle_id INTEGER NOT NULL,
    market_price_id INTEGER NOT NULL,
    estimated_transport_cost FLOAT,
    estimated_net_price FLOAT,
    rank INTEGER,
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_cycle_id) REFERENCES farm_cycles(id),
    FOREIGN KEY (market_price_id) REFERENCES market_prices(id),
    INDEX idx_market_rec_farm_cycle (farm_cycle_id),
    INDEX idx_market_rec_rank (rank)
);

CREATE TABLE IF NOT EXISTS model_registry (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(64) NOT NULL,
    version VARCHAR(64) NOT NULL,
    artifact_path VARCHAR(512),
    metrics_json TEXT,
    trained_at TIMESTAMP WITH TIME ZONE,
    dataset_version VARCHAR(64),
    UNIQUE model_name_version (model_name, version)
);

INSERT INTO crops (name, season, unit) VALUES
    ('wheat', 'rabi', 'quintal'),
    ('rice', 'kharif', 'quintal'),
    ('maize', 'kharif', 'quintal'),
    ('sugarcane', 'kharif', 'tonne'),
    ('cotton', 'kharif', 'quintal'),
    ('pulses', 'rabi', 'quintal'),
    ('groundnut', 'kharif', 'quintal'),
    ('mustard', 'rabi', 'quintal'),
    ('potato', 'rabi', 'quintal'),
    ('tomato', 'kharif', 'quintal')
ON CONFLICT (name) DO NOTHING;